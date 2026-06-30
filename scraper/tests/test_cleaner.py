"""
test_cleaner.py – Unit tests for the data cleaning utilities.

Tests cover:
* HTML tag removal.
* Emoji removal.
* Whitespace normalisation.
* Price parsing.
* Rating parsing.
* Date normalisation.
* Full review and product cleaning pipelines.
* Deduplication.
* Empty review detection.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.cleaner import (
    clean_product,
    clean_review,
    clean_text,
    deduplicate_reviews,
    is_empty_review,
    normalize_date,
    normalize_whitespace,
    parse_price,
    parse_rating,
    remove_emojis,
    remove_html_tags,
)


class TestRemoveHtmlTags(unittest.TestCase):
    def test_strips_simple_tags(self):
        self.assertEqual(remove_html_tags("<b>Bold</b>"), "Bold")

    def test_strips_nested_tags(self):
        self.assertEqual(
            remove_html_tags("<div><p>Hello <em>World</em></p></div>"),
            "Hello World",
        )

    def test_empty_string(self):
        self.assertEqual(remove_html_tags(""), "")

    def test_no_tags(self):
        self.assertEqual(remove_html_tags("Plain text"), "Plain text")


class TestRemoveEmojis(unittest.TestCase):
    def test_removes_emoji(self):
        result = remove_emojis("Great product 😊🎉")
        self.assertNotIn("😊", result)
        self.assertNotIn("🎉", result)
        self.assertIn("Great product", result)

    def test_no_emoji(self):
        self.assertEqual(remove_emojis("No emojis here"), "No emojis here")

    def test_empty_string(self):
        self.assertEqual(remove_emojis(""), "")


class TestNormalizeWhitespace(unittest.TestCase):
    def test_collapses_spaces(self):
        self.assertEqual(normalize_whitespace("a  b   c"), "a b c")

    def test_strips_newlines(self):
        self.assertEqual(normalize_whitespace("hello\nworld"), "hello world")

    def test_strips_tabs(self):
        self.assertEqual(normalize_whitespace("col1\tcol2"), "col1 col2")

    def test_trims_leading_trailing(self):
        self.assertEqual(normalize_whitespace("  hello  "), "hello")


class TestCleanText(unittest.TestCase):
    def test_full_pipeline(self):
        raw = "  <b>Great!</b>  😊  "
        result = clean_text(raw)
        self.assertNotIn("<b>", result)
        self.assertNotIn("😊", result)
        self.assertEqual(result, "Great!")

    def test_none_like_empty(self):
        self.assertEqual(clean_text(""), "")


class TestParsePrice(unittest.TestCase):
    def test_indian_rupee(self):
        self.assertEqual(parse_price("₹1,499.00"), 1499.0)

    def test_comma_formatted(self):
        self.assertEqual(parse_price("26,990"), 26990.0)

    def test_plain_number(self):
        self.assertEqual(parse_price("999"), 999.0)

    def test_empty_string(self):
        self.assertIsNone(parse_price(""))

    def test_no_digits(self):
        self.assertIsNone(parse_price("N/A"))

    def test_with_spaces(self):
        self.assertEqual(parse_price("  ₹ 500  "), 500.0)


class TestParseRating(unittest.TestCase):
    def test_out_of_five(self):
        self.assertEqual(parse_rating("4.2 out of 5"), 4.2)

    def test_integer_rating(self):
        self.assertEqual(parse_rating("5"), 5.0)

    def test_flipkart_style(self):
        self.assertEqual(parse_rating("4.3"), 4.3)

    def test_empty_string(self):
        self.assertIsNone(parse_rating(""))

    def test_no_number(self):
        self.assertIsNone(parse_rating("No Rating"))


class TestNormalizeDate(unittest.TestCase):
    def test_long_format(self):
        self.assertEqual(normalize_date("15 March 2024"), "2024-03-15")

    def test_us_format(self):
        self.assertEqual(normalize_date("March 15, 2024"), "2024-03-15")

    def test_short_month(self):
        self.assertEqual(normalize_date("15 Mar 2024"), "2024-03-15")

    def test_iso_passthrough(self):
        self.assertEqual(normalize_date("2024-03-15"), "2024-03-15")

    def test_empty_string(self):
        self.assertIsNone(normalize_date(""))

    def test_none_string(self):
        self.assertIsNone(normalize_date(""))


class TestCleanReview(unittest.TestCase):
    def test_cleans_text_fields(self):
        raw = {
            "review_id": "R1",
            "product_id": "P1",
            "review_title": "<b>Awesome!</b> 😊",
            "review_text": "  Works great.  ",
            "reviewer_name": "  John Doe  ",
            "star_rating": "4.5 out of 5",
            "review_date": "15 March 2024",
        }
        cleaned = clean_review(raw)
        self.assertEqual(cleaned["review_title"], "Awesome!")
        self.assertEqual(cleaned["review_text"], "Works great.")
        self.assertEqual(cleaned["reviewer_name"], "John Doe")
        self.assertEqual(cleaned["star_rating"], 4.5)
        self.assertEqual(cleaned["review_date"], "2024-03-15")

    def test_does_not_mutate_original(self):
        raw = {"review_title": "<b>Test</b>", "review_text": "Hello 😊"}
        original_title = raw["review_title"]
        clean_review(raw)
        self.assertEqual(raw["review_title"], original_title)


class TestCleanProduct(unittest.TestCase):
    def test_numeric_conversion(self):
        raw = {
            "product_id": "P1",
            "product_name": "Test",
            "price": "₹1,499",
            "overall_rating": "4.2 out of 5",
            "num_ratings": "1,200 ratings",
        }
        cleaned = clean_product(raw)
        self.assertEqual(cleaned["price"], 1499.0)
        self.assertEqual(cleaned["overall_rating"], 4.2)
        self.assertEqual(cleaned["num_ratings"], 1200)

    def test_does_not_mutate_original(self):
        raw = {"product_id": "P1", "product_name": "Test", "price": "₹999"}
        original_price = raw["price"]
        clean_product(raw)
        self.assertEqual(raw["price"], original_price)


class TestDeduplicateReviews(unittest.TestCase):
    def test_removes_duplicates_by_id(self):
        reviews = [
            {"review_id": "R1", "review_text": "Good"},
            {"review_id": "R1", "review_text": "Good"},
            {"review_id": "R2", "review_text": "Bad"},
        ]
        result = deduplicate_reviews(reviews)
        self.assertEqual(len(result), 2)

    def test_preserves_order(self):
        reviews = [
            {"review_id": "R1", "review_text": "A"},
            {"review_id": "R2", "review_text": "B"},
        ]
        result = deduplicate_reviews(reviews)
        self.assertEqual(result[0]["review_id"], "R1")
        self.assertEqual(result[1]["review_id"], "R2")

    def test_empty_list(self):
        self.assertEqual(deduplicate_reviews([]), [])

    def test_no_review_id_uses_hash(self):
        reviews = [
            {"reviewer_name": "Alice", "review_text": "Same text"},
            {"reviewer_name": "Alice", "review_text": "Same text"},
        ]
        result = deduplicate_reviews(reviews)
        self.assertEqual(len(result), 1)


class TestIsEmptyReview(unittest.TestCase):
    def test_empty_review(self):
        self.assertTrue(is_empty_review({"review_title": "", "review_text": ""}))

    def test_non_empty_review(self):
        self.assertFalse(
            is_empty_review({"review_title": "Good", "review_text": "Works well"})
        )

    def test_only_title(self):
        self.assertFalse(
            is_empty_review({"review_title": "Good", "review_text": ""})
        )

    def test_only_text(self):
        self.assertFalse(
            is_empty_review({"review_title": "", "review_text": "Works"})
        )

    def test_whitespace_only(self):
        self.assertTrue(
            is_empty_review({"review_title": "   ", "review_text": "  "})
        )


if __name__ == "__main__":
    unittest.main()
