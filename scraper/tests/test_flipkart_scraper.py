"""
test_flipkart_scraper.py – Unit tests for FlipkartScraper.

All Selenium / network calls are mocked so no real browser is required.

Tests cover:
* search_product: success, popup dismissal, CAPTCHA detection.
* collect_product_links: link extraction, relative URL resolution.
* scrape_product: successful extraction and CAPTCHA guard.
* _parse_ratings_reviews: various Flipkart rating string formats.
* _parse_helpful_votes: various formats.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

with (
    patch("utils.browser.ChromeDriverManager"),
    patch("utils.browser.webdriver.Chrome"),
):
    from scrapers.flipkart_scraper import FlipkartScraper


def _mock_element(text: str = "", href: str = "", src: str = "") -> MagicMock:
    el = MagicMock()
    el.text = text
    el.get_attribute = lambda attr: {"href": href, "src": src}.get(attr, "")
    el.find_elements = MagicMock(return_value=[])
    return el


class TestFlipkartScraperSearchProduct(unittest.TestCase):
    def setUp(self):
        self.scraper = FlipkartScraper.__new__(FlipkartScraper)
        self.scraper.logger = MagicMock()
        self.scraper.driver = MagicMock()
        self.scraper.products = []
        self.scraper.reviews = []

    @patch("scrapers.flipkart_scraper.safe_get", return_value=True)
    @patch("scrapers.flipkart_scraper.dismiss_popup", return_value=True)
    @patch("scrapers.flipkart_scraper.is_captcha_page", return_value=False)
    @patch("scrapers.flipkart_scraper.wait_for_element", return_value=MagicMock())
    def test_search_returns_true_on_success(
        self, mock_wait, mock_cap, mock_dismiss, mock_get
    ):
        result = self.scraper.search_product("laptop")
        self.assertTrue(result)

    @patch("scrapers.flipkart_scraper.safe_get", return_value=True)
    @patch("scrapers.flipkart_scraper.dismiss_popup", return_value=False)
    @patch("scrapers.flipkart_scraper.is_captcha_page", return_value=True)
    def test_search_returns_false_on_captcha(
        self, mock_cap, mock_dismiss, mock_get
    ):
        result = self.scraper.search_product("laptop")
        self.assertFalse(result)

    @patch("scrapers.flipkart_scraper.safe_get", return_value=False)
    def test_search_returns_false_when_navigation_fails(self, mock_get):
        result = self.scraper.search_product("laptop")
        self.assertFalse(result)


class TestFlipkartCollectLinks(unittest.TestCase):
    def setUp(self):
        self.scraper = FlipkartScraper.__new__(FlipkartScraper)
        self.scraper.logger = MagicMock()
        self.scraper.driver = MagicMock()

    @patch("scrapers.flipkart_scraper.wait_for_elements")
    def test_collects_and_resolves_relative_links(self, mock_elements):
        anchors = [
            _mock_element(href="/product/laptop-model-1/p/itm?pid=LAPTOP001"),
            _mock_element(href="/product/laptop-model-2/p/itm?pid=LAPTOP002"),
            _mock_element(href="https://www.flipkart.com/full-url?pid=LAPTOP003"),
        ]
        mock_elements.return_value = anchors

        links = self.scraper.collect_product_links("laptop", max_products=10)
        self.assertEqual(len(links), 3)
        # All links should be absolute
        for link in links:
            self.assertTrue(link.startswith("http"))

    @patch("scrapers.flipkart_scraper.wait_for_elements", return_value=[])
    def test_returns_empty_when_no_links(self, mock_elements):
        links = self.scraper.collect_product_links("noproduct", max_products=5)
        self.assertEqual(links, [])

    @patch("scrapers.flipkart_scraper.wait_for_elements")
    def test_respects_max_products(self, mock_elements):
        anchors = [
            _mock_element(href=f"/p/itm?pid=PROD{i:06d}") for i in range(20)
        ]
        mock_elements.return_value = anchors
        links = self.scraper.collect_product_links("phone", max_products=5)
        self.assertLessEqual(len(links), 5)


class TestFlipkartScrapeProduct(unittest.TestCase):
    def setUp(self):
        self.scraper = FlipkartScraper.__new__(FlipkartScraper)
        self.scraper.logger = MagicMock()
        self.scraper.driver = MagicMock()
        self.scraper.SITE = "flipkart"

    @patch("scrapers.flipkart_scraper.safe_get", return_value=True)
    @patch("scrapers.flipkart_scraper.dismiss_popup", return_value=False)
    @patch("scrapers.flipkart_scraper.is_captcha_page", return_value=False)
    @patch("scrapers.flipkart_scraper.wait_for_element")
    @patch("scrapers.flipkart_scraper.wait_for_elements", return_value=[])
    def test_returns_product_on_success(
        self, mock_els, mock_el, mock_cap, mock_dismiss, mock_get
    ):
        mock_el.return_value = _mock_element(text="Dell Laptop")
        url = "https://www.flipkart.com/dell-laptop/p/itm?pid=DELLPID123"
        product = self.scraper.scrape_product(url)
        self.assertIsNotNone(product)
        self.assertEqual(product.source, "flipkart")

    @patch("scrapers.flipkart_scraper.safe_get", return_value=False)
    def test_returns_none_when_navigation_fails(self, mock_get):
        product = self.scraper.scrape_product(
            "https://www.flipkart.com/product"
        )
        self.assertIsNone(product)

    @patch("scrapers.flipkart_scraper.safe_get", return_value=True)
    @patch("scrapers.flipkart_scraper.dismiss_popup", return_value=False)
    @patch("scrapers.flipkart_scraper.is_captcha_page", return_value=True)
    def test_returns_none_on_captcha(self, mock_cap, mock_dismiss, mock_get):
        product = self.scraper.scrape_product(
            "https://www.flipkart.com/product"
        )
        self.assertIsNone(product)


class TestFlipkartParseRatingsReviews(unittest.TestCase):
    def setUp(self):
        self.scraper = FlipkartScraper.__new__(FlipkartScraper)

    def test_combined_string(self):
        ratings, reviews = self.scraper._parse_ratings_reviews(
            "1,234 Ratings & 456 Reviews"
        )
        self.assertEqual(ratings, 1234)
        self.assertEqual(reviews, 456)

    def test_ratings_only(self):
        ratings, reviews = self.scraper._parse_ratings_reviews("500 Ratings")
        self.assertEqual(ratings, 500)
        self.assertIsNone(reviews)

    def test_empty_string(self):
        ratings, reviews = self.scraper._parse_ratings_reviews("")
        self.assertIsNone(ratings)
        self.assertIsNone(reviews)

    def test_no_numbers(self):
        ratings, reviews = self.scraper._parse_ratings_reviews("No ratings yet")
        self.assertIsNone(ratings)
        self.assertIsNone(reviews)


class TestFlipkartParseHelpfulVotes(unittest.TestCase):
    def setUp(self):
        self.scraper = FlipkartScraper.__new__(FlipkartScraper)

    def test_simple_number(self):
        self.assertEqual(self.scraper._parse_helpful_votes("5 found this helpful"), 5)

    def test_comma_number(self):
        self.assertEqual(self.scraper._parse_helpful_votes("1,000 upvotes"), 1000)

    def test_none_input(self):
        self.assertIsNone(self.scraper._parse_helpful_votes(None))

    def test_empty_string(self):
        self.assertIsNone(self.scraper._parse_helpful_votes(""))


if __name__ == "__main__":
    unittest.main()
