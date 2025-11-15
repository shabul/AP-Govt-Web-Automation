from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

import pandas as pd
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


@dataclass
class DashboardSelectors:
    search_input: str = "/html/body/app-root/div/div/div/app-common-dashboard/div/div/div[2]/input"
    no_requests_cell: str = "/html/body/app-root/div/div/div/app-common-dashboard/div/div/div[2]/div/table/tbody/tr/td"
    result_cell: str = "/html/body/app-root/div/div/div/app-common-dashboard/div/div/div[2]/div[1]/table/tbody/tr/td[2]"
    phone_field: str = (
        "/html/body/app-root/div/div/div/app-common-dashboard/div/div/div[4]/form[1]/"
        "app-common-form-view/div[1]/div[2]/div[3]/div[2]/div"
    )
    ration_field: str = (
        "/html/body/app-root/div/div/div/app-common-dashboard/div/div/div[4]/form[1]/"
        "app-integrated-certificate-view/div[2]/div[2]/div[1]/div[1]/div"
    )


@dataclass
class RequestDetails:
    request_id: str
    phone_number: str
    ration_card: str
    status: str


class DashboardScraper:
    """Encapsulates dashboard scraping logic."""

    def __init__(self, driver: WebDriver, *, wait_seconds: int = 30, selectors: DashboardSelectors | None = None) -> None:
        self.driver = driver
        self.wait = WebDriverWait(driver, wait_seconds)
        self.selectors = selectors or DashboardSelectors()

    def fetch_request(self, request_id: str) -> RequestDetails:
        """Return phone and ration details for a single request id."""

        search_box = self.wait.until(EC.presence_of_element_located((By.XPATH, self.selectors.search_input)))
        search_box.clear()
        search_box.send_keys(request_id)
        search_box.send_keys(u"\ue007")

        status = self._lookup_status()
        if status == "No requests are pending.":
            return RequestDetails(request_id, "", "", "not_found")

        result_cell = self.wait.until(EC.element_to_be_clickable((By.XPATH, self.selectors.result_cell)))
        result_cell.click()

        phone = self._safe_get_text(self.selectors.phone_field) or ""
        ration = self._safe_get_text(self.selectors.ration_field) or ""

        self.driver.execute_script("window.scrollTo(0, 0);")
        return RequestDetails(request_id, phone, ration, "success")

    def scrape_dataframe(
        self,
        df: pd.DataFrame,
        *,
        id_column: str = "Request ID",
        phone_column: str = "Phone Number",
        ration_column: str = "Ration Card Number",
        skip_ids: Optional[set[str]] = None,
    ) -> pd.DataFrame:
        """
        Iterate over Request IDs from the dataframe and populate the phone/ration columns.
        """

        updated = df.copy()
        if phone_column not in updated.columns:
            updated[phone_column] = ""
        if ration_column not in updated.columns:
            updated[ration_column] = ""

        for index, raw_value in updated[id_column].items():
            if pd.isna(raw_value):
                continue
            request_id = str(raw_value).strip()
            if not request_id:
                continue
            if skip_ids and request_id in skip_ids:
                continue

            try:
                details = self.fetch_request(request_id)
                updated.at[index, phone_column] = details.phone_number
                updated.at[index, ration_column] = details.ration_card
                updated.at[index, "Status"] = details.status
            except Exception as exc:  # pylint: disable=broad-except
                updated.at[index, "Status"] = f"failed: {exc}"

        return updated

    def _lookup_status(self) -> str:
        try:
            cell = self.wait.until(EC.presence_of_element_located((By.XPATH, self.selectors.no_requests_cell)))
            return cell.text.strip()
        except TimeoutException:
            return ""

    def _safe_get_text(self, xpath: str) -> str:
        try:
            return self.wait.until(EC.presence_of_element_located((By.XPATH, xpath))).text.strip()
        except TimeoutException:
            return ""
