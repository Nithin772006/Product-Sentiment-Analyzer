"""
urls.py – URL builders for supported e-commerce platforms.

Adding a new platform only requires adding a new builder function here
and registering it in the SEARCH_URL_BUILDERS mapping.
"""

from urllib.parse import quote_plus


def amazon_search_url(keyword: str, page: int = 1) -> str:
    """Return an Amazon.in search results URL for *keyword* at *page*.

    Args:
        keyword: Product search term.
        page:    Result page number (1-indexed).

    Returns:
        Fully qualified Amazon search URL string.
    """
    encoded = quote_plus(keyword)
    url = f"https://www.amazon.in/s?k={encoded}"
    if page > 1:
        url += f"&page={page}"
    return url


def flipkart_search_url(keyword: str, page: int = 1) -> str:
    """Return a Flipkart search results URL for *keyword* at *page*.

    Args:
        keyword: Product search term.
        page:    Result page number (1-indexed).

    Returns:
        Fully qualified Flipkart search URL string.
    """
    encoded = quote_plus(keyword)
    url = f"https://www.flipkart.com/search?q={encoded}"
    if page > 1:
        url += f"&page={page}"
    return url


# ---------------------------------------------------------------------------
# Platform base URLs
# ---------------------------------------------------------------------------

AMAZON_BASE_URL: str = "https://www.amazon.in"
FLIPKART_BASE_URL: str = "https://www.flipkart.com"

# ---------------------------------------------------------------------------
# Registry – maps site identifier → search URL builder
# ---------------------------------------------------------------------------

SEARCH_URL_BUILDERS: dict = {
    "amazon": amazon_search_url,
    "flipkart": flipkart_search_url,
}

SUPPORTED_SITES: list[str] = list(SEARCH_URL_BUILDERS.keys())
