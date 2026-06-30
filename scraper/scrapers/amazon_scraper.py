"""
amazon_scraper.py – Amazon.in concrete scraper implementation.

Inherits from :class:`~scrapers.base_scraper.BaseScraper` and implements
all four abstract methods using Amazon.in's current DOM structure.

Usage::

    from scrapers.amazon_scraper import AmazonScraper
    scraper = AmazonScraper()
    summary = scraper.run("wireless earphones", max_products=5)
"""

from __future__ import annotations

import re
import time
from typing import Any

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from config import settings
from config.urls import amazon_search_url, AMAZON_BASE_URL
from models.product import Product
from models.review import Review
from scrapers.base_scraper import BaseScraper
from utils.helper import (
    generate_product_id,
    generate_review_id,
    is_captcha_page,
    retry,
    safe_get,
)
from utils.wait_utils import (
    dismiss_popup,
    get_attribute_safe,
    get_text_safe,
    scroll_to_bottom,
    wait_for_clickable,
    wait_for_element,
    wait_for_elements,
)


class AmazonScraper(BaseScraper):
    """Scraper for Amazon.in product listings and reviews.

    Handles:
    * Product search with pagination.
    * Full product detail extraction.
    * All-reviews page scraping with pagination.
    * CAPTCHA detection and graceful skip.
    * Infinite-scroll review loading.
    """

    SITE = "amazon"

    # ------------------------------------------------------------------
    # CSS / XPath selectors  (update here if Amazon changes its layout)
    # ------------------------------------------------------------------

    # Search page
    _SEL_SEARCH_BOX = (By.ID, "twotabsearchtextbox")
    _SEL_SEARCH_BTN = (By.ID, "nav-search-submit-button")
    _SEL_PRODUCT_CARDS = (
        By.CSS_SELECTOR,
        "div[data-component-type='s-search-result'] h2 a.a-link-normal",
    )
    _SEL_NEXT_PAGE = (By.CSS_SELECTOR, "a.s-pagination-next")

    # Product page
    _SEL_PRODUCT_TITLE = (By.ID, "productTitle")
    _SEL_BRAND = (By.CSS_SELECTOR, "#bylineInfo, #brand")
    _SEL_PRICE_WHOLE = (By.CSS_SELECTOR, "span.a-price-whole")
    _SEL_PRICE_SYMBOL = (By.CSS_SELECTOR, "span.a-price-symbol")
    _SEL_DISCOUNT = (By.CSS_SELECTOR, "span.a-price.a-text-price span.a-offscreen")
    _SEL_RATING = (By.CSS_SELECTOR, "span[data-hook='rating-out-of-text'], #acrPopover span.a-icon-alt")
    _SEL_NUM_RATINGS = (By.ID, "acrCustomerReviewText")
    _SEL_AVAILABILITY = (By.CSS_SELECTOR, "#availability span")
    _SEL_DESCRIPTION = (By.ID, "productDescription")
    _SEL_FEATURE_BULLETS = (By.CSS_SELECTOR, "#feature-bullets ul li span.a-list-item")
    _SEL_IMAGE = (By.CSS_SELECTOR, "#imgTagWrapperId img, #landingImage")
    _SEL_BREADCRUMB = (By.CSS_SELECTOR, "#wayfinding-breadcrumbs_feature_div ul li a")

    # Reviews page
    _SEL_SEE_ALL_REVIEWS = (By.CSS_SELECTOR, "a[data-hook='see-all-reviews-link-foot'], a[data-hook='see-all-reviews-link-head']")
    _SEL_REVIEW_CARDS = (By.CSS_SELECTOR, "div[data-hook='review']")
    _SEL_REVIEW_TITLE = (By.CSS_SELECTOR, "a[data-hook='review-title'] span:last-child")
    _SEL_REVIEW_BODY = (By.CSS_SELECTOR, "span[data-hook='review-body'] span")
    _SEL_REVIEW_RATING = (By.CSS_SELECTOR, "i[data-hook='review-star-rating'] span.a-icon-alt, i[data-hook='cmps-review-star-rating'] span.a-icon-alt")
    _SEL_REVIEWER_NAME = (By.CSS_SELECTOR, "span.a-profile-name")
    _SEL_VERIFIED = (By.CSS_SELECTOR, "span[data-hook='avp-badge']")
    _SEL_REVIEW_DATE = (By.CSS_SELECTOR, "span[data-hook='review-date']")
    _SEL_HELPFUL_VOTES = (By.CSS_SELECTOR, "span[data-hook='helpful-vote-statement']")
    _SEL_NEXT_REVIEW_PAGE = (By.CSS_SELECTOR, "li.a-last a")

    # ------------------------------------------------------------------
    # Abstract method implementations
    # ------------------------------------------------------------------

    def search_product(self, keyword: str) -> bool:
        """Navigate to Amazon.in and perform a search for *keyword*.

        Args:
            keyword: Search term.

        Returns:
            ``True`` if search results loaded, ``False`` on failure.
        """
        self.logger.info("Searching Amazon.in for: '%s'", keyword)

        search_url = amazon_search_url(keyword)
        if not safe_get(self.driver, search_url, timeout=settings.PAGE_TIMEOUT):
            return False

        if is_captcha_page(self.driver):
            self.logger.warning("CAPTCHA detected on Amazon search page.")
            return False

        # Verify results loaded
        result = wait_for_element(
            self.driver,
            (By.CSS_SELECTOR, "div.s-main-slot"),
            timeout=settings.PAGE_TIMEOUT,
        )
        if result is None:
            self.logger.error("Search results container not found.")
            return False

        self.logger.info("Amazon search results loaded for: '%s'", keyword)
        return True

    def collect_product_links(
        self, keyword: str, max_products: int
    ) -> list[str]:
        """Collect product URLs from Amazon search result pages.

        Args:
            keyword:      Search term (used only for logging).
            max_products: Maximum number of links to return.

        Returns:
            List of absolute product page URLs.
        """
        links: list[str] = []
        page = 1

        while len(links) < max_products and page <= settings.MAX_SEARCH_PAGES:
            self.logger.debug(
                "Collecting links from search page %d …", page
            )

            if page > 1:
                next_url = amazon_search_url(keyword, page)
                if not safe_get(self.driver, next_url):
                    break

            cards = wait_for_elements(
                self.driver,
                self._SEL_PRODUCT_CARDS,
                timeout=settings.PAGE_TIMEOUT,
            )

            for card in cards:
                href = get_attribute_safe(card, "href")
                if href and "/dp/" in href:
                    full_url = (
                        href
                        if href.startswith("http")
                        else AMAZON_BASE_URL + href
                    )
                    # Remove query params beyond the ASIN for clean URLs
                    clean = re.sub(r"/ref=.*", "", full_url)
                    if clean not in links:
                        links.append(clean)
                        self.logger.debug("Found product: %s", clean)
                if len(links) >= max_products:
                    break

            page += 1

        self.logger.info(
            "Collected %d product link(s) from Amazon.", len(links)
        )
        return links[:max_products]

    @retry(max_attempts=settings.RETRY_ATTEMPTS, delay=settings.RETRY_DELAY)
    def scrape_product(self, url: str) -> Product | None:
        """Scrape all product details from an Amazon product page.

        Args:
            url: Product page URL.

        Returns:
            :class:`~models.product.Product` instance or ``None``.
        """
        if not safe_get(self.driver, url):
            return None

        if is_captcha_page(self.driver):
            self.logger.warning("CAPTCHA on product page: %s", url)
            return None

        product_id = generate_product_id(url)

        # Title
        title_el = wait_for_element(self.driver, self._SEL_PRODUCT_TITLE)
        product_name = get_text_safe(title_el, "Unknown Product")

        # Brand
        brand_el = wait_for_element(self.driver, self._SEL_BRAND, timeout=5)
        brand = get_text_safe(brand_el)
        if brand.startswith("Visit the "):
            brand = brand.replace("Visit the ", "").replace(" Store", "")
        if brand.startswith("Brand: "):
            brand = brand.replace("Brand: ", "")

        # Price
        price_el = wait_for_element(self.driver, self._SEL_PRICE_WHOLE, timeout=5)
        price_str = get_text_safe(price_el)
        # Also try full price text
        if not price_str:
            symbol_el = wait_for_element(self.driver, self._SEL_PRICE_SYMBOL, timeout=3)
            price_str = get_text_safe(symbol_el)

        # Discount (original price before discount)
        discount_el = wait_for_element(self.driver, self._SEL_DISCOUNT, timeout=5)
        discount_str = get_attribute_safe(discount_el, "innerHTML") if discount_el else ""

        # Rating
        rating_el = wait_for_element(self.driver, self._SEL_RATING, timeout=5)
        rating_str = get_text_safe(rating_el)

        # Number of ratings
        num_ratings_el = wait_for_element(
            self.driver, self._SEL_NUM_RATINGS, timeout=5
        )
        num_ratings_str = get_text_safe(num_ratings_el)

        # Availability
        avail_el = wait_for_element(
            self.driver, self._SEL_AVAILABILITY, timeout=5
        )
        availability = get_text_safe(avail_el, "Unknown")

        # Description (merge bullet points + description section)
        description_parts: list[str] = []
        bullets = wait_for_elements(
            self.driver, self._SEL_FEATURE_BULLETS, timeout=5
        )
        for b in bullets:
            text = get_text_safe(b)
            if text:
                description_parts.append(text)

        desc_el = wait_for_element(
            self.driver, self._SEL_DESCRIPTION, timeout=5
        )
        if desc_el:
            description_parts.append(get_text_safe(desc_el))

        description = " | ".join(filter(None, description_parts))

        # Image URL
        img_el = wait_for_element(self.driver, self._SEL_IMAGE, timeout=5)
        image_url = get_attribute_safe(img_el, "src")

        # Category (from breadcrumbs)
        breadcrumbs = wait_for_elements(
            self.driver, self._SEL_BREADCRUMB, timeout=5
        )
        category = " > ".join(
            get_text_safe(b) for b in breadcrumbs if get_text_safe(b)
        )

        product = Product(
            product_id=product_id,
            product_name=product_name,
            brand=brand or None,
            category=category or None,
            price=price_str or None,           # cleaned by BaseScraper pipeline
            discount_price=discount_str or None,
            overall_rating=rating_str or None,
            num_ratings=num_ratings_str or None,
            num_reviews=None,                  # filled after review scraping
            description=description or None,
            availability=availability,
            image_url=image_url or None,
            product_url=url,
            source=self.SITE,
        )

        self.logger.info(
            "Product found: '%s' (ID: %s)", product_name, product_id
        )
        return product

    @retry(max_attempts=settings.RETRY_ATTEMPTS, delay=settings.RETRY_DELAY)
    def scrape_reviews(
        self, url: str, product_id: str
    ) -> list[Review]:
        """Scrape all reviews for an Amazon product.

        Navigates to the 'all reviews' page and paginates through up to
        ``settings.MAX_REVIEW_PAGES`` pages.

        Args:
            url:        Product page URL.
            product_id: Parent product identifier.

        Returns:
            List of :class:`~models.review.Review` instances.
        """
        reviews: list[Review] = []

        # Try to navigate to 'See all reviews' page
        if not safe_get(self.driver, url):
            return reviews

        see_all_el = wait_for_element(
            self.driver, self._SEL_SEE_ALL_REVIEWS, timeout=8
        )
        if see_all_el:
            reviews_url = get_attribute_safe(see_all_el, "href")
            if reviews_url and not reviews_url.startswith("http"):
                reviews_url = AMAZON_BASE_URL + reviews_url
            if reviews_url:
                safe_get(self.driver, reviews_url)
        else:
            # Stay on the product page and scroll to the reviews section
            scroll_to_bottom(self.driver)

        for page_num in range(1, settings.MAX_REVIEW_PAGES + 1):
            self.logger.debug(
                "Scraping Amazon reviews page %d for product %s",
                page_num,
                product_id,
            )

            if is_captcha_page(self.driver):
                self.logger.warning(
                    "CAPTCHA on Amazon reviews page %d. Stopping.", page_num
                )
                break

            review_cards = wait_for_elements(
                self.driver,
                self._SEL_REVIEW_CARDS,
                timeout=settings.PAGE_TIMEOUT,
            )

            if not review_cards:
                self.logger.debug(
                    "No review cards found on page %d.", page_num
                )
                break

            for card in review_cards:
                review = self._parse_review_card(card, product_id)
                if review:
                    reviews.append(review)

            self.logger.info(
                "Reviews collected so far: %d (page %d)",
                len(reviews),
                page_num,
            )

            # Navigate to next page
            next_btn = wait_for_clickable(
                self.driver, self._SEL_NEXT_REVIEW_PAGE, timeout=5
            )
            if next_btn is None:
                self.logger.debug(
                    "No next page button found. End of reviews."
                )
                break

            next_url = get_attribute_safe(next_btn, "href")
            if not next_url:
                break
            if not next_url.startswith("http"):
                next_url = AMAZON_BASE_URL + next_url

            safe_get(self.driver, next_url)

        self.logger.info(
            "Total reviews extracted for %s: %d", product_id, len(reviews)
        )
        return reviews

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _parse_review_card(
        self, card: Any, product_id: str
    ) -> Review | None:
        """Extract a single review from a review card element.

        Args:
            card:       Selenium WebElement for the review card.
            product_id: Parent product identifier.

        Returns:
            :class:`~models.review.Review` or ``None`` if parsing fails.
        """
        try:
            title_el = card.find_elements(
                *self._SEL_REVIEW_TITLE
            )
            review_title = get_text_safe(title_el[0] if title_el else None)

            body_el = card.find_elements(*self._SEL_REVIEW_BODY)
            review_text = get_text_safe(body_el[0] if body_el else None)

            rating_el = card.find_elements(*self._SEL_REVIEW_RATING)
            rating_str = get_text_safe(rating_el[0] if rating_el else None)

            name_el = card.find_elements(*self._SEL_REVIEWER_NAME)
            reviewer_name = get_text_safe(name_el[0] if name_el else None)

            verified_el = card.find_elements(*self._SEL_VERIFIED)
            verified_purchase = len(verified_el) > 0

            date_el = card.find_elements(*self._SEL_REVIEW_DATE)
            review_date = get_text_safe(date_el[0] if date_el else None)
            # Amazon date format: "Reviewed in India on 15 March 2024"
            date_match = re.search(r"on (.+)$", review_date or "")
            if date_match:
                review_date = date_match.group(1).strip()

            helpful_el = card.find_elements(*self._SEL_HELPFUL_VOTES)
            helpful_text = get_text_safe(helpful_el[0] if helpful_el else None)
            helpful_votes = self._parse_helpful_votes(helpful_text)

            review_id = generate_review_id(
                product_id,
                reviewer_name or "",
                review_date or "",
                review_text or "",
            )

            return Review(
                review_id=review_id,
                product_id=product_id,
                review_title=review_title or None,
                review_text=review_text or None,
                star_rating=rating_str or None,    # cleaned by pipeline
                reviewer_name=reviewer_name or None,
                verified_purchase=verified_purchase,
                review_date=review_date or None,
                helpful_votes=helpful_votes,
                source=self.SITE,
            )

        except Exception as exc:  # pylint: disable=broad-except
            self.logger.warning(
                "Failed to parse a review card: %s", exc
            )
            return None

    @staticmethod
    def _parse_helpful_votes(text: str | None) -> int | None:
        """Extract the integer vote count from helpful-vote text.

        E.g. '12 people found this helpful' → 12.

        Args:
            text: Raw helpful-vote string.

        Returns:
            Integer count or ``None``.
        """
        if not text:
            return None
        match = re.search(r"(\d[\d,]*)", text)
        if match:
            try:
                return int(match.group(1).replace(",", ""))
            except ValueError:
                return None
        return None
