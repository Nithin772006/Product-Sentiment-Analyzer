"""
base_scraper.py – Abstract base class for all site-specific scrapers.

Defines the full scraping pipeline and all shared behaviour (browser
management, export, logging) so that concrete scrapers only need to
implement the four DOM-specific abstract methods.

Usage::

    # Do not instantiate BaseScraper directly.
    # Use AmazonScraper or FlipkartScraper instead.
    from scrapers.amazon_scraper import AmazonScraper
    scraper = AmazonScraper()
    scraper.run("wireless earphones")
"""

from __future__ import annotations

import csv
import json
import time
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from config import settings
from models.product import Product
from models.review import Review
from utils.browser import create_driver, quit_driver
from utils.cleaner import (
    clean_product,
    clean_review,
    deduplicate_reviews,
    is_empty_review,
)
from utils.helper import is_captcha_page, safe_get
from utils.logger import get_logger


class BaseScraper(ABC):
    """Abstract base class that defines the scraping pipeline.

    Concrete subclasses must implement:
    * :meth:`search_product`
    * :meth:`collect_product_links`
    * :meth:`scrape_product`
    * :meth:`scrape_reviews`

    All other behaviour – browser lifecycle, export, logging, retry
    orchestration – is handled here.
    """

    # Platform identifier – override in subclasses (e.g. 'amazon')
    SITE: str = "base"

    def __init__(self) -> None:
        self.logger = get_logger(f"scraper.{self.SITE}")
        self.driver = None
        self.products: list[Product] = []
        self.reviews: list[Review] = []

    # ------------------------------------------------------------------
    # Browser lifecycle
    # ------------------------------------------------------------------

    def initialize_browser(self) -> None:
        """Start a new Chrome WebDriver instance.

        Called automatically by :meth:`run` before scraping begins.
        Raises a ``RuntimeError`` if the driver cannot be created.
        """
        self.logger.info("Initialising browser for site: %s", self.SITE)
        try:
            self.driver = create_driver()
            self.logger.info("Browser initialised successfully.")
        except Exception as exc:
            self.logger.critical(
                "Failed to initialise browser: %s", exc, exc_info=True
            )
            raise RuntimeError(f"Browser initialisation failed: {exc}") from exc

    def close_browser(self) -> None:
        """Quit the WebDriver and release all resources."""
        quit_driver(self.driver)
        self.driver = None

    # ------------------------------------------------------------------
    # Abstract methods – implement in each site-specific scraper
    # ------------------------------------------------------------------

    @abstractmethod
    def search_product(self, keyword: str) -> bool:
        """Navigate to the site's search results for *keyword*.

        Args:
            keyword: Product search term entered by the user.

        Returns:
            ``True`` if the search results page loaded successfully.
        """

    @abstractmethod
    def collect_product_links(
        self, keyword: str, max_products: int
    ) -> list[str]:
        """Collect product page URLs from search results.

        Must handle pagination up to ``settings.MAX_SEARCH_PAGES`` pages.

        Args:
            keyword:      Product search term.
            max_products: Maximum number of product links to return.

        Returns:
            List of absolute product page URLs.
        """

    @abstractmethod
    def scrape_product(self, url: str) -> Product | None:
        """Scrape a single product page.

        Args:
            url: Product page URL.

        Returns:
            :class:`~models.product.Product` instance or ``None`` on
            failure.
        """

    @abstractmethod
    def scrape_reviews(
        self, url: str, product_id: str
    ) -> list[Review]:
        """Scrape all accessible reviews for a product.

        Must handle pagination and 'load more' patterns.

        Args:
            url:        Product page URL (used to derive the reviews URL).
            product_id: Parent product identifier.

        Returns:
            List of :class:`~models.review.Review` instances.
        """

    # ------------------------------------------------------------------
    # Orchestration pipeline
    # ------------------------------------------------------------------

    def run(
        self,
        keyword: str,
        max_products: int | None = None,
        max_reviews: int | None = None,
    ) -> dict[str, Any]:
        """Execute the full scraping pipeline for *keyword*.

        Steps:
        1. Initialise browser.
        2. Search for the keyword.
        3. Collect product links.
        4. For each product: scrape product info + reviews.
        5. Clean, deduplicate, export data.
        6. Close browser.

        Args:
            keyword:      Product search term.
            max_products: Override for ``settings.MAX_PRODUCTS``.
            max_reviews:  Override for ``settings.MAX_REVIEWS``.

        Returns:
            Summary dict with counts and output file paths.
        """
        _max_products = max_products or settings.MAX_PRODUCTS
        _max_reviews = max_reviews or settings.MAX_REVIEWS

        self.logger.info(
            "=" * 60
            + f"\nScraper started | site={self.SITE} | keyword='{keyword}'"
            + f"\nmax_products={_max_products} | max_reviews={_max_reviews}\n"
            + "=" * 60
        )

        start_time = time.time()
        self.products = []
        self.reviews = []

        try:
            self.initialize_browser()

            # Step 1 – Search
            if not self.search_product(keyword):
                self.logger.error("Search failed for keyword: '%s'", keyword)
                return self._build_summary(start_time, error="Search failed")

            # Step 2 – Collect links
            product_links = self.collect_product_links(keyword, _max_products)
            self.logger.info(
                "Found %d product link(s) for '%s'", len(product_links), keyword
            )

            if not product_links:
                self.logger.warning(
                    "No product links found. Verify selectors or keyword."
                )
                return self._build_summary(start_time, error="No products found")

            # Step 3 – Scrape each product
            for idx, url in enumerate(product_links, start=1):
                self.logger.info(
                    "Scraping product %d/%d: %s", idx, len(product_links), url
                )

                # CAPTCHA guard
                if is_captcha_page(self.driver):
                    self.logger.warning(
                        "CAPTCHA detected on product %d. Skipping …", idx
                    )
                    continue

                product = self._safe_scrape_product(url)
                if product is None:
                    continue

                # Clean and store product
                product_dict = clean_product(product.to_dict())
                self.products.append(Product.from_dict(product_dict))
                self.logger.info("Product scraped: %s", product.product_name)

                # Scrape reviews
                raw_reviews = self._safe_scrape_reviews(
                    url, product.product_id, _max_reviews
                )
                self.logger.info(
                    "Extracted %d review(s) for product %s",
                    len(raw_reviews),
                    product.product_id,
                )
                self.reviews.extend(raw_reviews)

            # Step 4 – Deduplicate reviews
            before = len(self.reviews)
            self.reviews = deduplicate_reviews(
                [r.to_dict() for r in self.reviews]
            )
            # Convert back to Review objects
            self.reviews = [Review.from_dict(r) for r in self.reviews]
            removed = before - len(self.reviews)
            if removed:
                self.logger.info("Removed %d duplicate review(s).", removed)

            # Step 5 – Export
            paths: dict[str, str] = {}
            if settings.EXPORT_JSON:
                paths.update(self.export_json())
            if settings.EXPORT_CSV:
                paths.update(self.export_csv())

        except Exception as exc:  # pylint: disable=broad-except
            self.logger.critical(
                "Unhandled error in scraper pipeline: %s", exc, exc_info=True
            )
            return self._build_summary(start_time, error=str(exc))

        finally:
            self.close_browser()

        summary = self._build_summary(start_time, output_paths=paths)
        self.logger.info(
            "Scraper completed | products=%d | reviews=%d | elapsed=%.1fs",
            summary["products_scraped"],
            summary["reviews_scraped"],
            summary["elapsed_seconds"],
        )
        return summary

    # ------------------------------------------------------------------
    # Safe wrappers with individual error isolation
    # ------------------------------------------------------------------

    def _safe_scrape_product(self, url: str) -> Product | None:
        """Scrape a product, logging and swallowing exceptions.

        Ensures one failed product doesn't abort the entire run.
        """
        try:
            return self.scrape_product(url)
        except Exception as exc:  # pylint: disable=broad-except
            self.logger.error(
                "Failed to scrape product at %s: %s", url, exc, exc_info=True
            )
            return None

    def _safe_scrape_reviews(
        self,
        url: str,
        product_id: str,
        max_reviews: int,
    ) -> list[Review]:
        """Scrape reviews, logging and swallowing exceptions."""
        try:
            raw = self.scrape_reviews(url, product_id)
            # Apply cleaning pipeline and enforce max_reviews limit
            cleaned: list[Review] = []
            for r in raw:
                r_dict = clean_review(r.to_dict())
                if not is_empty_review(r_dict):
                    cleaned.append(Review.from_dict(r_dict))
                if len(cleaned) >= max_reviews:
                    break
            return cleaned
        except Exception as exc:  # pylint: disable=broad-except
            self.logger.error(
                "Failed to scrape reviews for product %s: %s",
                product_id,
                exc,
                exc_info=True,
            )
            return []

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def export_json(self) -> dict[str, str]:
        """Write products and reviews to JSON files.

        Returns:
            Dict mapping ``'products_json'`` and ``'reviews_json'`` to
            their absolute file paths.
        """
        product_dicts = [p.to_dict() for p in self.products]
        review_dicts = [r.to_dict() for r in self.reviews]

        products_path = settings.PRODUCTS_JSON_FILE
        reviews_path = settings.REVIEWS_JSON_FILE

        self._write_json(products_path, product_dicts)
        self._write_json(reviews_path, review_dicts)

        self.logger.info(
            "JSON export complete | products=%s | reviews=%s",
            products_path,
            reviews_path,
        )
        return {
            "products_json": str(products_path),
            "reviews_json": str(reviews_path),
        }

    def export_csv(self) -> dict[str, str]:
        """Write products and reviews to CSV files.

        Returns:
            Dict mapping ``'products_csv'`` and ``'reviews_csv'`` to
            their absolute file paths.
        """
        product_dicts = [p.to_dict() for p in self.products]
        review_dicts = [r.to_dict() for r in self.reviews]

        products_path = settings.PRODUCTS_CSV_FILE
        reviews_path = settings.REVIEWS_CSV_FILE

        self._write_csv(products_path, product_dicts)
        self._write_csv(reviews_path, review_dicts)

        self.logger.info(
            "CSV export complete | products=%s | reviews=%s",
            products_path,
            reviews_path,
        )
        return {
            "products_csv": str(products_path),
            "reviews_csv": str(reviews_path),
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _write_json(path: Path, data: list[dict[str, Any]]) -> None:
        """Serialise *data* to a JSON file at *path*."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2, default=str)

    @staticmethod
    def _write_csv(path: Path, data: list[dict[str, Any]]) -> None:
        """Serialise *data* to a CSV file at *path* using pandas."""
        path.parent.mkdir(parents=True, exist_ok=True)
        if not data:
            pd.DataFrame().to_csv(path, index=False)
            return
        df = pd.DataFrame(data)
        df.to_csv(path, index=False, encoding="utf-8-sig")

    def _build_summary(
        self,
        start_time: float,
        output_paths: dict[str, str] | None = None,
        error: str | None = None,
    ) -> dict[str, Any]:
        """Build and return a run-summary dictionary."""
        return {
            "site": self.SITE,
            "products_scraped": len(self.products),
            "reviews_scraped": len(self.reviews),
            "elapsed_seconds": round(time.time() - start_time, 2),
            "output_files": output_paths or {},
            "error": error,
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }
