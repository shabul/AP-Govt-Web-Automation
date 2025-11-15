from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from browser import create_chrome_driver
from config import PortalConfig, resolve_profile
from data_tools import load_processed_ids, merge_excel_files
from dashboard_scraper import DashboardScraper
from portal import PortalSession
from table_verifier import TableVerifier


def main() -> None:
    parser = argparse.ArgumentParser(description="Unified automation toolkit for AP certificate workflows.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Shared driver args
    def add_driver_arguments(subparser: argparse.ArgumentParser) -> None:
        default_config = PortalConfig()
        subparser.add_argument("--home-url", default=default_config.home_url, help="Landing URL for the portal.")
        subparser.add_argument("--dashboard-url", default=default_config.dashboard_url, help="Dashboard URL.")
        subparser.add_argument("--chrome-profile", help="Path to a Chrome profile for session reuse.")
        subparser.add_argument("--headless", action="store_true", help="Run Chrome in headless mode.")
        subparser.add_argument("--wait-seconds", type=int, default=default_config.wait_seconds, help="WebDriver wait timeout.")
        subparser.add_argument(
            "--auto-login",
            action="store_true",
            help="Attempt automated login using environment credentials (default is manual login).",
        )

    # Scrape command
    scrape = subparsers.add_parser("scrape", help="Fetch phone/ration numbers for request IDs.")
    add_driver_arguments(scrape)
    scrape.add_argument("--source", required=True, help="Excel file with request IDs.")
    scrape.add_argument("--output", required=True, help="Destination Excel file for the enriched data.")
    scrape.add_argument("--processed", help="Optional Excel file with already processed request IDs.")
    scrape.add_argument("--skip-rows", type=int, default=0, help="Number of header rows to skip when reading the source file.")
    scrape.add_argument("--id-column", default="Request ID", help="Name of the request id column.")
    scrape.add_argument("--phone-column", default="Phone Number", help="Column used to store phone numbers.")
    scrape.add_argument("--ration-column", default="Ration Card Number", help="Column used to store ration card numbers.")
    scrape.set_defaults(func=run_scrape)

    # Verify command
    verify = subparsers.add_parser("verify", help="Check whether request IDs are present in the dashboard table.")
    add_driver_arguments(verify)
    verify.add_argument("--source", required=True, help="CSV/Excel file that contains the request IDs.")
    verify.add_argument("--output", required=True, help="CSV/Excel target file for the verification results.")
    verify.add_argument("--id-column", default="Request ID")
    verify.add_argument("--status-column", default="Status")
    verify.set_defaults(func=run_verify)

    # Merge command
    merge = subparsers.add_parser("merge", help="Merge two Excel exports and deduplicate by request ID.")
    merge.add_argument("--first", required=True, help="Primary Excel file path.")
    merge.add_argument("--second", required=True, help="Secondary Excel file path.")
    merge.add_argument("--output", required=True, help="Destination Excel file.")
    merge.add_argument("--unique-column", default="Request ID")
    merge.add_argument("--preferred-column", default="Ration Card Number")
    merge.set_defaults(func=run_merge)

    args = parser.parse_args()
    args.func(args)


def run_scrape(args: argparse.Namespace) -> None:
    source_path = Path(args.source)
    output_path = Path(args.output)
    processed_ids = load_processed_ids(Path(args.processed), column=args.id_column) if args.processed else set()

    data_frame = pd.read_excel(source_path, skiprows=args.skip_rows)

    config = PortalConfig(
        home_url=args.home_url,
        dashboard_url=args.dashboard_url,
        chrome_profile=resolve_profile(args.chrome_profile) if args.chrome_profile else None,
        wait_seconds=args.wait_seconds,
    )
    username = password = None
    if args.auto_login:
        username, password = config.credentials()

    driver = create_chrome_driver(config.chrome_profile, headless=args.headless)
    session = PortalSession(driver, config)
    scraper = DashboardScraper(driver, wait_seconds=config.wait_seconds)

    try:
        session.login(manual=not args.auto_login, username=username, password=password)
        session.open_dashboard()
        result_df = scraper.scrape_dataframe(
            data_frame,
            id_column=args.id_column,
            phone_column=args.phone_column,
            ration_column=args.ration_column,
            skip_ids=processed_ids,
        )
    finally:
        driver.quit()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    result_df.to_excel(output_path, index=False)


def run_verify(args: argparse.Namespace) -> None:
    source_path = Path(args.source)
    output_path = Path(args.output)
    frame = read_table(source_path)

    config = PortalConfig(
        home_url=args.home_url,
        dashboard_url=args.dashboard_url,
        chrome_profile=resolve_profile(args.chrome_profile) if args.chrome_profile else None,
        wait_seconds=args.wait_seconds,
    )
    username = password = None
    if args.auto_login:
        username, password = config.credentials()

    driver = create_chrome_driver(config.chrome_profile, headless=args.headless)
    session = PortalSession(driver, config)
    verifier = TableVerifier(driver, wait_seconds=config.wait_seconds)

    try:
        session.login(manual=not args.auto_login, username=username, password=password)
        session.open_dashboard()
        result_df = verifier.verify_dataframe(frame, id_column=args.id_column, status_column=args.status_column)
    finally:
        driver.quit()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_table(result_df, output_path)


def run_merge(args: argparse.Namespace) -> None:
    first = Path(args.first)
    second = Path(args.second)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    merge_excel_files(
        first,
        second,
        output,
        unique_column=args.unique_column,
        preferred_column=args.preferred_column,
    )


def read_table(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    return pd.read_excel(path)


def write_table(df: pd.DataFrame, path: Path) -> None:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        df.to_csv(path, index=False)
    else:
        df.to_excel(path, index=False)


if __name__ == "__main__":
    main()
