from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


WINDOW_SIZE = (1920, 1080)


def create_chrome_driver(
    user_data_dir: Optional[Path] = None,
    *,
    headless: bool = False,
    window_size: Tuple[int, int] = WINDOW_SIZE,
) -> webdriver.Chrome:
    """
    Construct a Chrome WebDriver instance with safe defaults.

    The driver manager automatically installs the matching ChromeDriver.
    """

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument(f"--window-size={window_size[0]},{window_size[1]}")
    if headless:
        chrome_options.add_argument("--headless=new")
    if user_data_dir:
        chrome_options.add_argument(f"--user-data-dir={str(user_data_dir)}")

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)
