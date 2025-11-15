# Andhra Pradesh Certificate Automation

This repository automates the Andhra Pradesh *Caste/Income* certificate workflow across VRO, RI, and MRO logins.  A single flat toolkit handles portal sign-in, dashboard scraping, table verification, and Excel clean‑ups so every field unit (Village Revenue Officer, Revenue Inspector, Mandal Revenue Officer) can reuse the same scripts with different data inputs.

- `automation.py` – command line entry point for all tasks
- `browser.py`, `portal.py`, `dashboard_scraper.py`, `table_verifier.py`, `data_tools.py`, `config.py` – shared helpers to keep the code readable and testable
- `legacy/` – archived notebooks and experimental files from the earlier workflow (kept for reference only)

## Features

- Manual or automated login to the AP MeeSeva portal with optional Chrome profile reuse
- Request ID scraping to pull applicant phone numbers and ration cards
- Dashboard verification to mark which IDs are still pending for VRO/RI/MRO teams
- Excel utilities to merge data exports and remove duplicates while keeping the best record

## Quick start

1. Create/activate a virtual environment.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Export credentials (only needed when using `--auto-login`, manual login is the default):

   ```bash
   export PORTAL_USERNAME="vro.user@ap.gov.in"
   export PORTAL_PASSWORD="super-secret"
   ```

4. Run the CLI with the scenario you need:

   ```bash
   # VRO or RI scrape to enrich a sheet with phone + ration data
   python automation.py scrape \
       --source data/Last_Sumoto.xlsx \
       --output data/with_contacts.xlsx \
       --processed data/already_done.xlsx

   # Dashboard verification for RI/MRO teams
   python automation.py verify \
       --source data/ids.csv \
       --output data/verification.csv \
       --status-column "Dashboard Status"

   # Merge two certificate export files and deduplicate on Request ID
   python automation.py merge \
       --first data/pola.xlsx \
       --second data/476_records.xlsx \
       --output data/combined.xlsx
   ```

### Helpful flags

- `--chrome-profile /path/to/profile` keeps a signed‑in session for all three roles (VRO/RI/MRO).
- `--headless` runs Chrome invisibly on servers.
- `--auto-login` pulls credentials from `PORTAL_USERNAME`/`PORTAL_PASSWORD`.
- `--wait-seconds` fine tunes Selenium waits (default 30 seconds).

## Notes

- All sensitive beneficiary data remains outside the repo; sample file names above are placeholders.
- Legacy folders are untouched but no longer part of the active workflow—everything runs from the repository root.
