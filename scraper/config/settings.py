"""
settings.py – Central configuration for the scraper module.

All tunable values live here. Override any setting by defining the
corresponding environment variable in your `.env` file.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

# Root of the scraper/ package directory
SCRAPER_ROOT: Path = Path(__file__).resolve().parent.parent

# Load .env from the scraper root (if it exists)
load_dotenv(SCRAPER_ROOT / ".env")

# Output directories
OUTPUT_DIR: Path = SCRAPER_ROOT / "output"
JSON_OUTPUT_DIR: Path = OUTPUT_DIR / "json"
CSV_OUTPUT_DIR: Path = OUTPUT_DIR / "csv"
LOG_DIR: Path = SCRAPER_ROOT / "logs"
DRIVERS_DIR: Path = SCRAPER_ROOT / "drivers"

# Ensure runtime directories exist
for _dir in (JSON_OUTPUT_DIR, CSV_OUTPUT_DIR, LOG_DIR, DRIVERS_DIR):
    _dir.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Browser settings
# ---------------------------------------------------------------------------

# Run Chrome in headless mode (set HEADLESS=false in .env to disable)
HEADLESS: bool = os.getenv("HEADLESS", "true").lower() == "true"

# Open browser in incognito/private mode
INCOGNITO: bool = os.getenv("INCOGNITO", "true").lower() == "true"

# Custom User-Agent string to reduce detection
USER_AGENT: str = os.getenv(
    "USER_AGENT",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36",
)

# Browser window size (only relevant when headless is False)
WINDOW_WIDTH: int = int(os.getenv("WINDOW_WIDTH", "1920"))
WINDOW_HEIGHT: int = int(os.getenv("WINDOW_HEIGHT", "1080"))

# ---------------------------------------------------------------------------
# Timing & waits
# ---------------------------------------------------------------------------

# Maximum time (seconds) to wait for a page element to appear
PAGE_TIMEOUT: int = int(os.getenv("PAGE_TIMEOUT", "20"))

# Implicit wait as a fallback (seconds) – kept low; prefer explicit waits
IMPLICIT_WAIT: int = int(os.getenv("IMPLICIT_WAIT", "5"))

# Scroll pause between scroll steps when loading dynamic content (seconds)
SCROLL_PAUSE: float = float(os.getenv("SCROLL_PAUSE", "1.5"))

# ---------------------------------------------------------------------------
# Scraping limits
# ---------------------------------------------------------------------------

# Maximum number of products to scrape per search keyword
MAX_PRODUCTS: int = int(os.getenv("MAX_PRODUCTS", "10"))

# Maximum number of reviews to collect per product
MAX_REVIEWS: int = int(os.getenv("MAX_REVIEWS", "50"))

# Maximum pagination pages to traverse for product listings
MAX_SEARCH_PAGES: int = int(os.getenv("MAX_SEARCH_PAGES", "3"))

# Maximum pagination pages for reviews per product
MAX_REVIEW_PAGES: int = int(os.getenv("MAX_REVIEW_PAGES", "5"))

# ---------------------------------------------------------------------------
# Retry settings
# ---------------------------------------------------------------------------

# Number of retry attempts on failure (network, timeout, captcha)
RETRY_ATTEMPTS: int = int(os.getenv("RETRY_ATTEMPTS", "3"))

# Initial delay (seconds) between retries – doubles on each attempt
RETRY_DELAY: float = float(os.getenv("RETRY_DELAY", "2.0"))

# ---------------------------------------------------------------------------
# Export settings
# ---------------------------------------------------------------------------

# Export results as JSON files
EXPORT_JSON: bool = os.getenv("EXPORT_JSON", "true").lower() == "true"

# Export results as CSV files
EXPORT_CSV: bool = os.getenv("EXPORT_CSV", "true").lower() == "true"

# JSON output file names
PRODUCTS_JSON_FILE: Path = JSON_OUTPUT_DIR / "products.json"
REVIEWS_JSON_FILE: Path = JSON_OUTPUT_DIR / "reviews.json"

# CSV output file names
PRODUCTS_CSV_FILE: Path = CSV_OUTPUT_DIR / "products.csv"
REVIEWS_CSV_FILE: Path = CSV_OUTPUT_DIR / "reviews.csv"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

LOG_FILE: Path = LOG_DIR / "scraper.log"
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()

# Maximum log file size before rotation (bytes) – default 5 MB
LOG_MAX_BYTES: int = int(os.getenv("LOG_MAX_BYTES", str(5 * 1024 * 1024)))

# Number of rotated log files to keep
LOG_BACKUP_COUNT: int = int(os.getenv("LOG_BACKUP_COUNT", "3"))
