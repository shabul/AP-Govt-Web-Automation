from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


@dataclass
class VerificationSelectors:
    search_input: str = "/html/body/app-root/div/div/div/app-common-dashboard/div/div/div[2]/input"
    status_cell: str = "/html/body/app-root/div/div/div/app-common-dashboard/div/div/div[2]/div[1]/table/tbody/tr/td"


@dataclass
class VerificationResult:
    request_id: str
    status: str


class TableVerifier:
    """Checks whether request IDs are present in the table."""

    def __init__(self, driver: WebDriver, *, wait_seconds: int = 30, selectors: VerificationSelectors | None = None) -> None:
        self.driver = driver
        self.wait = WebDriverWait(driver, wait_seconds)
        self.selectors = selectors or VerificationSelectors()

    def verify_request(self, request_id: str) -> VerificationResult:
        search_input = self.wait.until(EC.presence_of_element_located((By.XPATH, self.selectors.search_input)))
        search_input.clear()
        search_input.send_keys(request_id)
        search_input.send_keys(u"\ue007")

        status_cell = self.wait.until(EC.presence_of_element_located((By.XPATH, self.selectors.status_cell)))
        status_text = status_cell.text.strip()
        status = "available" if status_text != "No requests are pending." else "not_found"
        return VerificationResult(request_id, status)

    def verify_dataframe(
        self,
        df: pd.DataFrame,
        *,
        id_column: str = "Request ID",
        status_column: str = "Status",
    ) -> pd.DataFrame:
        updated = df.copy()
        if status_column not in updated.columns:
            updated[status_column] = ""

        for index, raw_value in updated[id_column].items():
            if pd.isna(raw_value):
                continue
            request_id = str(raw_value).strip()
            if not request_id:
                continue
            try:
                result = self.verify_request(request_id)
                updated.at[index, status_column] = result.status
            except Exception as exc:  # pylint: disable=broad-except
                updated.at[index, status_column] = f"failed: {exc}"
        return updated
