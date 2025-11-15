from __future__ import annotations

from pathlib import Path
from typing import Iterable, Set

import pandas as pd


def load_request_ids(
    excel_path: Path,
    *,
    column: str = "Request ID",
    skip_rows: int = 0,
    blacklist: Iterable[str] | None = None,
) -> list[str]:
    """Return sanitized request IDs from an Excel file."""

    frame = pd.read_excel(excel_path, skiprows=skip_rows)
    blacklist_set = {str(value).strip() for value in blacklist or []}
    request_ids: list[str] = []
    for value in frame[column].dropna():
        request_id = str(value).strip()
        if not request_id or request_id in {"NA", "na"}:
            continue
        if blacklist_set and request_id in blacklist_set:
            continue
        request_ids.append(request_id)
    return request_ids


def load_processed_ids(excel_path: Path, *, column: str = "Request ID") -> Set[str]:
    """Read already processed IDs so we do not scrape them again."""

    frame = pd.read_excel(excel_path)
    processed = set()
    for value in frame[column].dropna():
        processed.add(str(value).strip())
    return processed


def merge_excel_files(
    first_path: Path,
    second_path: Path,
    output_path: Path,
    *,
    unique_column: str = "Request ID",
    preferred_column: str = "Ration Card Number",
) -> pd.DataFrame:
    """
    Merge two Excel files by the request id, preferring rows that include ration card data.
    """

    first_df = pd.read_excel(first_path)
    second_df = pd.read_excel(second_path)
    combined = pd.concat([first_df, second_df], ignore_index=True)
    combined = combined.sort_values(
        by=[unique_column, preferred_column],
        ascending=[True, False],
        na_position="last",
    )
    deduped = combined.drop_duplicates(subset=[unique_column], keep="first")
    deduped.to_excel(output_path, index=False)
    return deduped
