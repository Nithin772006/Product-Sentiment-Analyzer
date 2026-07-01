"""
Tokenization utilities for the Sentiment Analysis module.

Provides a thin wrapper around NLTK's word tokenizer, ensuring the
required data files are downloaded automatically on first use.
"""

from __future__ import annotations

import nltk


def _ensure_punkt() -> None:
    """Download the ``punkt_tab`` tokenizer data if it is not present."""
    try:
        nltk.data.find("tokenizers/punkt_tab")
    except LookupError:
        nltk.download("punkt_tab", quiet=True)


def tokenize_text(text: str) -> list[str]:
    """Tokenize *text* into a list of word tokens.

    Uses NLTK's :func:`~nltk.tokenize.word_tokenize` under the hood.
    The ``punkt_tab`` resource is downloaded lazily on the first call.

    Args:
        text: Input text string.

    Returns:
        A list of token strings.

    Example:
        >>> tokenize_text("The product quality is amazing")
        ['The', 'product', 'quality', 'is', 'amazing']
    """
    if not text or not isinstance(text, str):
        return []

    _ensure_punkt()
    return nltk.word_tokenize(text)
