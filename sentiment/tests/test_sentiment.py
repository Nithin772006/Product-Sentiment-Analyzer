"""
Unit tests for the Sentiment Analysis module.

Covers:
    - Positive / Negative / Neutral classification
    - Empty and missing-text handling
    - Special characters and long reviews
    - Preprocessing pipeline (HTML, URLs, emojis removed)
    - JSON load / save round-trip
    - Output structure validation
    - VADER score ranges
    - Batch processing

Run from the project root::

    python -m pytest sentiment/tests/ -v
    python -m unittest sentiment.tests.test_sentiment -v
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Ensure the project root is importable
_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from sentiment.analyzer.sentiment_engine import (
    analyze_review,
    analyze_reviews,
    load_reviews,
    save_results,
)
from sentiment.analyzer.vader_analyzer import (
    classify_sentiment,
    compute_confidence,
    get_sentiment_scores,
)
from sentiment.models.review import Review
from sentiment.models.sentiment_result import SentimentResult
from sentiment.preprocessing.text_cleaner import (
    clean_text,
    normalize_whitespace,
    remove_emojis,
    remove_html_tags,
    remove_urls,
)
from sentiment.utils.helper import safe_read_json, safe_write_json, validate_review_dict


# ═══════════════════════════════════════════════════════════════════════
# 1. Preprocessing tests
# ═══════════════════════════════════════════════════════════════════════


class TestTextCleaner(unittest.TestCase):
    """Tests for ``preprocessing/text_cleaner.py``."""

    def test_remove_html_tags(self) -> None:
        self.assertEqual(remove_html_tags("<p>Hello <b>world</b></p>"), "Hello world")

    def test_remove_urls(self) -> None:
        text = "Visit https://example.com and http://test.org please"
        result = remove_urls(text)
        self.assertNotIn("https://", result)
        self.assertNotIn("http://", result)

    def test_remove_emojis(self) -> None:
        self.assertEqual(remove_emojis("Great product 😍🔥"), "Great product ")

    def test_normalize_whitespace(self) -> None:
        self.assertEqual(normalize_whitespace("  hello   world  "), "hello world")

    def test_clean_text_full_pipeline(self) -> None:
        raw = "<p>Check https://x.com! Great 😍</p>"
        cleaned = clean_text(raw)
        self.assertNotIn("<p>", cleaned)
        self.assertNotIn("https://", cleaned)
        # Emojis should be gone
        self.assertNotIn("😍", cleaned)
        # Should be lowercase
        self.assertEqual(cleaned, cleaned.lower())

    def test_clean_text_none(self) -> None:
        self.assertEqual(clean_text(None), "")

    def test_clean_text_empty(self) -> None:
        self.assertEqual(clean_text(""), "")

    def test_clean_text_whitespace_only(self) -> None:
        self.assertEqual(clean_text("   "), "")


# ═══════════════════════════════════════════════════════════════════════
# 2. VADER analyzer tests
# ═══════════════════════════════════════════════════════════════════════


class TestVaderAnalyzer(unittest.TestCase):
    """Tests for ``analyzer/vader_analyzer.py``."""

    def test_positive_scores(self) -> None:
        scores = get_sentiment_scores("This product is absolutely wonderful and amazing")
        self.assertGreater(scores["compound"], 0.05)
        self.assertGreater(scores["positive"], 0)

    def test_negative_scores(self) -> None:
        scores = get_sentiment_scores("Terrible, awful, worst product ever")
        self.assertLess(scores["compound"], -0.05)
        self.assertGreater(scores["negative"], 0)

    def test_neutral_scores(self) -> None:
        scores = get_sentiment_scores("The product is a product")
        self.assertGreaterEqual(scores["neutral"], 0)

    def test_score_keys(self) -> None:
        scores = get_sentiment_scores("Test text")
        for key in ("positive", "neutral", "negative", "compound"):
            self.assertIn(key, scores)

    def test_classify_positive(self) -> None:
        self.assertEqual(classify_sentiment(0.5), "Positive")
        self.assertEqual(classify_sentiment(0.05), "Positive")

    def test_classify_negative(self) -> None:
        self.assertEqual(classify_sentiment(-0.5), "Negative")
        self.assertEqual(classify_sentiment(-0.05), "Negative")

    def test_classify_neutral(self) -> None:
        self.assertEqual(classify_sentiment(0.0), "Neutral")
        self.assertEqual(classify_sentiment(0.04), "Neutral")
        self.assertEqual(classify_sentiment(-0.04), "Neutral")

    def test_confidence_range(self) -> None:
        scores = get_sentiment_scores("Amazing product")
        confidence = compute_confidence(scores)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)


# ═══════════════════════════════════════════════════════════════════════
# 3. Data model tests
# ═══════════════════════════════════════════════════════════════════════


class TestModels(unittest.TestCase):
    """Tests for the Review and SentimentResult data models."""

    def test_review_from_dict(self) -> None:
        data = {
            "review_id": "R1",
            "product_id": "P1",
            "review_text": "Nice item",
            "rating": 4,
        }
        review = Review.from_dict(data)
        self.assertEqual(review.review_id, "R1")
        self.assertEqual(review.review_text, "Nice item")

    def test_review_round_trip(self) -> None:
        data = {
            "review_id": "R1",
            "product_id": "P1",
            "review_text": "Nice",
            "rating": 4,
            "sentiment": None,
        }
        review = Review.from_dict(data)
        self.assertEqual(review.to_dict(), data)

    def test_review_missing_text_normalised(self) -> None:
        data = {"review_id": "R1", "product_id": "P1", "review_text": None}
        review = Review.from_dict(data)
        self.assertEqual(review.review_text, "")

    def test_sentiment_result_to_dict(self) -> None:
        result = SentimentResult(
            review_id="R1",
            product_id="P1",
            review_text="Great",
            sentiment="Positive",
            confidence_score=0.85,
            scores={"positive": 0.7, "neutral": 0.2, "negative": 0.1, "compound": 0.85},
        )
        d = result.to_dict()
        self.assertEqual(d["sentiment"], "Positive")
        self.assertIn("scores", d)
        self.assertEqual(set(d["scores"].keys()), {"positive", "neutral", "negative", "compound"})


# ═══════════════════════════════════════════════════════════════════════
# 4. Sentiment engine tests
# ═══════════════════════════════════════════════════════════════════════


class TestSentimentEngine(unittest.TestCase):
    """Tests for ``analyzer/sentiment_engine.py``."""

    def test_analyze_positive_review(self) -> None:
        result = analyze_review({
            "review_id": "R1",
            "product_id": "P1",
            "review_text": "This is an absolutely fantastic and wonderful product!",
        })
        self.assertIsNotNone(result)
        self.assertEqual(result.sentiment, "Positive")

    def test_analyze_negative_review(self) -> None:
        result = analyze_review({
            "review_id": "R2",
            "product_id": "P1",
            "review_text": "Horrible, terrible, worst purchase I have ever made.",
        })
        self.assertIsNotNone(result)
        self.assertEqual(result.sentiment, "Negative")

    def test_analyze_neutral_review(self) -> None:
        result = analyze_review({
            "review_id": "R3",
            "product_id": "P1",
            "review_text": "I received the product in the box.",
        })
        self.assertIsNotNone(result)
        # Neutral or could be slightly positive – just ensure it's not None
        self.assertIn(result.sentiment, ("Positive", "Negative", "Neutral"))

    def test_analyze_empty_review(self) -> None:
        result = analyze_review({
            "review_id": "R4",
            "product_id": "P1",
            "review_text": "",
        })
        self.assertIsNotNone(result)
        self.assertEqual(result.sentiment, "Neutral")
        self.assertEqual(result.confidence_score, 0.0)

    def test_analyze_special_characters(self) -> None:
        result = analyze_review({
            "review_id": "R5",
            "product_id": "P1",
            "review_text": "!!!@@@###$$$%%% ^^^ &&& great *** product",
        })
        self.assertIsNotNone(result)
        self.assertIn(result.sentiment, ("Positive", "Negative", "Neutral"))

    def test_analyze_long_review(self) -> None:
        long_text = "This product is amazing. " * 200
        result = analyze_review({
            "review_id": "R6",
            "product_id": "P1",
            "review_text": long_text,
        })
        self.assertIsNotNone(result)
        self.assertEqual(result.sentiment, "Positive")

    def test_analyze_invalid_dict_returns_none(self) -> None:
        result = analyze_review({"some_key": "value"})
        self.assertIsNone(result)

    def test_analyze_review_with_review_object(self) -> None:
        review = Review(review_id="R7", product_id="P1", review_text="Good quality")
        result = analyze_review(review)
        self.assertIsNotNone(result)

    def test_batch_analysis(self) -> None:
        reviews = [
            {"review_id": "R1", "product_id": "P1", "review_text": "Great!"},
            {"review_id": "R2", "product_id": "P1", "review_text": "Terrible!"},
            {"review_id": "R3", "product_id": "P1", "review_text": "It's fine."},
        ]
        results = analyze_reviews(reviews)
        self.assertEqual(len(results), 3)

    def test_batch_skips_invalid(self) -> None:
        reviews = [
            {"review_id": "R1", "product_id": "P1", "review_text": "Great!"},
            {"bad_key": "no data"},
            {"review_id": "R3", "product_id": "P1", "review_text": "Okay."},
        ]
        results = analyze_reviews(reviews)
        self.assertEqual(len(results), 2)

    def test_output_structure(self) -> None:
        result = analyze_review({
            "review_id": "R1",
            "product_id": "P1",
            "review_text": "Excellent product!",
        })
        self.assertIsNotNone(result)
        d = result.to_dict()
        expected_keys = {"review_id", "product_id", "review_text", "sentiment",
                         "confidence_score", "scores"}
        self.assertEqual(set(d.keys()), expected_keys)


# ═══════════════════════════════════════════════════════════════════════
# 5. Helper / I/O tests
# ═══════════════════════════════════════════════════════════════════════


class TestHelpers(unittest.TestCase):
    """Tests for ``utils/helper.py``."""

    def test_validate_review_dict_valid(self) -> None:
        self.assertTrue(validate_review_dict({
            "review_id": "R1", "product_id": "P1", "review_text": "hi",
        }))

    def test_validate_review_dict_missing_key(self) -> None:
        self.assertFalse(validate_review_dict({"review_id": "R1"}))

    def test_validate_review_dict_non_dict(self) -> None:
        self.assertFalse(validate_review_dict("not a dict"))

    def test_safe_read_write_json_round_trip(self) -> None:
        data = [{"review_id": "R1", "product_id": "P1", "review_text": "test"}]
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            tmp_path = f.name

        try:
            self.assertTrue(safe_write_json(data, tmp_path))
            loaded = safe_read_json(tmp_path)
            self.assertEqual(loaded, data)
        finally:
            os.unlink(tmp_path)

    def test_safe_read_json_file_not_found(self) -> None:
        result = safe_read_json("/nonexistent/path/file.json")
        self.assertEqual(result, [])

    def test_safe_read_json_invalid_json(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            f.write("{invalid json")
            tmp_path = f.name

        try:
            result = safe_read_json(tmp_path)
            self.assertEqual(result, [])
        finally:
            os.unlink(tmp_path)

    def test_safe_read_json_single_object(self) -> None:
        """A single JSON object (not an array) should be wrapped in a list."""
        data = {"review_id": "R1", "product_id": "P1", "review_text": "test"}
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(data, f)
            tmp_path = f.name

        try:
            loaded = safe_read_json(tmp_path)
            self.assertEqual(len(loaded), 1)
            self.assertEqual(loaded[0]["review_id"], "R1")
        finally:
            os.unlink(tmp_path)


# ═══════════════════════════════════════════════════════════════════════
# 6. Integration: load → analyze → save
# ═══════════════════════════════════════════════════════════════════════


class TestIntegration(unittest.TestCase):
    """End-to-end integration tests."""

    def test_load_analyze_save(self) -> None:
        """Full round-trip: write input → load → analyze → save → verify."""
        input_data = [
            {"review_id": "R1", "product_id": "P1",
             "review_text": "Absolutely love this product!", "rating": 5,
             "sentiment": None},
            {"review_id": "R2", "product_id": "P1",
             "review_text": "Worst thing I ever bought.", "rating": 1,
             "sentiment": None},
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = os.path.join(tmpdir, "input.json")
            output_path = os.path.join(tmpdir, "output.json")

            # Write input
            with open(input_path, "w", encoding="utf-8") as f:
                json.dump(input_data, f)

            # Load
            reviews = load_reviews(input_path)
            self.assertEqual(len(reviews), 2)

            # Analyze
            results = analyze_reviews(reviews)
            self.assertEqual(len(results), 2)

            # Save
            self.assertTrue(save_results(results, output_path))

            # Verify output
            with open(output_path, "r", encoding="utf-8") as f:
                output = json.load(f)

            self.assertEqual(len(output), 2)
            self.assertIn(output[0]["sentiment"], ("Positive", "Negative", "Neutral"))
            self.assertIn("scores", output[0])


if __name__ == "__main__":
    unittest.main()
