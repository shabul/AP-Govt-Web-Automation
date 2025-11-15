from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv

def setup_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--user-data-dir=chrome-profile')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--window-size=1920,1080')
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def wait_for_page_ready(driver, wait, spinner_xpath="//div[contains(@class, 'loading') or contains(@class, 'spinner')]"):
    try:
        print("Checking for loading spinner...")
        wait.until_not(EC.presence_of_element_located((By.XPATH, spinner_xpath)))
        print("No loading spinner detected. Page is ready.")
    except Exception:
        print("No spinner found or already gone.")

def login(driver, username, password):
    try:
        driver.get("https://vswsonline.ap.gov.in/#/home")
        input("Please log in manually, then press Enter to continue automation...")
        print("Continuing automation after manual login.")
        return True
    except Exception as e:
        import traceback
        print(f"An error occurred during login: {str(e)}")
        traceback.print_exc()
        return False

def check_table_for_id(driver, csv_path):
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
        results = []
        for idx, row in enumerate(rows):
            # if idx == 0:
            #     print("Skipping first row.")
            #     continue
            # if row['Status'].lower() == 'available':
            #     print(f"Row {idx+1}: Status is 'Available'. Skipping.")
            #     results.append({'Request ID': row[''], 'Status': 'Already Available'})
            #     continue
            try:
                app_id = row['Request ID']
                wait = WebDriverWait(driver, 30)
                print("Waiting for search input to appear before entering Application ID...")
                search_input = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/app-root/div/div/div/app-common-dashboard/div/div/div[2]/input")))
                print("Search input is ready.")
                search_input.clear()
                print(f"Entering Application ID: {app_id}")
                search_input.send_keys(app_id)
                search_input.send_keys(u"\ue007")
                time.sleep(2)
                # Check if table has results for Application ID
                try:
                    status_cell = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/app-root/div/div/div/app-common-dashboard/div/div/div[2]/div[1]/table/tbody/tr/td")))
                    status_text = status_cell.text.strip()
                    print(f"Status cell text: {status_text}")
                    if status_text == "No requests are pending.":
                        print(f"Application ID {app_id}: No requests are pending. Skipping to next record.")
                        result = {'Application ID': app_id, 'Status': 'Not Available'}
                    else:
                        print(f"Application ID {app_id}: Found in table.")
                        result = {'Application ID': app_id, 'Status': 'Available'}
                except Exception as e:
                    print(f"Status cell not found or error: {e}")
                    result = {'Application ID': app_id, 'Status': f'Failed: {e}'}
            except Exception as e:
                print(f"Error processing row {idx+1}: {e}")
                result = {'Application ID': row.get('Application ID', f'Row {idx+1}'), 'Status': f'Failed: {e}'}
            results.append(result)
        # Write results to a new CSV file
        with open('ID_check_results.csv', 'w', newline='', encoding='utf-8') as resultfile:
            fieldnames = ['Application ID', 'Status']
            writer = csv.DictWriter(resultfile, fieldnames=fieldnames)
            writer.writeheader()
            for r in results:
                writer.writerow(r)
        print("Results written to ID_check_results.csv")

def main():
    username = "10690231-vro@apgsws.onmicrosoft.com"
    password = "Vro@pola123"
    driver = setup_driver()
    try:
        success = login(driver, username, password)
        if success:
            check_table_for_id(driver, "/Users/ey/Documents/Rahet_work/Sep-3-VRO/4-oct/Data_oct_4.csv")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
