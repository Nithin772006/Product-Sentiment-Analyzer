#!/usr/bin/env python3
"""
main.py – CLI entry point for the Product Sentiment Analyzer scraper.

Run from inside the scraper/ directory:

    python main.py --site amazon --keyword "wireless earphones"
    python main.py --site flipkart --keyword "laptop" --max-products 3
    python main.py --site amazon --keyword "headphones" --no-headless

Use --help for a full list of options.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Ensure scraper/ is on the Python path regardless of working directory
_SCRAPER_ROOT = Path(__file__).resolve().parent
if str(_SCRAPER_ROOT) not in sys.path:
    sys.path.insert(0, str(_SCRAPER_ROOT))

from config import settings
from config.urls import SUPPORTED_SITES
from utils.logger import setup_logger

logger = setup_logger("scraper")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse and validate command-line arguments.

    Args:
        argv: Argument list (defaults to ``sys.argv[1:]``).

    Returns:
        Parsed :class:`argparse.Namespace`.
    """
    parser = argparse.ArgumentParser(
        prog="main.py",
        description=(
            "Product Sentiment Analyzer – Web Scraping Module\n"
            "Scrapes product info and reviews from supported e-commerce sites."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python main.py --site amazon --keyword \"wireless earphones\"\n"
            "  python main.py --site flipkart --keyword \"laptop\" "
            "--max-products 3 --max-reviews 20\n"
            "  python main.py --site amazon --keyword \"headphones\" --no-headless\n"
        ),
    )

    parser.add_argument(
        "--site",
        required=True,
        choices=SUPPORTED_SITES,
        metavar="SITE",
        help=f"E-commerce site to scrape. Supported: {', '.join(SUPPORTED_SITES)}",
    )

    parser.add_argument(
        "--keyword",
        required=True,
        metavar="KEYWORD",
        help="Product search keyword (e.g. 'wireless earphones')",
    )

    parser.add_argument(
        "--max-products",
        type=int,
        default=settings.MAX_PRODUCTS,
        metavar="N",
        help=f"Maximum number of products to scrape (default: {settings.MAX_PRODUCTS})",
    )

    parser.add_argument(
        "--max-reviews",
        type=int,
        default=settings.MAX_REVIEWS,
        metavar="N",
        help=f"Maximum reviews per product (default: {settings.MAX_REVIEWS})",
    )

    parser.add_argument(
        "--no-headless",
        action="store_true",
        default=False,
        help="Open a visible browser window instead of running headless",
    )

    parser.add_argument(
        "--no-json",
        action="store_true",
        default=False,
        help="Skip JSON export",
    )

    parser.add_argument(
        "--no-csv",
        action="store_true",
        default=False,
        help="Skip CSV export",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        metavar="PATH",
        help="Override the default output directory",
    )

    return parser.parse_args(argv)


def _apply_cli_overrides(args: argparse.Namespace) -> None:
    """Apply CLI flag overrides to the live settings module.

    This mutates the settings module in place so that all downstream code
    (browser, scrapers, etc.) picks up the values without needing to be
    passed arguments.

    Args:
        args: Parsed CLI arguments.
    """
    if args.no_headless:
        settings.HEADLESS = False
        logger.info("Headless mode disabled via --no-headless flag.")

    if args.no_json:
        settings.EXPORT_JSON = False

    if args.no_csv:
        settings.EXPORT_CSV = False

    if args.output_dir:
        settings.JSON_OUTPUT_DIR = args.output_dir / "json"
        settings.CSV_OUTPUT_DIR = args.output_dir / "csv"
        settings.PRODUCTS_JSON_FILE = settings.JSON_OUTPUT_DIR / "products.json"
        settings.REVIEWS_JSON_FILE = settings.JSON_OUTPUT_DIR / "reviews.json"
        settings.PRODUCTS_CSV_FILE = settings.CSV_OUTPUT_DIR / "products.csv"
        settings.REVIEWS_CSV_FILE = settings.CSV_OUTPUT_DIR / "reviews.csv"
        settings.JSON_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        settings.CSV_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        logger.info("Output directory overridden to: %s", args.output_dir)


def _get_scraper(site: str):
    """Instantiate and return the correct scraper for *site*.

    Args:
        site: Site identifier string (e.g. ``'amazon'``).

    Returns:
        An instance of a :class:`~scrapers.base_scraper.BaseScraper` subclass.

    Raises:
        SystemExit: If *site* is not supported.
    """
    if site == "amazon":
        from scrapers.amazon_scraper import AmazonScraper
        return AmazonScraper()
    elif site == "flipkart":
        from scrapers.flipkart_scraper import FlipkartScraper
        return FlipkartScraper()
    else:
        logger.critical("Unsupported site: '%s'", site)
        sys.exit(1)


def main(argv: list[str] | None = None) -> int:
    """Main entry point.

    Args:
        argv: Optional argument list for testing. Defaults to ``sys.argv``.

    Returns:
        Exit code: 0 = success, 1 = failure.
    """
    args = parse_args(argv)

    logger.info("=" * 60)
    logger.info("Product Sentiment Analyzer – Scraper Module")
    logger.info("Site: %s | Keyword: '%s'", args.site.upper(), args.keyword)
    logger.info("Max products: %d | Max reviews: %d", args.max_products, args.max_reviews)
    logger.info("=" * 60)

    _apply_cli_overrides(args)

    scraper = _get_scraper(args.site)

    summary = scraper.run(
        keyword=args.keyword,
        max_products=args.max_products,
        max_reviews=args.max_reviews,
    )

    # Print summary to console
    print("\n" + "=" * 60)
    print("SCRAPING COMPLETE")
    print("=" * 60)
    print(json.dumps(summary, indent=2, default=str))
    print("=" * 60 + "\n")

    if summary.get("error"):
        logger.error("Scraper finished with error: %s", summary["error"])
        return 1

    if summary["products_scraped"] == 0:
        logger.warning("No products were scraped.")
        return 1

    logger.info(
        "Successfully scraped %d product(s) and %d review(s).",
        summary["products_scraped"],
        summary["reviews_scraped"],
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
