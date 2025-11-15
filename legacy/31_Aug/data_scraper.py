import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# Load request IDs from POLA_SUOMOTO.xlsx
excel_path = 'Last_Sumoto.xlsx'
df = pd.read_excel(excel_path, skiprows=2)
print(f"Loaded {len(df)} rows from {excel_path}")
print("Columns:", df.columns.tolist())
print(df['Request ID'].head())
# Load processed request IDs from 476_records.xlsx
processed_df = pd.read_excel('476_records.xlsx')
processed_ids = set() #set(processed_df['Request ID'].dropna().astype(str))

# Filter request IDs: only those not in 476_records.xlsx
request_ids = df['Request ID'].dropna()
request_ids = [rid for rid in request_ids if str(rid) not in processed_ids and str(rid).lower() != 'na' and 'bank' not in str(rid).lower()]

# Prepare new columns if not present
if 'Phone Number' not in df.columns:
    df['Phone Number'] = ''
if 'Ration Card Number' not in df.columns:
    df['Ration Card Number'] = ''

def setup_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--window-size=1920,1080')
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def login(driver, username, password):
    wait = WebDriverWait(driver, 30)
    
    driver.get("https://vswsonline.ap.gov.in/#/home")
    input("Press Enter after completing CAPTCHA...")
    time.sleep(3)
    return True
    
    login_menu = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/div/app-home/div/app-home-header/header/section/div/div/div/div[7]/div/ul/li/a")))
    login_menu.click()
    time.sleep(1)
    employee_login = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/div/app-home/div/app-home-header/header/section/div/div/div/div[7]/div/ul/li/ul/li[2]/a")))
    employee_login.click()
    time.sleep(2)
    username_field = wait.until(EC.presence_of_element_located((By.NAME, "loginfmt")))
    username_field.send_keys(username)
    username_field.send_keys(u"\ue007")
    time.sleep(2)
    password_field = wait.until(EC.presence_of_element_located((By.NAME, "passwd")))
    password_field.send_keys(password)
    password_field.send_keys(u"\ue007")
    time.sleep(5)

def fetch_dashboard_data(driver, request_id):
    wait = WebDriverWait(driver, 30)
    # Enter request ID (no need to click dashboard link each time)
    request_input = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/app-root/div/div/div/app-common-dashboard/div/div/div[2]/input")))
    request_input.clear()
    request_input.send_keys(str(request_id))
    time.sleep(1)
    # Check for 'No requests are pending.' message
    try:
        status_cell = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/app-root/div/div/div/app-common-dashboard/div/div/div[2]/div/table/tbody/tr/td")))
        status_text = status_cell.text.strip()
        if status_text == "No requests are pending.":
            print(f"Request ID {request_id}: No requests are pending.")
            return "No number found", "No number found"
    except Exception:
        pass  # If not found, continue as normal
    # Click search result
    result_cell = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/div/div/div/app-common-dashboard/div/div/div[2]/div[1]/table/tbody/tr/td[2]")))
    result_cell.click()
    time.sleep(2)
    # Get phone number
    phone_elem = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/app-root/div/div/div/app-common-dashboard/div/div/div[4]/form[1]/app-common-form-view/div[1]/div[2]/div[3]/div[2]/div")))
    phone_number = phone_elem.text.strip()
    # Get ration card number
    ration_elem = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/app-root/div/div/div/app-common-dashboard/div/div/div[4]/form[1]/app-integrated-certificate-view/div[2]/div[2]/div[1]/div[1]/div")))
    ration_card = ration_elem.text.strip()
    # Print details
    print(f"Phone Number: {phone_number}, Ration Card Number: {ration_card}")
    # Scroll up before next entry
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(1)
    return phone_number, ration_card

def main():
    username = "10690231-vro@apgsws.onmicrosoft.com"
    password = "Vro@pola123"
    driver = setup_driver()
    try:
        login(driver, username, password)
        print(f"Working on {len(request_ids)} request IDs...")
        for idx, request_id in enumerate(request_ids):
            print(f"Processing Request ID: {request_id}")
            try:
                phone, ration = fetch_dashboard_data(driver, request_id)
                df.loc[df['Request ID'] == request_id, 'Phone Number'] = phone
                df.loc[df['Request ID'] == request_id, 'Ration Card Number'] = ration
            except Exception as e:
                print(f"Failed for {request_id}: {e}")
                continue  # Gracefully skip to next request ID
            time.sleep(1)
    finally:
        driver.quit()
        df.to_excel('POLA_SUOMOTO_with_data.xlsx', index=False)
        print("Saved results to POLA_SUOMOTO_with_data.xlsx")

if __name__ == "__main__":
    main()
