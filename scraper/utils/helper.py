"""
helper.py – Generic utility functions shared across all scraper components.

Includes:
* Retry decorator with exponential back-off.
* Unique ID generators.
* URL validation.
* Safe browser navigation.

Usage::

    from utils.helper import retry, generate_product_id, safe_get
"""

from __future__ import annotations

import functools
import hashlib
import re
import time
import uuid
from typing import Any, Callable, TypeVar
from urllib.parse import urlparse

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webdriver import WebDriver

from utils.logger import get_logger

logger = get_logger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


# ---------------------------------------------------------------------------
# Retry decorator
# ---------------------------------------------------------------------------

def retry(
    max_attempts: int = 3,
    delay: float = 2.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
    on_retry: Callable[[int, Exception], None] | None = None,
) -> Callable[[F], F]:
    """Decorator that retries the wrapped function on failure.

    Uses exponential back-off: waits ``delay * 2^(attempt-1)`` seconds
    between retries.

    Args:
        max_attempts: Maximum number of attempts (including the first call).
        delay:        Initial delay in seconds between retries.
        exceptions:   Tuple of exception types to catch and retry.
        on_retry:     Optional callback ``(attempt_number, exception)``
                      called before each retry.

    Returns:
        Decorated callable with automatic retry behaviour.

    Example::

        @retry(max_attempts=3, delay=1.5)
        def fetch_page(driver, url):
            driver.get(url)
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exc: Exception | None = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    last_exc = exc
                    if attempt == max_attempts:
                        logger.error(
                            "[%s] All %d attempt(s) failed. Last error: %s",
                            func.__name__,
                            max_attempts,
                            exc,
                        )
                        raise
                    wait = delay * (2 ** (attempt - 1))
                    logger.warning(
                        "[%s] Attempt %d/%d failed (%s). Retrying in %.1fs …",
                        func.__name__,
                        attempt,
                        max_attempts,
                        exc,
                        wait,
                    )
                    if on_retry:
                        on_retry(attempt, exc)
                    time.sleep(wait)
            raise RuntimeError("Retry logic error – should not reach here")

        return wrapper  # type: ignore[return-value]

    return decorator


# ---------------------------------------------------------------------------
# ID generation
# ---------------------------------------------------------------------------

def generate_product_id(url: str) -> str:
    """Derive a stable product ID from its URL.

    Extracts the ASIN / product slug from the URL if possible; otherwise
    returns a SHA-256 hash of the full URL.

    Args:
        url: Product page URL.

    Returns:
        Short alphanumeric ID string.
    """
    # Amazon ASIN pattern: /dp/XXXXXXXXXX
    asin_match = re.search(r"/dp/([A-Z0-9]{10})", url)
    if asin_match:
        return asin_match.group(1)

    # Flipkart PID pattern: pid=XXXXXXXXXXXXXXXX
    pid_match = re.search(r"pid=([A-Z0-9]+)", url, re.IGNORECASE)
    if pid_match:
        return pid_match.group(1)

    # Fallback: SHA-256 of the URL (first 16 hex chars)
    return hashlib.sha256(url.encode()).hexdigest()[:16].upper()


def generate_review_id(
    product_id: str,
    reviewer_name: str,
    review_date: str,
    review_text: str,
) -> str:
    """Create a stable, unique review ID.

    Combines key fields into a SHA-256 hash so the same review always
    gets the same ID, enabling deduplication across runs.

    Args:
        product_id:    Parent product identifier.
        reviewer_name: Name of the reviewer.
        review_date:   Date string of the review.
        review_text:   Full review body text.

    Returns:
        16-character uppercase hex string.
    """
    raw = f"{product_id}|{reviewer_name}|{review_date}|{review_text[:100]}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16].upper()


# ---------------------------------------------------------------------------
# URL validation
# ---------------------------------------------------------------------------

def is_valid_url(url: str) -> bool:
    """Return ``True`` if *url* is a well-formed HTTP(S) URL.

    Args:
        url: String to validate.

    Returns:
        Boolean validity flag.
    """
    try:
        result = urlparse(url)
        return all([result.scheme in ("http", "https"), result.netloc])
    except Exception:  # pylint: disable=broad-except
        return False


# ---------------------------------------------------------------------------
# Safe browser navigation
# ---------------------------------------------------------------------------

def safe_get(
    driver: WebDriver,
    url: str,
    timeout: int = 30,
) -> bool:
    """Navigate *driver* to *url*, handling common exceptions.

    Args:
        driver:  Active WebDriver instance.
        url:     Target URL.
        timeout: Page-load timeout in seconds.

    Returns:
        ``True`` on success, ``False`` on failure.
    """
    if not is_valid_url(url):
        logger.error("Invalid URL, skipping navigation: %s", url)
        return False

    try:
        driver.set_page_load_timeout(timeout)
        driver.get(url)
        logger.debug("Navigated to: %s", url)
        return True
    except WebDriverException as exc:
        logger.error("Failed to load URL %s – %s", url, exc)
        return False


# ---------------------------------------------------------------------------
# Captcha detection
# ---------------------------------------------------------------------------

def is_captcha_page(driver: WebDriver) -> bool:
    """Heuristically detect common CAPTCHA / bot-detection pages.

    Checks page title and body text for known challenge patterns.

    Args:
        driver: Active WebDriver instance.

    Returns:
        ``True`` if a CAPTCHA is likely present.
    """
    indicators = [
        "captcha",
        "robot",
        "verify you are human",
        "unusual traffic",
        "access denied",
        "bot check",
        "press & hold",
    ]
    try:
        page_source = (driver.page_source or "").lower()
        title = (driver.title or "").lower()
        return any(
            indicator in page_source or indicator in title
            for indicator in indicators
        )
    except Exception:  # pylint: disable=broad-except
        return False


# ---------------------------------------------------------------------------
# Miscellaneous
# ---------------------------------------------------------------------------

def truncate(text: str, max_length: int = 500) -> str:
    """Truncate *text* to *max_length* characters, appending '…'.

    Args:
        text:       Input string.
        max_length: Maximum character length.

    Returns:
        Possibly-truncated string.
    """
    if not text or len(text) <= max_length:
        return text
    return text[:max_length] + "…"


def chunk_list(lst: list[Any], size: int) -> list[list[Any]]:
    """Split *lst* into sub-lists of at most *size* elements.

    Args:
        lst:  Source list.
        size: Maximum sub-list length.

    Returns:
        List of chunks.
    """
    return [lst[i : i + size] for i in range(0, len(lst), size)]
