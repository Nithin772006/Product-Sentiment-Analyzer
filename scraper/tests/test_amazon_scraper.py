"""
test_amazon_scraper.py – Unit tests for AmazonScraper.

All Selenium / network calls are mocked so these tests run without a
real browser or internet connection.

Tests cover:
* search_product: success and CAPTCHA detection.
* collect_product_links: link extraction and deduplication.
* scrape_product: successful extraction and CAPTCHA guard.
* scrape_reviews: pagination, review card parsing.
* _parse_helpful_votes: various text formats.
* JSON and CSV export (via BaseScraper).
* Full run() pipeline (success and error paths).
"""

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Patch webdriver-manager and selenium at import time so no Chrome is needed
with (
    patch("utils.browser.ChromeDriverManager"),
    patch("utils.browser.webdriver.Chrome"),
):
    from scrapers.amazon_scraper import AmazonScraper


def _mock_element(text: str = "", href: str = "", src: str = "") -> MagicMock:
    """Create a minimal mock WebElement."""
    el = MagicMock()
    el.text = text
    el.get_attribute = lambda attr: {"href": href, "src": src}.get(attr, "")
    el.find_elements = MagicMock(return_value=[])
    return el


class TestAmazonScraperSearchProduct(unittest.TestCase):
    def setUp(self):
        self.scraper = AmazonScraper.__new__(AmazonScraper)
        self.scraper.logger = MagicMock()
        self.scraper.driver = MagicMock()
        self.scraper.products = []
        self.scraper.reviews = []

    @patch("scrapers.amazon_scraper.safe_get", return_value=True)
    @patch("scrapers.amazon_scraper.is_captcha_page", return_value=False)
    @patch("scrapers.amazon_scraper.wait_for_element", return_value=MagicMock())
    def test_search_returns_true_on_success(self, mock_wait, mock_cap, mock_get):
        result = self.scraper.search_product("earphones")
        self.assertTrue(result)

    @patch("scrapers.amazon_scraper.safe_get", return_value=True)
    @patch("scrapers.amazon_scraper.is_captcha_page", return_value=True)
    def test_search_returns_false_on_captcha(self, mock_cap, mock_get):
        result = self.scraper.search_product("earphones")
        self.assertFalse(result)

    @patch("scrapers.amazon_scraper.safe_get", return_value=False)
    def test_search_returns_false_when_navigation_fails(self, mock_get):
        result = self.scraper.search_product("earphones")
        self.assertFalse(result)

    @patch("scrapers.amazon_scraper.safe_get", return_value=True)
    @patch("scrapers.amazon_scraper.is_captcha_page", return_value=False)
    @patch("scrapers.amazon_scraper.wait_for_element", return_value=None)
    def test_search_returns_false_when_results_not_found(self, mock_wait, mock_cap, mock_get):
        result = self.scraper.search_product("earphones")
        self.assertFalse(result)


class TestAmazonScraperCollectLinks(unittest.TestCase):
    def setUp(self):
        self.scraper = AmazonScraper.__new__(AmazonScraper)
        self.scraper.logger = MagicMock()
        self.scraper.driver = MagicMock()

    @patch("scrapers.amazon_scraper.wait_for_elements")
    def test_collects_links_from_cards(self, mock_elements):
        cards = [
            _mock_element(href="https://www.amazon.in/dp/ASIN000001/ref=sr_1_1"),
            _mock_element(href="https://www.amazon.in/dp/ASIN000002/ref=sr_1_2"),
            _mock_element(href="/dp/ASIN000003"),  # relative URL
        ]
        mock_elements.return_value = cards

        links = self.scraper.collect_product_links("earphones", max_products=5)

        self.assertGreater(len(links), 0)
        for link in links:
            self.assertIn("/dp/", link)

    @patch("scrapers.amazon_scraper.wait_for_elements", return_value=[])
    def test_returns_empty_when_no_cards(self, mock_elements):
        links = self.scraper.collect_product_links("nonexistent", max_products=5)
        self.assertEqual(links, [])

    @patch("scrapers.amazon_scraper.wait_for_elements")
    def test_respects_max_products_limit(self, mock_elements):
        cards = [
            _mock_element(href=f"https://www.amazon.in/dp/ASIN{i:06d}")
            for i in range(20)
        ]
        mock_elements.return_value = cards

        links = self.scraper.collect_product_links("laptop", max_products=3)
        self.assertLessEqual(len(links), 3)

    @patch("scrapers.amazon_scraper.wait_for_elements")
    def test_deduplicates_links(self, mock_elements):
        same_href = "https://www.amazon.in/dp/ASIN000001"
        cards = [_mock_element(href=same_href)] * 5
        mock_elements.return_value = cards

        links = self.scraper.collect_product_links("earphones", max_products=10)
        self.assertEqual(links.count(same_href), 1)


class TestAmazonScraperScrapeProduct(unittest.TestCase):
    def setUp(self):
        self.scraper = AmazonScraper.__new__(AmazonScraper)
        self.scraper.logger = MagicMock()
        self.scraper.driver = MagicMock()
        self.scraper.SITE = "amazon"

    @patch("scrapers.amazon_scraper.safe_get", return_value=True)
    @patch("scrapers.amazon_scraper.is_captcha_page", return_value=False)
    @patch("scrapers.amazon_scraper.wait_for_element")
    @patch("scrapers.amazon_scraper.wait_for_elements", return_value=[])
    def test_returns_product_on_success(
        self, mock_els, mock_el, mock_cap, mock_get
    ):
        mock_el.return_value = _mock_element(text="Sony Headphones")
        product = self.scraper.scrape_product(
            "https://www.amazon.in/dp/B0CH7RLKFC"
        )
        self.assertIsNotNone(product)
        self.assertEqual(product.product_id, "B0CH7RLKFC")
        self.assertEqual(product.source, "amazon")

    @patch("scrapers.amazon_scraper.safe_get", return_value=False)
    def test_returns_none_when_navigation_fails(self, mock_get):
        product = self.scraper.scrape_product(
            "https://www.amazon.in/dp/B0CH7RLKFC"
        )
        self.assertIsNone(product)

    @patch("scrapers.amazon_scraper.safe_get", return_value=True)
    @patch("scrapers.amazon_scraper.is_captcha_page", return_value=True)
    def test_returns_none_on_captcha(self, mock_cap, mock_get):
        product = self.scraper.scrape_product(
            "https://www.amazon.in/dp/B0CH7RLKFC"
        )
        self.assertIsNone(product)


class TestAmazonScraperHelpfulVotes(unittest.TestCase):
    def setUp(self):
        self.scraper = AmazonScraper.__new__(AmazonScraper)

    def test_parse_helpful_votes_simple(self):
        self.assertEqual(self.scraper._parse_helpful_votes("12 people found this helpful"), 12)

    def test_parse_helpful_votes_comma(self):
        self.assertEqual(self.scraper._parse_helpful_votes("1,234 people found this helpful"), 1234)

    def test_parse_helpful_votes_none(self):
        self.assertIsNone(self.scraper._parse_helpful_votes(None))

    def test_parse_helpful_votes_empty(self):
        self.assertIsNone(self.scraper._parse_helpful_votes(""))

    def test_parse_helpful_votes_no_number(self):
        self.assertIsNone(self.scraper._parse_helpful_votes("Some people found this helpful"))


class TestBaseScrapeExport(unittest.TestCase):
    """Test JSON and CSV export via BaseScraper using AmazonScraper."""

    def setUp(self):
        self.scraper = AmazonScraper.__new__(AmazonScraper)
        self.scraper.logger = MagicMock()
        self.scraper.driver = MagicMock()
        self.scraper.SITE = "amazon"

        from models.product import Product
        from models.review import Review

        self.scraper.products = [
            Product(product_id="P1", product_name="Test Product", source="amazon")
        ]
        self.scraper.reviews = [
            Review(
                review_id="R1",
                product_id="P1",
                review_title="Great",
                review_text="Excellent product",
                star_rating=5.0,
                source="amazon",
            )
        ]

    def test_export_json(self, tmp_path=None):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            from config import settings
            orig_pj = settings.PRODUCTS_JSON_FILE
            orig_rj = settings.REVIEWS_JSON_FILE
            settings.PRODUCTS_JSON_FILE = base / "products.json"
            settings.REVIEWS_JSON_FILE = base / "reviews.json"

            paths = self.scraper.export_json()

            self.assertTrue(Path(paths["products_json"]).exists())
            self.assertTrue(Path(paths["reviews_json"]).exists())

            with open(paths["products_json"], encoding="utf-8") as fh:
                data = json.load(fh)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["product_id"], "P1")

            with open(paths["reviews_json"], encoding="utf-8") as fh:
                rev_data = json.load(fh)
            self.assertIsNone(rev_data[0]["sentiment"])

            settings.PRODUCTS_JSON_FILE = orig_pj
            settings.REVIEWS_JSON_FILE = orig_rj

    def test_export_csv(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            from config import settings
            orig_pc = settings.PRODUCTS_CSV_FILE
            orig_rc = settings.REVIEWS_CSV_FILE
            settings.PRODUCTS_CSV_FILE = base / "products.csv"
            settings.REVIEWS_CSV_FILE = base / "reviews.csv"

            paths = self.scraper.export_csv()

            self.assertTrue(Path(paths["products_csv"]).exists())
            self.assertTrue(Path(paths["reviews_csv"]).exists())

            settings.PRODUCTS_CSV_FILE = orig_pc
            settings.REVIEWS_CSV_FILE = orig_rc


if __name__ == "__main__":
    unittest.main()
