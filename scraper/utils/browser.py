"""
browser.py – Chrome WebDriver factory.

Centralises all browser configuration so that every scraper gets a
consistent, fingerprint-resistant Chrome instance with a single call.

Usage::

    from utils.browser import create_driver
    driver = create_driver()
"""

from __future__ import annotations

import logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


def _build_chrome_options() -> Options:
    """Assemble and return a configured :class:`Options` object.

    Applies:
    * Headless mode (configurable).
    * Incognito / private mode.
    * Custom User-Agent.
    * Window size.
    * Several anti-bot-detection flags.

    Returns:
        :class:`selenium.webdriver.chrome.options.Options`
    """
    options = Options()

    if settings.HEADLESS:
        # New headless flag supported since Chrome 112
        options.add_argument("--headless=new")
        logger.debug("Chrome headless mode: ON")
    else:
        logger.debug("Chrome headless mode: OFF")

    if settings.INCOGNITO:
        options.add_argument("--incognito")

    # Window size
    options.add_argument(
        f"--window-size={settings.WINDOW_WIDTH},{settings.WINDOW_HEIGHT}"
    )

    # Custom User-Agent
    options.add_argument(f"--user-agent={settings.USER_AGENT}")

    # Stability / sandbox flags (important in CI / Docker environments)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    # Anti-detection flags
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # Disable image loading to speed up scraping (optional performance tweak)
    prefs = {
        "profile.managed_default_content_settings.images": 1,  # 2 = disable
        "profile.default_content_setting_values.notifications": 2,
    }
    options.add_experimental_option("prefs", prefs)

    # Suppress verbose Chrome logging to stdout
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    return options


def create_driver() -> webdriver.Chrome:
    """Create, configure, and return a Chrome WebDriver instance.

    Automatically downloads and caches the correct ChromeDriver binary via
    ``webdriver-manager``.  Sets implicit waits and injects JavaScript to
    mask the ``navigator.webdriver`` property.

    Returns:
        A ready-to-use :class:`selenium.webdriver.Chrome` instance.

    Raises:
        RuntimeError: If the driver cannot be initialised after setup.
    """
    logger.info("Initialising Chrome WebDriver …")

    options = _build_chrome_options()

    service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(service=service, options=options)

    # Fallback implicit wait (explicit waits take priority)
    driver.implicitly_wait(settings.IMPLICIT_WAIT)

    # Mask navigator.webdriver to reduce bot-detection probability
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """
        },
    )

    logger.info(
        "Chrome WebDriver ready | headless=%s | window=%sx%s",
        settings.HEADLESS,
        settings.WINDOW_WIDTH,
        settings.WINDOW_HEIGHT,
    )
    return driver


def quit_driver(driver: webdriver.Chrome | None) -> None:
    """Safely quit the WebDriver, ignoring errors if already closed.

    Args:
        driver: The WebDriver instance to quit (may be ``None``).
    """
    if driver is None:
        return
    try:
        driver.quit()
        logger.info("Chrome WebDriver closed successfully.")
    except Exception as exc:  # pylint: disable=broad-except
        logger.warning("Error while closing WebDriver: %s", exc)
