"""
test_helper.py – Unit tests for the helper utility functions.

Tests cover:
* generate_product_id (ASIN extraction, PID extraction, fallback hash).
* generate_review_id (stable hash).
* is_valid_url.
* is_captcha_page (mocked driver).
* retry decorator (success, failure, max attempts).
* truncate.
* chunk_list.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.helper import (
    chunk_list,
    generate_product_id,
    generate_review_id,
    is_captcha_page,
    is_valid_url,
    retry,
    truncate,
)


class TestGenerateProductId(unittest.TestCase):
    def test_extracts_amazon_asin(self):
        url = "https://www.amazon.in/dp/B0CH7RLKFC/ref=sr_1_1"
        self.assertEqual(generate_product_id(url), "B0CH7RLKFC")

    def test_extracts_flipkart_pid(self):
        url = (
            "https://www.flipkart.com/sony-headphones/"
            "p/itm?pid=EARHZ5NGXJ5BVQY2"
        )
        self.assertEqual(generate_product_id(url), "EARHZ5NGXJ5BVQY2")

    def test_fallback_hash_for_unknown_url(self):
        url = "https://example.com/product/12345"
        result = generate_product_id(url)
        self.assertEqual(len(result), 16)
        self.assertTrue(result.isupper() or result.isalnum())

    def test_stable_output_for_same_url(self):
        url = "https://example.com/product/test"
        self.assertEqual(generate_product_id(url), generate_product_id(url))


class TestGenerateReviewId(unittest.TestCase):
    def test_returns_16_char_string(self):
        result = generate_review_id("P1", "Alice", "2024-01-01", "Good product")
        self.assertEqual(len(result), 16)

    def test_stable_for_same_inputs(self):
        args = ("P1", "Alice", "2024-01-01", "Good product")
        self.assertEqual(generate_review_id(*args), generate_review_id(*args))

    def test_different_for_different_inputs(self):
        id1 = generate_review_id("P1", "Alice", "2024-01-01", "Good")
        id2 = generate_review_id("P1", "Bob", "2024-01-01", "Good")
        self.assertNotEqual(id1, id2)


class TestIsValidUrl(unittest.TestCase):
    def test_valid_https_url(self):
        self.assertTrue(is_valid_url("https://www.amazon.in/dp/ABC123"))

    def test_valid_http_url(self):
        self.assertTrue(is_valid_url("http://example.com"))

    def test_empty_string(self):
        self.assertFalse(is_valid_url(""))

    def test_no_scheme(self):
        self.assertFalse(is_valid_url("www.example.com/product"))

    def test_ftp_scheme(self):
        self.assertFalse(is_valid_url("ftp://example.com"))

    def test_none_like_string(self):
        self.assertFalse(is_valid_url("None"))


class TestIsCaptchaPage(unittest.TestCase):
    def _make_driver(self, page_source: str, title: str) -> MagicMock:
        driver = MagicMock()
        driver.page_source = page_source
        driver.title = title
        return driver

    def test_detects_captcha_in_source(self):
        driver = self._make_driver(
            "<html>Please complete this captcha challenge</html>",
            "Amazon",
        )
        self.assertTrue(is_captcha_page(driver))

    def test_detects_robot_check(self):
        driver = self._make_driver(
            "<html>verify you are human to continue</html>",
            "Robot Check",
        )
        self.assertTrue(is_captcha_page(driver))

    def test_normal_page(self):
        driver = self._make_driver(
            "<html><h1>Product Page</h1></html>",
            "Sony Headphones | Amazon.in",
        )
        self.assertFalse(is_captcha_page(driver))

    def test_access_denied_in_title(self):
        driver = self._make_driver(
            "<html>Sorry</html>",
            "Access Denied",
        )
        self.assertTrue(is_captcha_page(driver))


class TestRetryDecorator(unittest.TestCase):
    def test_succeeds_on_first_attempt(self):
        call_count = [0]

        @retry(max_attempts=3, delay=0)
        def func():
            call_count[0] += 1
            return "ok"

        result = func()
        self.assertEqual(result, "ok")
        self.assertEqual(call_count[0], 1)

    def test_retries_on_failure_then_succeeds(self):
        call_count = [0]

        @retry(max_attempts=3, delay=0)
        def func():
            call_count[0] += 1
            if call_count[0] < 3:
                raise ValueError("Temporary error")
            return "success"

        result = func()
        self.assertEqual(result, "success")
        self.assertEqual(call_count[0], 3)

    def test_raises_after_max_attempts(self):
        call_count = [0]

        @retry(max_attempts=2, delay=0)
        def func():
            call_count[0] += 1
            raise ConnectionError("Always fails")

        with self.assertRaises(ConnectionError):
            func()
        self.assertEqual(call_count[0], 2)

    def test_only_catches_specified_exceptions(self):
        """Decorator does not catch unspecified exceptions."""
        @retry(max_attempts=3, delay=0, exceptions=(ValueError,))
        def func():
            raise RuntimeError("Not caught")

        with self.assertRaises(RuntimeError):
            func()

    def test_preserves_function_name(self):
        @retry(max_attempts=3, delay=0)
        def my_function():
            pass

        self.assertEqual(my_function.__name__, "my_function")


class TestTruncate(unittest.TestCase):
    def test_short_string_unchanged(self):
        self.assertEqual(truncate("Hello", 100), "Hello")

    def test_long_string_truncated(self):
        long = "A" * 600
        result = truncate(long, 500)
        self.assertTrue(result.endswith("…"))
        self.assertLessEqual(len(result), 502)

    def test_empty_string(self):
        self.assertEqual(truncate("", 100), "")


class TestChunkList(unittest.TestCase):
    def test_even_chunks(self):
        result = chunk_list([1, 2, 3, 4], 2)
        self.assertEqual(result, [[1, 2], [3, 4]])

    def test_uneven_chunks(self):
        result = chunk_list([1, 2, 3, 4, 5], 2)
        self.assertEqual(result, [[1, 2], [3, 4], [5]])

    def test_chunk_larger_than_list(self):
        result = chunk_list([1, 2], 10)
        self.assertEqual(result, [[1, 2]])

    def test_empty_list(self):
        self.assertEqual(chunk_list([], 5), [])


if __name__ == "__main__":
    unittest.main()
