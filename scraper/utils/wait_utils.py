"""
wait_utils.py – Selenium WebDriverWait helpers.

All waiting and scrolling logic lives here so individual scrapers stay
focused on selectors and business logic rather than timing.

Usage::

    from utils.wait_utils import wait_for_element, scroll_to_bottom
"""

from __future__ import annotations

import time
from typing import Any

from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


def wait_for_element(
    driver: WebDriver,
    locator: tuple[str, str],
    timeout: int = settings.PAGE_TIMEOUT,
) -> WebElement | None:
    """Wait until a single element matching *locator* is visible.

    Args:
        driver:  Active WebDriver instance.
        locator: ``(By.X, 'selector')`` tuple.
        timeout: Seconds before giving up (default: ``PAGE_TIMEOUT``).

    Returns:
        The :class:`WebElement` if found, otherwise ``None``.
    """
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )
        return element
    except TimeoutException:
        logger.debug("Timeout waiting for element %s", locator)
        return None


def wait_for_elements(
    driver: WebDriver,
    locator: tuple[str, str],
    timeout: int = settings.PAGE_TIMEOUT,
) -> list[WebElement]:
    """Wait until at least one element matching *locator* is visible.

    Args:
        driver:  Active WebDriver instance.
        locator: ``(By.X, 'selector')`` tuple.
        timeout: Seconds before giving up.

    Returns:
        List of :class:`WebElement` objects (may be empty on timeout).
    """
    try:
        WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )
        return driver.find_elements(*locator)
    except TimeoutException:
        logger.debug("Timeout waiting for elements %s", locator)
        return []


def wait_for_clickable(
    driver: WebDriver,
    locator: tuple[str, str],
    timeout: int = settings.PAGE_TIMEOUT,
) -> WebElement | None:
    """Wait until an element is clickable.

    Args:
        driver:  Active WebDriver instance.
        locator: ``(By.X, 'selector')`` tuple.
        timeout: Seconds before giving up.

    Returns:
        Clickable :class:`WebElement` or ``None`` on timeout.
    """
    try:
        return WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable(locator)
        )
    except TimeoutException:
        logger.debug("Timeout waiting for clickable element %s", locator)
        return None


def safe_click(driver: WebDriver, element: WebElement) -> bool:
    """Click *element*, falling back to a JavaScript click on failure.

    Args:
        driver:  Active WebDriver instance.
        element: The element to click.

    Returns:
        ``True`` if click succeeded, ``False`` otherwise.
    """
    try:
        element.click()
        return True
    except Exception:  # pylint: disable=broad-except
        try:
            driver.execute_script("arguments[0].click();", element)
            return True
        except Exception as exc:  # pylint: disable=broad-except
            logger.warning("safe_click failed: %s", exc)
            return False


def scroll_to_bottom(
    driver: WebDriver,
    pause: float = settings.SCROLL_PAUSE,
    max_scrolls: int = 20,
) -> None:
    """Scroll to the page bottom, handling infinite-scroll pages.

    Scrolls incrementally and stops when no further content loads.

    Args:
        driver:      Active WebDriver instance.
        pause:       Seconds to pause between scroll steps.
        max_scrolls: Safety cap to prevent infinite loops.
    """
    last_height = driver.execute_script("return document.body.scrollHeight")
    scroll_count = 0

    while scroll_count < max_scrolls:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            logger.debug("Reached page bottom after %d scroll(s).", scroll_count + 1)
            break
        last_height = new_height
        scroll_count += 1


def scroll_to_element(driver: WebDriver, element: WebElement) -> None:
    """Scroll *element* into the visible viewport.

    Args:
        driver:  Active WebDriver instance.
        element: Target element.
    """
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)


def click_load_more(
    driver: WebDriver,
    css_selector: str,
    max_clicks: int = 10,
    pause: float = settings.SCROLL_PAUSE,
) -> int:
    """Repeatedly click a 'Load More' / 'Show More' button.

    Args:
        driver:       Active WebDriver instance.
        css_selector: CSS selector targeting the button.
        max_clicks:   Maximum number of clicks before stopping.
        pause:        Seconds to wait after each click.

    Returns:
        Number of times the button was successfully clicked.
    """
    clicks = 0
    while clicks < max_clicks:
        button = wait_for_clickable(
            driver, (By.CSS_SELECTOR, css_selector), timeout=5
        )
        if button is None:
            logger.debug(
                "'Load More' button (%s) not found after %d click(s).",
                css_selector,
                clicks,
            )
            break
        scroll_to_element(driver, button)
        if not safe_click(driver, button):
            break
        clicks += 1
        time.sleep(pause)

    return clicks


def dismiss_popup(
    driver: WebDriver,
    close_locator: tuple[str, str],
    timeout: int = 5,
) -> bool:
    """Attempt to close a modal/popup by clicking its close element.

    Args:
        driver:        Active WebDriver instance.
        close_locator: Locator for the close button/link.
        timeout:       Seconds to wait for popup.

    Returns:
        ``True`` if popup was dismissed, ``False`` otherwise.
    """
    element = wait_for_clickable(driver, close_locator, timeout=timeout)
    if element:
        safe_click(driver, element)
        logger.debug("Popup dismissed via %s", close_locator)
        return True
    return False


def get_text_safe(element: WebElement | None, default: str = "") -> str:
    """Return the visible text of *element*, or *default* if None/stale.

    Args:
        element: A :class:`WebElement` or ``None``.
        default: Fallback string.

    Returns:
        Stripped text string.
    """
    if element is None:
        return default
    try:
        return element.text.strip()
    except StaleElementReferenceException:
        return default


def get_attribute_safe(
    element: WebElement | None, attr: str, default: str = ""
) -> str:
    """Return an attribute value from *element*, or *default* on failure.

    Args:
        element: A :class:`WebElement` or ``None``.
        attr:    HTML attribute name (e.g. ``'href'``).
        default: Fallback string.

    Returns:
        Attribute value string.
    """
    if element is None:
        return default
    try:
        value = element.get_attribute(attr)
        return value.strip() if value else default
    except StaleElementReferenceException:
        return default
