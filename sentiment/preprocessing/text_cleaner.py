"""
Text cleaning utilities for the Sentiment Analysis module.

Every function is a **pure function** (no side-effects) that accepts a
string and returns a cleaned string.  The top-level :func:`clean_text`
orchestrates all individual steps in the recommended order.
"""

from __future__ import annotations

import re
import string


# ── Individual cleaning steps ──────────────────────────────────────────

def remove_html_tags(text: str) -> str:
    """Strip HTML / XML tags.

    >>> remove_html_tags("<p>Hello <b>world</b></p>")
    'Hello world'
    """
    return re.sub(r"<[^>]+>", "", text)


def remove_urls(text: str) -> str:
    """Remove ``http(s)://…`` and ``www.…`` URLs.

    >>> remove_urls("Visit https://example.com for details")
    'Visit  for details'
    """
    return re.sub(r"https?://\S+|www\.\S+", "", text)


def remove_emojis(text: str) -> str:
    """Remove emoji characters (Unicode emoji ranges).

    Covers the most common emoji blocks including emoticons, symbols,
    dingbats, flags, and supplemental symbols.
    """
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002702-\U000027B0"  # dingbats
        "\U000024C2-\U0001F251"  # enclosed characters
        "\U0001F900-\U0001F9FF"  # supplemental symbols
        "\U0001FA00-\U0001FA6F"  # chess symbols
        "\U0001FA70-\U0001FAFF"  # symbols extended-A
        "]+",
        flags=re.UNICODE,
    )
    return emoji_pattern.sub("", text)


def remove_punctuation(text: str) -> str:
    """Remove all ASCII punctuation characters.

    >>> remove_punctuation("Hello, world!")
    'Hello world'
    """
    return text.translate(str.maketrans("", "", string.punctuation))


def remove_special_characters(text: str) -> str:
    """Keep only alphanumeric characters and whitespace.

    This is a stricter pass than :func:`remove_punctuation` and catches
    non-ASCII special characters as well.

    >>> remove_special_characters("price: $19.99 — great!")
    'price 1999  great'
    """
    return re.sub(r"[^A-Za-z0-9\s]", "", text)


def normalize_whitespace(text: str) -> str:
    """Collapse multiple spaces / tabs / newlines into a single space.

    >>> normalize_whitespace("  hello   world  ")
    'hello world'
    """
    return re.sub(r"\s+", " ", text).strip()


# ── Orchestrator ───────────────────────────────────────────────────────

def clean_text(text: str | None) -> str:
    """Run the full cleaning pipeline on *text*.

    Steps (in order):
    1. Handle ``None`` / non-string values
    2. Convert to lowercase
    3. Remove HTML tags
    4. Remove URLs
    5. Remove emojis
    6. Remove special characters (keeps alphanumeric + spaces)
    7. Normalize whitespace

    Args:
        text: Raw review text.

    Returns:
        Cleaned, lowercase, single-spaced text ready for analysis.
    """
    if not text or not isinstance(text, str):
        return ""

    text = text.lower()
    text = remove_html_tags(text)
    text = remove_urls(text)
    text = remove_emojis(text)
    text = remove_special_characters(text)
    text = normalize_whitespace(text)

    return text
