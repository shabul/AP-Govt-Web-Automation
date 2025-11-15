# Rahet Work - Automation Project

This project contains web automation scripts for data collection and verification tasks.

## Project Structure

- **31_Aug/**: Initial automation scripts and data processing
  - `vro_login_automation.py`: VRO portal login automation
  - `data_scraper.py`: Dashboard data scraping
  - `data_processing.py`: Data combination and deduplication
  - Excel files with processed records

- **Sep-3-VRO/**: VRO (Village Revenue Officer) automation
  - `vro_login_automation.py`: VRO portal login
  - `table_verification.py`: Table data verification
  - `Source-Data.csv`: Sanitized source data
  - `ID_check_results.csv`: ID verification results
  - `4-oct/`: October 4th data and analysis

- **Sep-5_RI/**: RI (Revenue Inspector) automation
  - `ri_login_automation.py`: RI portal login
  - `table_verification.py`: Table data verification
  - `Source-Data.csv`: Sanitized source data
  - `ID_check_results.csv`: ID verification results
  - `4-oct/`: October 4th data and analysis

## Features

- Automated login to government portals
- Web scraping and data extraction
- Data validation and verification
- CSV/Excel data processing
- Duplicate record detection

## Data Privacy

All sensitive personal information (names, phone numbers, addresses) has been removed from CSV and Excel files to protect privacy.

## Usage

Each folder contains independent automation scripts. Ensure you have the required dependencies installed:

```bash
pip install selenium pandas openpyxl
```

## Notes

- Scripts use Selenium for browser automation
- Chrome profiles are used for session management
- Data files are sanitized for privacy compliance
