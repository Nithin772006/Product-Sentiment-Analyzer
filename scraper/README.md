# Scraper Module

Selenium-based web scraping module for the **Product Sentiment Analyzer and Review Dashboard** project.

Collects product information and customer reviews from supported e-commerce platforms and exports clean, MongoDB-ready JSON and CSV files.

---

## Table of Contents

1. [Supported Websites](#supported-websites)
2. [Folder Structure](#folder-structure)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [How to Run](#how-to-run)
6. [Output Format](#output-format)
7. [Logging](#logging)
8. [Architecture Overview](#architecture-overview)
9. [Adding a New Website](#adding-a-new-website)
10. [Running Tests](#running-tests)
11. [Known Limitations](#known-limitations)
12. [Future Improvements](#future-improvements)

---

## Supported Websites

| Site | Base URL | Status |
|---|---|---|
| Amazon | https://www.amazon.in | ✅ Implemented |
| Flipkart | https://www.flipkart.com | ✅ Implemented |

---

## Folder Structure

```
scraper/
├── main.py                  ← CLI entry point
├── requirements.txt         ← Python dependencies
├── README.md                ← This file
├── .env.example             ← Environment variable template
├── __init__.py
│
├── config/
│   ├── settings.py          ← All configurable constants
│   └── urls.py              ← Site-specific URL builders
│
├── drivers/                 ← ChromeDriver cache (auto-managed)
│
├── scrapers/
│   ├── base_scraper.py      ← Abstract base class + pipeline
│   ├── amazon_scraper.py    ← Amazon.in implementation
│   └── flipkart_scraper.py  ← Flipkart implementation
│
├── models/
│   ├── product.py           ← Product dataclass
│   └── review.py            ← Review dataclass
│
├── utils/
│   ├── browser.py           ← Chrome WebDriver factory
│   ├── cleaner.py           ← Data cleaning helpers
│   ├── logger.py            ← Logging setup
│   ├── helper.py            ← Retry decorator, ID generators, etc.
│   └── wait_utils.py        ← WebDriverWait wrappers
│
├── output/
│   ├── json/                ← products.json, reviews.json
│   └── csv/                 ← products.csv, reviews.csv
│
├── logs/                    ← scraper.log (auto-created)
│
└── tests/                   ← Unit tests
```

---

## Installation

### Prerequisites

- Python 3.12 or later
- Google Chrome browser installed
- Internet connection (ChromeDriver is auto-downloaded)

### Steps

```bash
# 1. Navigate to the scraper directory
cd scraper

# 2. Create and activate a virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy the environment template
copy .env.example .env     # Windows
cp .env.example .env       # macOS / Linux

# 5. Edit .env if you want to change any defaults (optional)
```

---

## Configuration

All settings live in `config/settings.py` and can be overridden via the `.env` file.

| Variable | Default | Description |
|---|---|---|
| `HEADLESS` | `true` | Run Chrome without a visible window |
| `INCOGNITO` | `true` | Use incognito/private mode |
| `MAX_PRODUCTS` | `10` | Products to scrape per keyword |
| `MAX_REVIEWS` | `50` | Reviews to collect per product |
| `MAX_SEARCH_PAGES` | `3` | Search result pages to paginate |
| `MAX_REVIEW_PAGES` | `5` | Review pages to paginate per product |
| `PAGE_TIMEOUT` | `20` | Seconds to wait for page elements |
| `SCROLL_PAUSE` | `1.5` | Pause between scroll steps (seconds) |
| `RETRY_ATTEMPTS` | `3` | Retry count on transient failures |
| `RETRY_DELAY` | `2.0` | Initial retry delay (exponential back-off) |
| `EXPORT_JSON` | `true` | Generate JSON output files |
| `EXPORT_CSV` | `true` | Generate CSV output files |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

---

## How to Run

All commands must be run from inside the `scraper/` directory.

```bash
# Basic usage
python main.py --site amazon --keyword "wireless earphones"

# Flipkart with limits
python main.py --site flipkart --keyword "laptop" --max-products 3 --max-reviews 20

# Visible browser (useful for debugging)
python main.py --site amazon --keyword "headphones" --no-headless

# Skip CSV export
python main.py --site amazon --keyword "speakers" --no-csv

# Custom output directory
python main.py --site flipkart --keyword "phone" --output-dir ./my_output

# Full help
python main.py --help
```

### Output on success

```
============================================================
SCRAPING COMPLETE
============================================================
{
  "site": "amazon",
  "products_scraped": 5,
  "reviews_scraped": 134,
  "elapsed_seconds": 47.3,
  "output_files": {
    "products_json": "...\\output\\json\\products.json",
    "reviews_json":  "...\\output\\json\\reviews.json",
    "products_csv":  "...\\output\\csv\\products.csv",
    "reviews_csv":   "...\\output\\csv\\reviews.csv"
  },
  "error": null,
  "completed_at": "2024-03-15T14:30:00+00:00"
}
============================================================
```

---

## Output Format

### `output/json/products.json`

```json
[
  {
    "product_id": "B0CH7RLKFC",
    "product_name": "Sony WH-1000XM5 Wireless Headphones",
    "brand": "Sony",
    "category": "Electronics > Headphones",
    "price": 26990.0,
    "discount_price": 22990.0,
    "overall_rating": 4.4,
    "num_ratings": 12450,
    "num_reviews": 3210,
    "description": "Industry-leading noise cancellation | ...",
    "availability": "In Stock",
    "image_url": "https://m.media-amazon.com/images/...",
    "product_url": "https://www.amazon.in/dp/B0CH7RLKFC",
    "source": "amazon",
    "scraped_at": "2024-03-15T14:30:00+00:00"
  }
]
```

### `output/json/reviews.json`

```json
[
  {
    "review_id": "A1B2C3D4E5F6G7H8",
    "product_id": "B0CH7RLKFC",
    "review_title": "Amazing noise cancellation!",
    "review_text": "I have been using these for 3 months now...",
    "star_rating": 5.0,
    "reviewer_name": "Rahul S.",
    "verified_purchase": true,
    "review_date": "2024-02-20",
    "helpful_votes": 42,
    "source": "amazon",
    "scraped_at": "2024-03-15T14:30:00+00:00",
    "sentiment": null
  }
]
```

> **Note for Sentiment Analysis Team**: The `sentiment` field is always `null` in scraper output. Your pipeline should update this field with the classification result.

---

## Logging

Logs are written to `logs/scraper.log` and also printed to the console with colour coding.

```
2024-03-15 14:28:01 | INFO     | scraper        | Scraper started | site=AMAZON | keyword='wireless earphones'
2024-03-15 14:28:03 | INFO     | scraper.amazon | Browser initialised successfully.
2024-03-15 14:28:08 | INFO     | scraper.amazon | Amazon search results loaded for: 'wireless earphones'
2024-03-15 14:28:09 | INFO     | scraper.amazon | Collected 10 product link(s) from Amazon.
2024-03-15 14:28:15 | INFO     | scraper.amazon | Product found: 'Sony WH-1000XM5' (ID: B0CH7RLKFC)
2024-03-15 14:28:34 | INFO     | scraper.amazon | Total reviews extracted for B0CH7RLKFC: 50
2024-03-15 14:30:02 | INFO     | scraper        | Scraper completed | products=5 | reviews=134 | elapsed=47.3s
```

---

## Architecture Overview

```
main.py
  └── AmazonScraper / FlipkartScraper
        └── BaseScraper (pipeline orchestration)
              ├── utils/browser.py   (WebDriver creation)
              ├── utils/wait_utils.py (explicit waits)
              ├── utils/cleaner.py   (data cleaning)
              ├── utils/helper.py    (retry, IDs, validation)
              ├── models/product.py  (Product dataclass)
              └── models/review.py   (Review dataclass)
```

The `BaseScraper.run()` method orchestrates the full pipeline.
Site-specific scrapers only implement four abstract methods:
`search_product`, `collect_product_links`, `scrape_product`, `scrape_reviews`.

---

## Adding a New Website

1. Create `scrapers/new_site_scraper.py` inheriting from `BaseScraper`.
2. Set `SITE = "new_site"` as a class attribute.
3. Implement the four abstract methods.
4. Register a URL builder in `config/urls.py`.
5. Add the import in `main.py`'s `_get_scraper()` function.

---

## Running Tests

```bash
# From inside scraper/
python -m pytest tests/ -v

# With coverage report
python -m pytest tests/ --cov=. --cov-report=term-missing
```

---

## Known Limitations

- **CAPTCHA / Bot detection**: Amazon and Flipkart actively detect automated browsers. Headless Chrome may be blocked after repeated requests. Using `--no-headless` with a slower scroll pace reduces detection. Adding residential proxy support would further mitigate this.
- **DOM changes**: E-commerce websites frequently update their HTML structure. If selectors break, update the `_SEL_*` constants at the top of each scraper class.
- **Dynamic login walls**: Flipkart sometimes requires login to view all reviews. The scraper dismisses the popup but cannot log in.
- **Review pagination limits**: Enforced by `MAX_REVIEW_PAGES` to avoid excessive run times. Increase in `.env` if needed.
- **Rate limiting**: No proxy rotation is implemented. Running with a small delay between requests (`SCROLL_PAUSE`) helps but does not eliminate throttling.
- **Images**: Only the primary product image URL is captured. Gallery images are not collected.

---

## Future Improvements

- [ ] Add proxy rotation support to bypass IP-based rate limiting.
- [ ] Implement cookie/session persistence to avoid re-solving CAPTCHAs.
- [ ] Add Playwright as an alternative browser backend for better stealth.
- [ ] Support Meesho, Myntra, and Snapdeal scrapers.
- [ ] Implement incremental scraping (skip already-scraped products).
- [ ] Add a scheduling mechanism for periodic data refresh.
- [ ] Expose a REST API endpoint so the backend can trigger scraping on demand.
- [ ] Add async/concurrent scraping for faster execution.
