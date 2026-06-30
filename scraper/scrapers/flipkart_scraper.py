"""
flipkart_scraper.py – Flipkart concrete scraper implementation.

Inherits from :class:`~scrapers.base_scraper.BaseScraper` and implements
all four abstract methods using Flipkart's current DOM structure.

Usage::

    from scrapers.flipkart_scraper import FlipkartScraper
    scraper = FlipkartScraper()
    summary = scraper.run("wireless earphones", max_products=5)
"""

from __future__ import annotations

import re
import time
from typing import Any

from selenium.webdriver.common.by import By

from config import settings
from config.urls import flipkart_search_url, FLIPKART_BASE_URL
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
    safe_click,
    scroll_to_element,
)


class FlipkartScraper(BaseScraper):
    """Scraper for Flipkart product listings and reviews.

    Handles:
    * Login-popup dismissal on first visit.
    * Product search with pagination.
    * Full product detail extraction.
    * Reviews page scraping with pagination.
    * 'READ MORE' expander clicks for truncated reviews.
    * CAPTCHA detection and graceful skip.
    """

    SITE = "flipkart"

    # ------------------------------------------------------------------
    # CSS selectors (update here if Flipkart changes its layout)
    # ------------------------------------------------------------------

    # Login popup
    _SEL_LOGIN_CLOSE = (By.CSS_SELECTOR, "button._2KpZ6l._2doB4z")

    # Search page – Flipkart uses multiple grid layouts; cover both
    _SEL_PRODUCT_LINKS_GRID = (
        By.CSS_SELECTOR,
        "div._1AtVbE div._13oc-S a, div._2kHMtA a, div._4rR01T a, a.s1Q9rs",
    )
    _SEL_NEXT_PAGE = (By.CSS_SELECTOR, "a._1LKTO3[rel='next'], nav a[aria-label='Next']")

    # Product page
    _SEL_PRODUCT_TITLE = (By.CSS_SELECTOR, "span.B_NuCI, h1.yhB1nd span")
    _SEL_BRAND = (By.CSS_SELECTOR, "span.G6XhRU a, div._2rdoCL span")
    _SEL_PRICE = (By.CSS_SELECTOR, "div._30jeq3._16Jk6d, div._16Jk6d")
    _SEL_ORIGINAL_PRICE = (By.CSS_SELECTOR, "div._3I9_wc._2p6lqe, div._3qQ9m1")
    _SEL_RATING = (By.CSS_SELECTOR, "div._3LWZlK")
    _SEL_NUM_RATINGS = (By.CSS_SELECTOR, "span._13vcmD, span._2_R_DZ")
    _SEL_AVAILABILITY = (By.CSS_SELECTOR, "div._16FRp0")
    _SEL_DESCRIPTION = (By.CSS_SELECTOR, "div._1mXcCf._34Y9b8 div._3eNLzu, div.X3BRps")
    _SEL_FEATURE_ROWS = (By.CSS_SELECTOR, "table._14cfVK tr")
    _SEL_IMAGE = (By.CSS_SELECTOR, "img._396cs4._2amPTt._3qGmMb, img._1Nyybr._Z0IfN")
    _SEL_BREADCRUMB = (By.CSS_SELECTOR, "div._3GIHBu a, div.aMaAEs a")

    # Reviews section on product page
    _SEL_ALL_REVIEWS_LINK = (
        By.CSS_SELECTOR,
        "div._3UAT2v a, a._1KDB0._2K8FXD, div._3obHNa a",
    )
    _SEL_REVIEW_CARDS = (
        By.CSS_SELECTOR,
        "div._1AtVbE div._27M-vq, div.col._2wzgFH, div._3AVKGK",
    )
    _SEL_REVIEW_TITLE = (By.CSS_SELECTOR, "p._2-N8zT")
    _SEL_REVIEW_BODY = (By.CSS_SELECTOR, "div.t-ZTKy div div.qwjRop, div._6K-7Co")
    _SEL_READ_MORE = (By.CSS_SELECTOR, "span._2lzDo")
    _SEL_REVIEW_RATING = (By.CSS_SELECTOR, "div._3LWZlK")
    _SEL_REVIEWER_NAME = (By.CSS_SELECTOR, "p._2sc7ZR._2V5EHH")
    _SEL_VERIFIED = (By.CSS_SELECTOR, "p._2mcZGG span._2afOsN._3gFjFr")
    _SEL_REVIEW_DATE = (By.CSS_SELECTOR, "p._2sc7ZR")
    _SEL_HELPFUL_VOTES = (By.CSS_SELECTOR, "span._1_Wj6c")
    _SEL_NEXT_REVIEW_PAGE = (
        By.CSS_SELECTOR,
        "a._1LKTO3[rel='next'], nav a[aria-label='Next']",
    )

    # ------------------------------------------------------------------
    # Abstract method implementations
    # ------------------------------------------------------------------

    def search_product(self, keyword: str) -> bool:
        """Navigate to Flipkart and perform a search for *keyword*.

        Also dismisses the login popup that Flipkart shows on first visit.

        Args:
            keyword: Search term.

        Returns:
            ``True`` if search results loaded, ``False`` on failure.
        """
        self.logger.info("Searching Flipkart for: '%s'", keyword)

        search_url = flipkart_search_url(keyword)
        if not safe_get(self.driver, search_url, timeout=settings.PAGE_TIMEOUT):
            return False

        # Dismiss login popup (appears on ~50% of visits)
        dismissed = dismiss_popup(
            self.driver, self._SEL_LOGIN_CLOSE, timeout=5
        )
        if dismissed:
            self.logger.debug("Flipkart login popup dismissed.")

        if is_captcha_page(self.driver):
            self.logger.warning("CAPTCHA detected on Flipkart search page.")
            return False

        # Verify search results loaded
        result = wait_for_element(
            self.driver,
            (By.CSS_SELECTOR, "div._2B099V, div._1YokD2._3Mn1Gg, section"),
            timeout=settings.PAGE_TIMEOUT,
        )
        if result is None:
            self.logger.error("Flipkart search results container not found.")
            return False

        self.logger.info(
            "Flipkart search results loaded for: '%s'", keyword
        )
        return True

    def collect_product_links(
        self, keyword: str, max_products: int
    ) -> list[str]:
        """Collect product URLs from Flipkart search result pages.

        Args:
            keyword:      Search term.
            max_products: Maximum number of links to return.

        Returns:
            List of absolute product page URLs.
        """
        links: list[str] = []
        page = 1

        while len(links) < max_products and page <= settings.MAX_SEARCH_PAGES:
            self.logger.debug(
                "Collecting Flipkart links from page %d …", page
            )

            if page > 1:
                page_url = flipkart_search_url(keyword, page)
                if not safe_get(self.driver, page_url):
                    break
                dismiss_popup(
                    self.driver, self._SEL_LOGIN_CLOSE, timeout=3
                )

            product_anchors = wait_for_elements(
                self.driver,
                self._SEL_PRODUCT_LINKS_GRID,
                timeout=settings.PAGE_TIMEOUT,
            )

            for anchor in product_anchors:
                href = get_attribute_safe(anchor, "href")
                if not href:
                    continue
                full_url = (
                    href
                    if href.startswith("http")
                    else FLIPKART_BASE_URL + href
                )
                # Deduplicate
                if full_url not in links:
                    links.append(full_url)
                    self.logger.debug("Found product: %s", full_url)
                if len(links) >= max_products:
                    break

            page += 1

        self.logger.info(
            "Collected %d product link(s) from Flipkart.", len(links)
        )
        return links[:max_products]

    @retry(max_attempts=settings.RETRY_ATTEMPTS, delay=settings.RETRY_DELAY)
    def scrape_product(self, url: str) -> Product | None:
        """Scrape all product details from a Flipkart product page.

        Args:
            url: Product page URL.

        Returns:
            :class:`~models.product.Product` instance or ``None``.
        """
        if not safe_get(self.driver, url):
            return None

        dismiss_popup(self.driver, self._SEL_LOGIN_CLOSE, timeout=4)

        if is_captcha_page(self.driver):
            self.logger.warning("CAPTCHA on Flipkart product page: %s", url)
            return None

        product_id = generate_product_id(url)

        # Title
        title_el = wait_for_element(self.driver, self._SEL_PRODUCT_TITLE)
        product_name = get_text_safe(title_el, "Unknown Product")

        # Brand
        brand_el = wait_for_element(self.driver, self._SEL_BRAND, timeout=5)
        brand = get_text_safe(brand_el)

        # Price (current selling price)
        price_el = wait_for_element(self.driver, self._SEL_PRICE, timeout=5)
        price_str = get_text_safe(price_el)

        # Original price (before discount)
        orig_price_el = wait_for_element(
            self.driver, self._SEL_ORIGINAL_PRICE, timeout=5
        )
        discount_str = get_text_safe(orig_price_el)

        # Rating
        rating_el = wait_for_element(self.driver, self._SEL_RATING, timeout=5)
        rating_str = get_text_safe(rating_el)

        # Number of ratings / reviews
        num_ratings_el = wait_for_element(
            self.driver, self._SEL_NUM_RATINGS, timeout=5
        )
        num_ratings_text = get_text_safe(num_ratings_el)
        # Flipkart combines ratings + reviews: "1,234 Ratings & 456 Reviews"
        ratings_count, reviews_count = self._parse_ratings_reviews(
            num_ratings_text
        )

        # Availability
        avail_el = wait_for_element(
            self.driver, self._SEL_AVAILABILITY, timeout=5
        )
        availability = get_text_safe(avail_el, "In Stock")

        # Description from feature rows (spec table)
        spec_parts: list[str] = []
        spec_rows = wait_for_elements(
            self.driver, self._SEL_FEATURE_ROWS, timeout=5
        )
        for row in spec_rows[:10]:  # Cap at 10 rows
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 2:
                key = get_text_safe(cells[0])
                val = get_text_safe(cells[1])
                if key and val:
                    spec_parts.append(f"{key}: {val}")

        # Fallback description block
        desc_el = wait_for_element(
            self.driver, self._SEL_DESCRIPTION, timeout=5
        )
        if desc_el:
            spec_parts.append(get_text_safe(desc_el))

        description = " | ".join(filter(None, spec_parts))

        # Image
        img_el = wait_for_element(self.driver, self._SEL_IMAGE, timeout=5)
        image_url = get_attribute_safe(img_el, "src")

        # Category from breadcrumb
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
            price=price_str or None,
            discount_price=discount_str or None,
            overall_rating=rating_str or None,
            num_ratings=ratings_count,
            num_reviews=reviews_count,
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
        """Scrape all reviews for a Flipkart product.

        Navigates to the 'All Reviews' page and paginates through up to
        ``settings.MAX_REVIEW_PAGES`` pages.

        Args:
            url:        Product page URL.
            product_id: Parent product identifier.

        Returns:
            List of :class:`~models.review.Review` instances.
        """
        reviews: list[Review] = []

        if not safe_get(self.driver, url):
            return reviews

        dismiss_popup(self.driver, self._SEL_LOGIN_CLOSE, timeout=4)

        # Navigate to 'All Reviews' page
        all_reviews_el = wait_for_element(
            self.driver, self._SEL_ALL_REVIEWS_LINK, timeout=8
        )
        if all_reviews_el:
            reviews_href = get_attribute_safe(all_reviews_el, "href")
            if reviews_href:
                if not reviews_href.startswith("http"):
                    reviews_href = FLIPKART_BASE_URL + reviews_href
                safe_get(self.driver, reviews_href)
                dismiss_popup(self.driver, self._SEL_LOGIN_CLOSE, timeout=3)
        else:
            scroll_to_bottom(self.driver)

        for page_num in range(1, settings.MAX_REVIEW_PAGES + 1):
            self.logger.debug(
                "Scraping Flipkart reviews page %d for product %s",
                page_num,
                product_id,
            )

            if is_captcha_page(self.driver):
                self.logger.warning(
                    "CAPTCHA on Flipkart reviews page %d. Stopping.", page_num
                )
                break

            # Click 'READ MORE' buttons to expand truncated reviews
            self._expand_reviews()

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

            # Navigate to next reviews page
            next_btn = wait_for_clickable(
                self.driver, self._SEL_NEXT_REVIEW_PAGE, timeout=5
            )
            if next_btn is None:
                self.logger.debug("No next page button. End of reviews.")
                break

            if not safe_click(self.driver, next_btn):
                break
            # Wait for new cards to load
            time.sleep(settings.SCROLL_PAUSE)
            dismiss_popup(self.driver, self._SEL_LOGIN_CLOSE, timeout=2)

        self.logger.info(
            "Total reviews extracted for %s: %d", product_id, len(reviews)
        )
        return reviews

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _expand_reviews(self) -> None:
        """Click all 'READ MORE' expanders to reveal full review text."""
        read_more_btns = self.driver.find_elements(*self._SEL_READ_MORE)
        for btn in read_more_btns:
            try:
                scroll_to_element(self.driver, btn)
                safe_click(self.driver, btn)
            except Exception:  # pylint: disable=broad-except
                pass

    def _parse_review_card(
        self, card: Any, product_id: str
    ) -> Review | None:
        """Extract a single review from a Flipkart review card element.

        Args:
            card:       Selenium WebElement for the review container.
            product_id: Parent product identifier.

        Returns:
            :class:`~models.review.Review` or ``None`` if parsing fails.
        """
        try:
            title_el = card.find_elements(*self._SEL_REVIEW_TITLE)
            review_title = get_text_safe(title_el[0] if title_el else None)

            body_el = card.find_elements(*self._SEL_REVIEW_BODY)
            review_text = get_text_safe(body_el[0] if body_el else None)

            rating_el = card.find_elements(*self._SEL_REVIEW_RATING)
            rating_str = get_text_safe(rating_el[0] if rating_el else None)

            # Reviewer info – Flipkart combines name + date in one element
            info_els = card.find_elements(*self._SEL_REVIEWER_NAME)
            reviewer_name = ""
            review_date = ""
            if info_els:
                reviewer_name = get_text_safe(info_els[0])
            if len(info_els) > 1:
                review_date = get_text_safe(info_els[1])

            verified_el = card.find_elements(*self._SEL_VERIFIED)
            verified_purchase = any(
                "certified" in get_text_safe(el).lower()
                or "buyer" in get_text_safe(el).lower()
                for el in verified_el
            )

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
                star_rating=rating_str or None,
                reviewer_name=reviewer_name or None,
                verified_purchase=verified_purchase,
                review_date=review_date or None,
                helpful_votes=helpful_votes,
                source=self.SITE,
            )

        except Exception as exc:  # pylint: disable=broad-except
            self.logger.warning(
                "Failed to parse a Flipkart review card: %s", exc
            )
            return None

    @staticmethod
    def _parse_ratings_reviews(
        text: str,
    ) -> tuple[int | None, int | None]:
        """Parse Flipkart's combined ratings + reviews string.

        E.g. '1,234 Ratings & 456 Reviews' → (1234, 456).

        Args:
            text: Raw ratings/reviews string from the page.

        Returns:
            Tuple of (ratings_count, reviews_count).
        """
        if not text:
            return None, None
        nums = re.findall(r"[\d,]+", text)
        ratings = None
        reviews = None
        if len(nums) >= 1:
            try:
                ratings = int(nums[0].replace(",", ""))
            except ValueError:
                pass
        if len(nums) >= 2:
            try:
                reviews = int(nums[1].replace(",", ""))
            except ValueError:
                pass
        return ratings, reviews

    @staticmethod
    def _parse_helpful_votes(text: str | None) -> int | None:
        """Extract the integer vote count from helpful-vote text.

        Args:
            text: Raw string such as '23 found this helpful'.

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
