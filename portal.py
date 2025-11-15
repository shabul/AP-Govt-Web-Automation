from __future__ import annotations

from dataclasses import dataclass

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import PortalConfig


@dataclass
class PortalSession:
    """High level helper for logging in and navigating within the portal."""

    driver: WebDriver
    config: PortalConfig

    def __post_init__(self) -> None:
        self.wait = WebDriverWait(self.driver, self.config.wait_seconds)

    def login(self, *, manual: bool = True, username: str | None = None, password: str | None = None) -> None:
        """
        Login handler.

        Manual login keeps MFA/CAPTCHA handling outside the automation.  Automated login
        can still be used for test environments where the flow is deterministic.
        """

        self.driver.get(self.config.home_url)
        if manual:
            input("Complete the login in the browser window, then press Enter to continue...")
            return
        if not username or not password:
            raise ValueError("Username and password are required for automated login.")

        login_menu = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "/html/body/app-root/div/app-home/div/app-home-header/header/section/div/div/div/div[7]/div/ul/li/a")
            )
        )
        login_menu.click()
        employee_login = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "/html/body/app-root/div/app-home/div/app-home-header/header/section/div/div/div/div[7]/div/ul/li/ul/li[2]/a")
            )
        )
        employee_login.click()

        username_field = self.wait.until(EC.presence_of_element_located((By.NAME, "loginfmt")))
        username_field.send_keys(username)
        username_field.send_keys(u"\ue007")  # Enter

        password_field = self.wait.until(EC.presence_of_element_located((By.NAME, "passwd")))
        password_field.send_keys(password)
        password_field.send_keys(u"\ue007")

    def open_dashboard(self) -> None:
        """Navigate to the dashboard view used by the automation workflows."""

        self.driver.get(self.config.dashboard_url)
