"""
cleaner.py – Data-cleaning helpers for raw scraped text and values.

All cleaning is idempotent and returns a copy rather than mutating the
input. Import individual functions or call ``clean_review`` / 
``clean_product`` to apply the full pipeline at once.

Usage::

    from utils.cleaner import clean_text, parse_price, clean_review
"""

from __future__ import annotations

import re
import unicodedata
from datetime import datetime
from typing import Any

from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Text cleaning
# ---------------------------------------------------------------------------

# Regex patterns compiled once for performance
_EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map
    "\U0001F1E0-\U0001F1FF"  # flags
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "]+",
    flags=re.UNICODE,
)

_WHITESPACE_PATTERN = re.compile(r"\s+")
_PRICE_DIGITS_PATTERN = re.compile(r"[^\d.]")
_RATING_DIGITS_PATTERN = re.compile(r"(\d+(?:\.\d+)?)")


def remove_html_tags(text: str) -> str:
    """Strip all HTML tags from *text* using BeautifulSoup.

    Args:
        text: Raw string that may contain HTML markup.

    Returns:
        Plain text with no HTML tags.
    """
    if not text:
        return ""
    return BeautifulSoup(text, "html.parser").get_text(separator=" ")


def remove_emojis(text: str) -> str:
    """Remove emoji characters from *text*.

    Args:
        text: Input string.

    Returns:
        String with emojis stripped.
    """
    if not text:
        return ""
    return _EMOJI_PATTERN.sub("", text)


def normalize_whitespace(text: str) -> str:
    """Collapse multiple whitespace characters into a single space.

    Args:
        text: Input string.

    Returns:
        Trimmed string with no double spaces or newlines.
    """
    if not text:
        return ""
    return _WHITESPACE_PATTERN.sub(" ", text).strip()


def clean_text(text: str) -> str:
    """Apply the full text-cleaning pipeline.

    Removes HTML tags → emojis → normalises whitespace.

    Args:
        text: Raw string from a scraped element.

    Returns:
        Clean, human-readable string.
    """
    if not text:
        return ""
    text = remove_html_tags(text)
    text = remove_emojis(text)
    text = normalize_whitespace(text)
    return text


# ---------------------------------------------------------------------------
# Price parsing
# ---------------------------------------------------------------------------

def parse_price(price_str: str) -> float | None:
    """Convert a price string (e.g. '₹1,499.00') to a float.

    Args:
        price_str: Raw price string from the website.

    Returns:
        Numeric price as a float, or ``None`` if parsing fails.
    """
    if not price_str:
        return None
    cleaned = _PRICE_DIGITS_PATTERN.sub("", price_str.strip())
    try:
        return float(cleaned) if cleaned else None
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Rating parsing
# ---------------------------------------------------------------------------

def parse_rating(rating_str: str) -> float | None:
    """Extract the numeric rating from strings like '4.2 out of 5'.

    Args:
        rating_str: Raw rating string.

    Returns:
        Numeric rating as a float, or ``None`` if parsing fails.
    """
    if not rating_str:
        return None
    match = _RATING_DIGITS_PATTERN.search(rating_str.strip())
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None
    return None


# ---------------------------------------------------------------------------
# Date normalisation
# ---------------------------------------------------------------------------

# Ordered list of date formats to try when parsing scraper dates
_DATE_FORMATS: list[str] = [
    "%d %B %Y",       # 15 March 2024
    "%B %d, %Y",      # March 15, 2024
    "%d-%m-%Y",       # 15-03-2024
    "%Y-%m-%d",       # 2024-03-15
    "%d/%m/%Y",       # 15/03/2024
    "%m/%d/%Y",       # 03/15/2024
    "%d %b %Y",       # 15 Mar 2024
    "%b %d, %Y",      # Mar 15, 2024
    "%Y",             # 2024
]


def normalize_date(date_str: str) -> str | None:
    """Parse *date_str* and return an ISO 8601 date string ``'YYYY-MM-DD'``.

    Args:
        date_str: Date string in any common format.

    Returns:
        ISO-formatted date string, or ``None`` if parsing fails.
    """
    if not date_str:
        return None
    cleaned = normalize_whitespace(date_str)
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(cleaned, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return cleaned  # Return as-is if no format matched


# ---------------------------------------------------------------------------
# Review-level cleaning pipeline
# ---------------------------------------------------------------------------

def clean_review(review: dict[str, Any]) -> dict[str, Any]:
    """Apply all cleaning helpers to a raw review dictionary.

    Modifies a copy – the original dict is not mutated.

    Args:
        review: Raw review dict from a scraper.

    Returns:
        Cleaned review dict.
    """
    r = dict(review)  # shallow copy

    r["review_title"] = clean_text(r.get("review_title", ""))
    r["review_text"] = clean_text(r.get("review_text", ""))
    r["reviewer_name"] = clean_text(r.get("reviewer_name", ""))

    # Numeric conversion
    if isinstance(r.get("star_rating"), str):
        r["star_rating"] = parse_rating(r["star_rating"])

    # Date normalisation
    if isinstance(r.get("review_date"), str):
        r["review_date"] = normalize_date(r["review_date"])

    return r


# ---------------------------------------------------------------------------
# Product-level cleaning pipeline
# ---------------------------------------------------------------------------

def clean_product(product: dict[str, Any]) -> dict[str, Any]:
    """Apply all cleaning helpers to a raw product dictionary.

    Modifies a copy – the original dict is not mutated.

    Args:
        product: Raw product dict from a scraper.

    Returns:
        Cleaned product dict.
    """
    p = dict(product)  # shallow copy

    p["product_name"] = clean_text(p.get("product_name", ""))
    p["brand"] = clean_text(p.get("brand", ""))
    p["category"] = clean_text(p.get("category", ""))
    p["description"] = clean_text(p.get("description", ""))
    p["availability"] = clean_text(p.get("availability", ""))

    # Numeric conversion
    if isinstance(p.get("price"), str):
        p["price"] = parse_price(p["price"])
    if isinstance(p.get("discount_price"), str):
        p["discount_price"] = parse_price(p["discount_price"])
    if isinstance(p.get("overall_rating"), str):
        p["overall_rating"] = parse_rating(p["overall_rating"])
    if isinstance(p.get("num_ratings"), str):
        try:
            p["num_ratings"] = int(
                re.sub(r"[^\d]", "", p["num_ratings"])
            )
        except ValueError:
            p["num_ratings"] = None
    if isinstance(p.get("num_reviews"), str):
        try:
            p["num_reviews"] = int(
                re.sub(r"[^\d]", "", p["num_reviews"])
            )
        except ValueError:
            p["num_reviews"] = None

    return p


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------

def deduplicate_reviews(
    reviews: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Remove duplicate reviews based on ``review_id``.

    If a review has no ``review_id``, falls back to hashing the
    reviewer name + text combination.

    Args:
        reviews: List of raw review dicts.

    Returns:
        De-duplicated list preserving first occurrence.
    """
    import hashlib

    seen: set[str] = set()
    unique: list[dict[str, Any]] = []

    for review in reviews:
        key = review.get("review_id") or hashlib.sha256(
            (
                str(review.get("reviewer_name", ""))
                + str(review.get("review_text", ""))
            ).encode()
        ).hexdigest()

        if key not in seen:
            seen.add(key)
            unique.append(review)

    return unique


def is_empty_review(review: dict[str, Any]) -> bool:
    """Return ``True`` if a review has no meaningful text content.

    Args:
        review: Review dict to check.

    Returns:
        ``True`` if both title and text are empty/whitespace.
    """
    title = (review.get("review_title") or "").strip()
    text = (review.get("review_text") or "").strip()
    return not title and not text
