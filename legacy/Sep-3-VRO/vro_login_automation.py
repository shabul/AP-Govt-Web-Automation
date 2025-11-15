from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv
import os

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
        # Navigate to the website
        # driver.get("https://vswsonline.ap.gov.in/#/home")
        driver.get("https://vswsonline.ap.gov.in/#/suomoto")
        input("Please log in manually, then press Enter to continue automation...")
        print("Continuing automation after manual login.")
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

def process_applications(driver, csv_path):
    available_ids = get_available_ids('ID_check_results.csv')
    print(f"Total available IDs: {len(available_ids)}")
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
        for idx, row in enumerate(rows):
            # if idx = 100:
            #     print("Skipping first row.")
            #     continue
            app_id = row['Request ID'].strip()
            if app_id not in available_ids:
                print(f"Skipping Application ID {app_id}: Not marked as Available.")
                continue
            try:
                print(f"Processing Application ID: {app_id}")
                wait = WebDriverWait(driver, 30)
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
                time.sleep(2)
                print("Locating phone number...")
                try:
                    phone_elem = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/app-root/div/div/div/app-common-dashboard/div/div/div[4]/form[1]/app-common-form-view/div[1]/div[2]/div[3]/div[2]/div")))
                    phone_number = phone_elem.text.strip()
                    print(f"Phone number found: {phone_number}")
                    if not phone_number:
                        phone_number = "9999999999"
                except Exception:
                    print("Phone number not found, using default 9999999999")
                    phone_number = "9999999999"
                print("Selecting BC-A in first dropdown...")
                dropdown1 = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/div/div/div/app-common-dashboard/div/div/div[4]/div[1]/div/div[2]/form/div/div[1]/div/select")))
                print(f"Dropdown1 current value before selection: {dropdown1.get_attribute('value')}")
                time.sleep(0.5)
                found_bc_a = False
                for option in dropdown1.find_elements(By.TAG_NAME, "option"):
                    print(f"Dropdown1 option: text='{option.text}', value='{option.get_attribute('value')}', selected={option.is_selected()}")
                    if "BC-A" in option.text:
                        try:
                            driver.execute_script("arguments[0].scrollIntoView();", option)
                            driver.execute_script("arguments[0].click();", option)
                            time.sleep(0.5)
                            if not option.is_selected():
                                print("JS click did not select. Trying Selenium click...")
                                option.click()
                                time.sleep(0.5)
                            # If still not selected, set value directly
                            if not option.is_selected():
                                print("Direct click did not select. Setting value via JS...")
                                driver.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('change'));", dropdown1, option.get_attribute('value'))
                                time.sleep(0.5)
                            found_bc_a = option.is_selected()
                            print(f"Selected BC-A: {found_bc_a}")
                        except Exception as e:
                            print(f"Error selecting BC-A: {e}")
                        break
                print(f"Dropdown1 current value after selection: {dropdown1.get_attribute('value')}")
                if not found_bc_a:
                    print("BC-A not found or not selected in dropdown1!")
                time.sleep(1)
                print("Selecting Agnikula Kshatriya in sub-caste dropdown...")
                dropdown2 = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/div/div/div/app-common-dashboard/div/div/div[4]/div[1]/div/div[2]/form/div/div[2]/div/select")))
                print(f"Dropdown2 current value before selection: {dropdown2.get_attribute('value')}")
                found_agnikula = False
                for option in dropdown2.find_elements(By.TAG_NAME, "option"):
                    print(f"Dropdown2 option: text='{option.text}', value='{option.get_attribute('value')}', selected={option.is_selected()}")
                    if "Agnikula Kshatriya" in option.text:
                        driver.execute_script("arguments[0].scrollIntoView();", option)
                        driver.execute_script("arguments[0].click();", option)
                        time.sleep(0.5)
                        if not option.is_selected():
                            print("JS click did not select. Trying Selenium click...")
                            option.click()
                            time.sleep(0.5)
                        if not option.is_selected():
                            print("Direct click did not select. Setting value via JS...")
                            driver.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('change'));", dropdown2, option.get_attribute('value'))
                            time.sleep(0.5)
                        found_agnikula = option.is_selected()
                        print(f"Selected Agnikula Kshatriya: {found_agnikula}")
                        break
                print(f"Dropdown2 current value after selection: {dropdown2.get_attribute('value')}")
                if not found_agnikula:
                    print("Agnikula Kshatriya not found or not selected in dropdown2!")
                time.sleep(1)
                print("Selecting Hindu in third dropdown...")
                dropdown3 = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/div/div/div/app-common-dashboard/div/div/div[4]/div[1]/div/div[2]/form/div/div[3]/div/select")))
                found_hindu = False
                for option in dropdown3.find_elements(By.TAG_NAME, "option"):
                    print(f"Dropdown3 option: {option.text}")
                    if "Hindu" in option.text:
                        option.click()
                        found_hindu = True
                        print("Selected Hindu.")
                        break
                if not found_hindu:
                    print("Hindu not found in dropdown3!")
                print("Pasting phone number in textbox...")
                phone_input = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/app-root/div/div/div/app-common-dashboard/div/div/div[4]/div[1]/div/div[2]/form/div/div[8]/input")))
                phone_input.clear()
                phone_input.send_keys(phone_number)
                print("Typing NA in textbox...")
                na_input = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/app-root/div/div/div/app-common-dashboard/div/div/div[4]/div[1]/div/div[2]/form/div/div[6]/input")))
                na_input.clear()
                na_input.send_keys("NA")
                print("Selecting POLATITIPPA in dropdown...")
                dropdown4 = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/div/div/div/app-common-dashboard/div/div/div[4]/div[1]/div/div[2]/form/div/div[5]/div/select")))
                found_polatitippa = False
                for option in dropdown4.find_elements(By.TAG_NAME, "option"):
                    print(f"Dropdown4 option: {option.text}")
                    if "POLATITIPPA" in option.text:
                        option.click()
                        found_polatitippa = True
                        print("Selected POLATITIPPA.")
                        break
                if not found_polatitippa:
                    print("POLATITIPPA not found in dropdown4!")
                print("Selecting radio button...")
                radio_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/div/div/div/app-common-dashboard/div/div/div[4]/div[1]/div/div[2]/form/div/div[11]/div/div/input[2]")))
                print(f"Radio button attributes: displayed={radio_btn.is_displayed()}, enabled={radio_btn.is_enabled()}, location={radio_btn.location}, size={radio_btn.size}")
                driver.execute_script("arguments[0].scrollIntoView();", radio_btn)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", radio_btn)
                print("Radio button clicked.")
                time.sleep(0.5)
                # Check if table has results for Application ID
                try:
                    status_cell = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/app-root/div/div/div/app-common-dashboard/div/div/div[2]/div[1]/table/tbody/tr/td")))
                    status_text = status_cell.text.strip()
                    print(f"Status cell text: {status_text}")
                    if status_text == "No requests are pending.":
                        print(f"Application ID {app_id}: No requests are pending. Skipping to next record.")
                        row['Automation Status'] = "No requests are pending."
                        continue
                except Exception as e:
                    print(f"Status cell not found or error: {e}")
                # Determine PDF file based on row index
                # row_index = int(row['SNO'])
                # print(f"Row index: {row_index}")
                # pdf_file = None
                # pdf_ranges = [
                #     (1, 24, "1-24.pdf"),
                #     (25, 51, "25-51.pdf"),
                #     (52, 78, "52-78.pdf"),
                #     (79, 105, "79-105.pdf"),
                #     (106, 132, "106-132.pdf"),
                #     (133, 159, "133-159.pdf"),
                #     (160, 186, "160-186.pdf"),
                #     (187, 213, "187-213.pdf")
                # ]
                # for start, end, fname in pdf_ranges:
                #     if start <= row_index <= end:
                #         pdf_file = f"uploads/{fname}"
                #         break
                pdf_file = '4-oct/profile.pdf'
                print(f"PDF file chosen: {pdf_file}")
                import os
                abs_pdf_file = os.path.abspath(pdf_file)
                # Upload PDF in three places
                upload_xpaths = [
                    "/html/body/app-root/div/div/div/app-common-dashboard/div/div/div[4]/div[1]/div/div[2]/form/div/div[12]/div/div/input",
                    "/html/body/app-root/div/div/div/app-common-dashboard/div/div/div[4]/form[3]/div/div[3]/div[1]/div[2]/div/input",
                    "/html/body/app-root/div/div/div/app-common-dashboard/div/div/div[4]/form[3]/div/div[3]/div[2]/div[2]/div/input"
                ]
                for i, xpath in enumerate(upload_xpaths):
                    print(f"Uploading PDF to input {i+1} at {xpath}")
                    upload_elem = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                    print(f"Upload input {i+1}: displayed={upload_elem.is_displayed()}, enabled={upload_elem.is_enabled()}, type={upload_elem.get_attribute('type')}")
                    time.sleep(1)
                    upload_elem.send_keys(abs_pdf_file)
                    print(f"Sent file {abs_pdf_file} to input {i+1}")
                    time.sleep(1)
                # Check the checkbox
                checkbox_xpath = "/html/body/app-root/div/div/div/app-common-dashboard/div/div/div[6]/div/input"
                print(f"Checking checkbox at {checkbox_xpath}")
                checkbox_elem = wait.until(EC.element_to_be_clickable((By.XPATH, checkbox_xpath)))
                driver.execute_script("arguments[0].click();", checkbox_elem)
                # Select 'Recommended' in dropdown
                dropdown_xpath = "/html/body/app-root/div/div/div/app-common-dashboard/div/div/div[4]/form[3]/div/div[3]/div[3]/select"
                print(f"Selecting 'Recommended' in dropdown at {dropdown_xpath}")
                dropdown_elem = wait.until(EC.element_to_be_clickable((By.XPATH, dropdown_xpath)))
                found_recommended = False
                for option in dropdown_elem.find_elements(By.TAG_NAME, "option"):
                    print(f"Dropdown option: {option.text}")
                    if "Recommended" in option.text:
                        option.click()
                        found_recommended = True
                        print("Selected 'Recommended'.")
                        break
                if not found_recommended:
                    print("'Recommended' not found in dropdown!")
                # Click submit button to complete record
                submit_xpath = "/html/body/app-root/div/div/div/app-common-dashboard/div/div/div[7]/button"
                print(f"Clicking submit button at {submit_xpath}")
                try:
                    submit_btn = wait.until(EC.element_to_be_clickable((By.XPATH, submit_xpath)))
                    driver.execute_script("arguments[0].scrollIntoView();", submit_btn)
                    driver.execute_script("arguments[0].click();", submit_btn)
                    print("Submit button clicked. Record completed.")
                    status = "Success"
                except Exception as e:
                    print(f"Error clicking submit button: {e}")
                    status = f"Failed: {e}"
                # After submit, wait for modal and click its button
                try:
                    print("Waiting for modal button to appear...")
                    modal_btn_xpath = "/html/body/ngb-modal-window/div/div/app-common-msg-modal/div[3]/button"
                    modal_btn = wait.until(EC.element_to_be_clickable((By.XPATH, modal_btn_xpath)))
                    driver.execute_script("arguments[0].scrollIntoView();", modal_btn)
                    driver.execute_script("arguments[0].click();", modal_btn)
                    print("Modal button clicked.")
                except Exception as e:
                    print(f"Modal button not found or error: {e}")
                # Wait for page to reload before next record
                print("Waiting for next record's search input to appear after modal...")
                try:
                    wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/app-root/div/div/div/app-common-dashboard/div/div/div[2]/input")))
                    print("Next record's search input is ready.")
                except Exception as e:
                    print(f"Error waiting for next search input: {e}")
                # Update status back to CSV
                row['Automation Status'] = status
                print(f"Completed Application ID: {app_id} with status: {status}")
                # Wait for the next record's search input to be ready before proceeding
                print("Waiting for next record's search input to appear...")
                try:
                    wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/app-root/div/div/div/app-common-dashboard/div/div/div[2]/input")))
                    print("Next record's search input is ready.")
                except Exception as e:
                    print(f"Error waiting for next search input: {e}")
            except Exception as e:
                print(f"Error processing row {idx+1}: {e}")
                row['Automation Status'] = f"Failed: {e}"
                print("Waiting 10 seconds before proceeding to next row...")
                time.sleep(10)
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
