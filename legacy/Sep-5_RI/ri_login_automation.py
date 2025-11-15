from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv
import os
import pandas as pd

def setup_driver():
    # Set up Chrome options
    chrome_options = webdriver.ChromeOptions()
    # Use a persistent user data directory for session reuse
    chrome_options.add_argument('--user-data-dir=chrome-profile')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--window-size=1920,1080')
    # Add any additional options if needed
    # chrome_options.add_argument('--headless')  # Uncomment to run in headless mode

    # Initialize the Chrome WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def login(driver, username, password):
    try:
        # Navigate directly to the suomoto page using chrome profile
        driver.get("https://vswsonline.ap.gov.in/#/suomoto")
        print("Navigated to /#/suomoto page.")
        # Wait for a specific text to appear (change 'YourTextHere' to the actual text to check)
        wait = WebDriverWait(driver, 30)
        text_to_check = "Suomoto"  # Change this to the actual text you want to check for
        try:
            print(f"Looking for text '{text_to_check}' on the page...")
            body = wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            if text_to_check.lower() in body.text.lower():
                input(f"Text '{text_to_check}' found. Please complete any manual steps and press Enter to continue automation...")
                print("Continuing automation after user confirmation.")
            else:
                print(f"Text '{text_to_check}' not found, proceeding...")
        except Exception as e:
            print(f"Error or timeout looking for text: {e}. Proceeding...")
        return True
    except Exception as e:
        import traceback
        print(f"An error occurred during login: {str(e)}")
        traceback.print_exc()
        return False

def wait_for_page_ready(driver, wait, spinner_xpath="//div[contains(@class, 'loading') or contains(@class, 'spinner')]"):
    try:
        print("Checking for loading spinner...")
        wait.until_not(EC.presence_of_element_located((By.XPATH, spinner_xpath)))
        print("No loading spinner detected. Page is ready.")
    except Exception:
        print("No spinner found or already gone.")

def get_available_ids(results_csv):
    available_ids = set()
    with open(results_csv, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Status'].strip().lower() == 'available':
                available_ids.add(row['Application ID'].strip())
    return available_ids



remaining = '''SCGC2010016597680
SCGC2010016764988
SCGC2004012489364
SCGC2101010344069
SCGC2101010363483
SCGC2101010660575
SCGC2102010990146
SCGC2102010991193
SCGC2103011701937'''.split("\n")
def process_applications(driver, csv_path):
    # Track processed Application IDs in a CSV file
    processed_file = 'processed_ids.csv'
    processed_ids = set()
    try:
        import pandas as pd
        if os.path.exists(processed_file):
            df = pd.read_csv(processed_file)
            processed_ids = set(df['Request ID'].astype(str).str.strip())
            print(f"Loaded {len(processed_ids)} processed Application IDs from {processed_file}")
    except Exception as e:
        print(f"Error reading {processed_file}: {e}")
    available_ids = get_available_ids('ID_check_results.csv')
    print(f"Total available IDs: {len(available_ids)}")
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
        for idx, row in enumerate(rows):
            app_id = row['Request ID'].strip()
            if app_id not in remaining:
                print(f"Skipping Application ID {app_id}: In remaining list.")
                continue
            # --- SKIP CONDITIONS ---
            # if idx <=35:
            #     continue
            # if app_id in processed_ids:
            #     print(f"Skipping Application ID {app_id}: Already processed in previous runs.")
            #     continue
            # if idx = 100:
            #     print("Skipping first row.")
            #     continue
            # if app_id not in available_ids:
            #     print(f"Skipping Application ID {app_id}: Not marked as Available.")
            #     continue
            try:
                print(f"Processing Application ID: {app_id}")
                wait = WebDriverWait(driver, 3)
                print("Locating search input...")
                search_input = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/app-root/div/div/div/app-common-dashboard/div/div/div[2]/input")))
                print("Search input is ready.")
                search_input.clear()
                print(f"Entering Application ID: {app_id}")
                search_input.send_keys(app_id)
                search_input.send_keys(u"\ue007")
                time.sleep(2)
                print("Locating result cell...")
                result_cell = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/div/div/div/app-common-dashboard/div/div/div[2]/div[1]/table/tbody/tr/td[2]")))
                result_cell.click()
                time.sleep(1)

                # --- NEW LOGIC: Click two radio buttons ---
                try:
                    print("Clicking first radio button...")
                    radio1 = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/div/div/div/app-common-dashboard/div/div/div[4]/div[1]/div/div[3]/form/div[1]/div/input[1]")))
                    driver.execute_script("arguments[0].scrollIntoView();", radio1)
                    time.sleep(0.5)
                    radio1.click()
                    print("First radio button clicked.")
                except Exception as e:
                    print(f"Error clicking first radio button: {e}")
                try:
                    print("Clicking second radio button...")
                    radio2 = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/div/div/div/app-common-dashboard/div/div/div[4]/div[1]/div/div[3]/form/div[2]/div/input[1]")))
                    driver.execute_script("arguments[0].scrollIntoView();", radio2)
                    time.sleep(0.5)
                    radio2.click()
                    print("Second radio button clicked.")
                except Exception as e:
                    print(f"Error clicking second radio button: {e}")

                # --- NEW LOGIC: Upload file using filename from page ---
                try:
                    # print("Extracting file name from page...")
                    # file_name_elem = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/app-root/div/div/div/app-common-dashboard/div/div/div[4]/form[3]/div/div[1]/div[3]/div/div[3]/div/div/a")))
                    # file_name = file_name_elem.text.strip()
                    # print(f"File name from page: {file_name}")
                    # abs_pdf_file = os.path.abspath(os.path.join('uploads', file_name))
                    # if not os.path.exists(abs_pdf_file):
                    #     print(f"File {abs_pdf_file} does not exist. Skipping Application ID {app_id}.")
                    #     continue
                    abs_pdf_file = os.path.abspath('4-oct/profile.pdf')
                    if not os.path.exists(abs_pdf_file):
                        print(f"File {abs_pdf_file} does not exist. Skipping Application ID {app_id}.")
                        continue
                    print(f"Using PDF file: {abs_pdf_file}")
                    print("Uploading file to new input...")
                    upload_elem = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/app-root/div/div/div/app-common-dashboard/div/div/div[4]/form[3]/div/div[2]/div[1]/div[2]/div/input")))
                    print(f"Upload input: displayed={upload_elem.is_displayed()}, enabled={upload_elem.is_enabled()}, type={upload_elem.get_attribute('type')}")
                    time.sleep(0.5)
                    upload_elem.send_keys(abs_pdf_file)
                    print(f"File {abs_pdf_file} uploaded.")
                    time.sleep(0.5)
                except Exception as e:
                    print(f"Error uploading file: {e}")

                # --- NEW LOGIC: Select dropdown option 2 ---
                try:
                    print("Selecting option 2 in dropdown...")
                    dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/div/div/div/app-common-dashboard/div/div/div[4]/form[3]/div/div[2]/div[2]/select")))
                    options = dropdown.find_elements(By.TAG_NAME, "option")
                    if len(options) >= 2:
                        options[1].click()
                        print("Option 2 selected in dropdown.")
                    else:
                        print("Dropdown does not have enough options.")
                except Exception as e:
                    print(f"Error selecting dropdown option: {e}")

                # --- NEW LOGIC: Check the box ---
                try:
                    print("Checking the box...")
                    checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/div/div/div/app-common-dashboard/div/div/div[6]/div/input")))
                    driver.execute_script("arguments[0].scrollIntoView();", checkbox)
                    time.sleep(0.5)
                    checkbox.click()
                    print("Checkbox checked.")
                except Exception as e:
                    print(f"Error checking the box: {e}")

                # --- Extract val1 and val2 before submit ---
                def get_xpath_text(xpath):
                    try:
                        elem = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                        return elem.text.strip()
                    except Exception as e:
                        print(f"Could not extract value for {xpath}: {e}")
                        return ''


                # New XPaths for val1 and val2 (dropdowns)
                def get_selected_option_text(xpath):
                    try:
                        select_elem = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                        selected = select_elem.find_element(By.XPATH, './option[@selected]')
                        return selected.text.strip()
                    except Exception:
                        # fallback: get first selected option if @selected not set
                        try:
                            options = select_elem.find_elements(By.TAG_NAME, 'option')
                            for opt in options:
                                if opt.is_selected():
                                    return opt.text.strip()
                        except Exception as e:
                            print(f"Could not extract selected option for {xpath}: {e}")
                        return ''
                    
                # input("Press Enter to continue with value checks...")

                val1 = get_selected_option_text("/html/body/app-root/div/div/div/app-common-dashboard/div/div/div[4]/div[1]/div/div[2]/form/div/div[1]/div/select")
                val2 = get_selected_option_text("/html/body/app-root/div/div/div/app-common-dashboard/div/div/div[4]/div[1]/div/div[2]/form/div/div[2]/div/select")

                if val1 != "BC-A" or val2 != "Agnikula Kshatriya":
                    print(f"Skipping Application ID {app_id}: val1='{val1}' (expected 'BC-A'), val2='{val2}' (expected 'Agnikula Kshatriya'). Values mismatch.")
                    # Write to processed file with mismatch reason
                    val3 = get_xpath_text("/html/body/app-root/div/div/div/app-common-dashboard/div/div/div[4]/form[1]/app-common-form-view/div[1]/div[2]/div[1]/div[2]/div")
                    try:
                        write_header = not os.path.exists(processed_file) or os.stat(processed_file).st_size == 0
                        with open(processed_file, 'a', newline='', encoding='utf-8') as pf:
                            writer = csv.writer(pf)
                            if write_header:
                                writer.writerow(['Application ID', 'CertView1', 'CertView2', 'FormView', 'Status'])
                            writer.writerow([app_id, val1, val2, val3, 'Values mismatch'])
                        print(f"Application ID {app_id} and extracted values written to {processed_file} (mismatch)")
                    except Exception as e:
                        print(f"Error writing Application ID to {processed_file}: {e}")
                    continue

                # --- NEW LOGIC: Click submit button after checkbox ---
                try:
                    print("Clicking submit button after checkbox...")
                    # input("Press Enter to continue to click submit...")
                    submit_xpath = "/html/body/app-root/div/div/div/app-common-dashboard/div/div/div[7]/button"
                    submit_btn = wait.until(EC.element_to_be_clickable((By.XPATH, submit_xpath)))
                    driver.execute_script("arguments[0].scrollIntoView();", submit_btn)
                    try:
                        submit_btn.click()
                        print("Submit button clicked with .click().")
                    except Exception as e:
                        print(f".click() failed: {e}, trying JS click...")
                        driver.execute_script("arguments[0].click();", submit_btn)
                        print("Submit button clicked with JS.")
                    # Wait for modal after clicking submit
                    print("Waiting for modal button to appear after submit...")
                    modal_btn_xpath = "/html/body/ngb-modal-window/div/div/app-common-msg-modal/div[3]/button"
                    modal_btn = wait.until(EC.element_to_be_clickable((By.XPATH, modal_btn_xpath)))
                    driver.execute_script("arguments[0].scrollIntoView();", modal_btn)
                    driver.execute_script("arguments[0].click();", modal_btn)
                    print("Modal button clicked.")
                except Exception as e:
                    print(f"Error clicking submit or modal button: {e}")
                # Wait for page to reload before next record
                print("Waiting for next record's search input to appear after modal...")
                try:
                    wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/app-root/div/div/div/app-common-dashboard/div/div/div[2]/input")))
                    print("Next record's search input is ready.")
                except Exception as e:
                    print(f"Error waiting for next search input: {e}")
                # Update status back to CSV
                row['Automation Status'] = 'Success'
                print(f"Completed Application ID: {app_id} with status: Success")
                # Refresh the page and wait for the next record's search input to be ready before proceeding
                print("Refreshing page for next record...")
                driver.refresh()
                try:
                    wait = WebDriverWait(driver, 10)
                    wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/app-root/div/div/div/app-common-dashboard/div/div/div[2]/input")))
                    print("Next record's search input is ready after refresh.")
                except Exception as e:
                    print(f"Error waiting for next search input after refresh: {e}")
                # Extract val3 for processed file
                val3 = get_xpath_text("/html/body/app-root/div/div/div/app-common-dashboard/div/div/div[4]/form[1]/app-common-form-view/div[1]/div[2]/div[1]/div[2]/div")

                # After successful processing, write Application ID and extracted values to processed_ids.csv
                try:
                    write_header = not os.path.exists(processed_file) or os.stat(processed_file).st_size == 0
                    with open(processed_file, 'a', newline='', encoding='utf-8') as pf:
                        writer = csv.writer(pf)
                        if write_header:
                            writer.writerow(['Application ID', 'CertView1', 'CertView2', 'FormView', 'Status'])
                        writer.writerow([app_id, val1, val2, val3, 'Success'])
                    print(f"Application ID {app_id} and extracted values written to {processed_file}")
                except Exception as e:
                    print(f"Error writing Application ID to {processed_file}: {e}")
            except Exception as e:
                print(f"Error processing row {idx+1}: {e}")
                row['Automation Status'] = f"Failed: {e}"
                print("Waiting 4 seconds before proceeding to next row...")
                # time.sleep(4)
                continue

def main():
    username = "10690231-vro@apgsws.onmicrosoft.com"
    password = "Vro@pola123"
    driver = setup_driver()
    try:
        success = login(driver, username, password)
        if success:
            input("Login complete. Press Enter to start automation...")
            process_applications(driver, "/Users/ey/Documents/Rahet_work/Sep-3-VRO/4-oct/Data_oct_4.csv")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
