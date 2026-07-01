"""
High-level sentiment analysis orchestrator.

This module ties together preprocessing, VADER scoring, and data models
to provide a clean API that the Flask backend (or any caller) can use:

    >>> from sentiment.analyzer.sentiment_engine import analyze_review
    >>> result = analyze_review({"review_id": "R1", "product_id": "P1",
    ...                          "review_text": "Great product!"})
    >>> result.sentiment
    'Positive'
"""

from __future__ import annotations

from typing import Any

from sentiment.analyzer.vader_analyzer import (
    classify_sentiment,
    compute_confidence,
    get_sentiment_scores,
)
from sentiment.models.review import Review
from sentiment.models.sentiment_result import SentimentResult
from sentiment.preprocessing.text_cleaner import clean_text
from sentiment.utils.helper import safe_read_json, safe_write_json, validate_review_dict
from sentiment.utils.logger import get_logger

logger = get_logger()


# ── Single review ──────────────────────────────────────────────────────

def analyze_review(review_data: dict[str, Any] | Review) -> SentimentResult | None:
    """Analyze a single review and return a :class:`SentimentResult`.

    Accepts either a raw dictionary (as received from the scraping
    pipeline) or a :class:`Review` dataclass instance.

    Args:
        review_data: Review data to analyze.

    Returns:
        A :class:`SentimentResult`, or ``None`` if the input is invalid.
    """
    # ── Normalise input ────────────────────────────────────────────────
    if isinstance(review_data, dict):
        if not validate_review_dict(review_data):
            logger.warning(
                "Skipping invalid review dict (missing required keys): %s",
                review_data,
            )
            return None
        try:
            review = Review.from_dict(review_data)
        except (KeyError, TypeError, ValueError) as exc:
            logger.warning("Failed to parse review dict: %s – %s", review_data, exc)
            return None
    elif isinstance(review_data, Review):
        review = review_data
    else:
        logger.warning("Unsupported review_data type: %s", type(review_data).__name__)
        return None

    # ── Preprocess ─────────────────────────────────────────────────────
    cleaned = clean_text(review.review_text)

    if not cleaned:
        logger.warning(
            "Review %s has empty text after cleaning – assigning Neutral.",
            review.review_id,
        )
        return SentimentResult(
            review_id=review.review_id,
            product_id=review.product_id,
            review_text=review.review_text,
            sentiment="Neutral",
            confidence_score=0.0,
            scores={"positive": 0.0, "neutral": 1.0, "negative": 0.0, "compound": 0.0},
        )

    # ── Analyse ────────────────────────────────────────────────────────
    scores = get_sentiment_scores(cleaned)
    sentiment = classify_sentiment(scores["compound"])
    confidence = compute_confidence(scores)

    logger.debug(
        "Review %s → %s (compound=%.4f, confidence=%.4f)",
        review.review_id,
        sentiment,
        scores["compound"],
        confidence,
    )

    return SentimentResult(
        review_id=review.review_id,
        product_id=review.product_id,
        review_text=review.review_text,
        sentiment=sentiment,
        confidence_score=confidence,
        scores=scores,
    )


# ── Batch processing ──────────────────────────────────────────────────

def analyze_reviews(
    reviews: list[dict[str, Any]] | list[Review],
) -> list[SentimentResult]:
    """Analyze a batch of reviews.

    Invalid reviews are logged and skipped; the remaining reviews are
    still processed.

    Args:
        reviews: A list of review dicts or :class:`Review` instances.

    Returns:
        A list of :class:`SentimentResult` objects (one per valid review).
    """
    results: list[SentimentResult] = []
    total = len(reviews)
    logger.info("Starting batch analysis of %d review(s)…", total)

    for idx, rev in enumerate(reviews, start=1):
        result = analyze_review(rev)
        if result is not None:
            results.append(result)

        if idx % 100 == 0 or idx == total:
            logger.info("Processed %d / %d reviews.", idx, total)

    logger.info(
        "Batch complete – %d / %d reviews analyzed successfully.",
        len(results),
        total,
    )
    return results


# ── File I/O convenience ──────────────────────────────────────────────

def load_reviews(filepath: str) -> list[Review]:
    """Load reviews from a JSON file.

    Args:
        filepath: Path to a JSON file containing an array of review objects.

    Returns:
        A list of :class:`Review` instances.
    """
    raw = safe_read_json(filepath)
    reviews: list[Review] = []

    for item in raw:
        if validate_review_dict(item):
            try:
                reviews.append(Review.from_dict(item))
            except (KeyError, TypeError, ValueError) as exc:
                logger.warning("Skipping malformed review entry: %s", exc)
        else:
            logger.warning("Skipping entry with missing keys: %s", item)

    logger.info("Loaded %d valid review(s) from %s.", len(reviews), filepath)
    return reviews


def save_results(
    results: list[SentimentResult],
    filepath: str,
) -> bool:
    """Save analysis results to a JSON file.

    Args:
        results: List of :class:`SentimentResult` instances.
        filepath: Destination file path.

    Returns:
        ``True`` on success, ``False`` on failure.
    """
    data = [r.to_dict() for r in results]
    return safe_write_json(data, filepath)


def process_file(input_path: str, output_path: str) -> list[SentimentResult]:
    """Full pipeline: load → analyze → save.

    Args:
        input_path: Path to the input JSON file.
        output_path: Path where the output JSON will be written.

    Returns:
        The list of :class:`SentimentResult` objects produced.
    """
    logger.info("═" * 60)
    logger.info("Sentiment Analysis Pipeline – START")
    logger.info("Input : %s", input_path)
    logger.info("Output: %s", output_path)
    logger.info("═" * 60)

    reviews = load_reviews(input_path)

    if not reviews:
        logger.warning("No valid reviews found. Nothing to analyse.")
        return []

    results = analyze_reviews(reviews)
    save_results(results, output_path)

    # ── Summary ────────────────────────────────────────────────────────
    pos = sum(1 for r in results if r.sentiment == "Positive")
    neg = sum(1 for r in results if r.sentiment == "Negative")
    neu = sum(1 for r in results if r.sentiment == "Neutral")

    logger.info("═" * 60)
    logger.info("Sentiment Analysis Pipeline – COMPLETE")
    logger.info("Total analysed : %d", len(results))
    logger.info("  Positive     : %d", pos)
    logger.info("  Negative     : %d", neg)
    logger.info("  Neutral      : %d", neu)
    logger.info("═" * 60)

    return results
