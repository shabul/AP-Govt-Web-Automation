from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def setup_driver():
    # Set up Chrome options
    chrome_options = webdriver.ChromeOptions()
    # Remove headless mode for visual browser
    # chrome_options.add_argument('--headless')  # Commented out to run with browser window
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
        print("Navigating to login page...")
        driver.get("https://vswsonline.ap.gov.in/#/home")
        # driver.get("https://vswsonline.ap.gov.in/#/suomoto")
        time.sleep(5)
        print("Saving page source for inspection...")
        with open("page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("Page source saved to page_source.html.")
        wait = WebDriverWait(driver, 30)

        print("Waiting for main login menu to be clickable...")
        login_menu = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/div/app-home/div/app-home-header/header/section/div/div/div/div[7]/div/ul/li/a")))
        print("Main login menu found. Clicking...")
        login_menu.click()
        time.sleep(1)

        print("Waiting for employee login dropdown option...")
        employee_login = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/div/app-home/div/app-home-header/header/section/div/div/div/div[7]/div/ul/li/ul/li[2]/a")))
        print("Employee login option found. Clicking...")
        employee_login.click()
        time.sleep(2)

        print("Waiting for username field...")
        username_field = wait.until(EC.presence_of_element_located((By.NAME, "loginfmt")))
        print("Username field found. Entering username...")
        username_field.send_keys(username)
        username_field.send_keys(u"\ue007")
        time.sleep(2)

        print("Waiting for password field...")
        password_field = wait.until(EC.presence_of_element_located((By.NAME, "passwd")))
        print("Password field found. Entering password...")
        password_field.send_keys(password)
        password_field.send_keys(u"\ue007")
        time.sleep(5)

        print("Successfully logged in!")
        return True
    except Exception as e:
        import traceback
        print(f"An error occurred during login: {str(e)}")
        traceback.print_exc()
        return False

def main():
    # Login credentials
    username = "10690231-vro@apgsws.onmicrosoft.com"
    password = "Vro@pola123"
    
    # Initialize the driver
    driver = setup_driver()
    
    try:
        # Perform login
        success = login(driver, username, password)
        
        if success:
            # Keep the browser open for a while to verify the login
            time.sleep(10)
            
            # You can add more automation steps here later
            
    finally:
        # Close the browser
        driver.quit()

if __name__ == "__main__":
    main()
