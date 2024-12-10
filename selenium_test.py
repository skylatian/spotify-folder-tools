import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as cond
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from credentials import username, password, chromedriver_path

# set some options
chrome_options = Options()
chrome_options.add_argument("--headless")  # remove if you want to see the browser window
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-extensions")
#chrome_options.add_argument("--no-sandbox") # enable if having difficulties running in Docker or something
#chrome_options.add_argument("--disable-dev-shm-usage") # see above

# Set up Chrome with performance logging
caps = DesiredCapabilities.CHROME.copy()
caps['goog:loggingPrefs'] = {'performance': 'ALL'}
driver = webdriver.Chrome(service=Service(chromedriver_path), desired_capabilities=caps, options=chrome_options)

try:
    # Log in to Spotify
    driver.get("https://accounts.spotify.com/en/login?continue=https:%2F%2Fopen.spotify.com%2F")
    WebDriverWait(driver, 10).until(cond.presence_of_element_located((By.CSS_SELECTOR, 'input[autocomplete="username"]'))).send_keys(username)
    driver.find_element(By.CSS_SELECTOR, 'input[autocomplete="current-password"]').send_keys(password)
    driver.find_element(By.ID, "login-button").click()

    # Wait for the main page to load and allow network requests to complete
    WebDriverWait(driver, 15).until(cond.url_contains("https://open.spotify.com"))
    time.sleep(5)

    # Extract tokens from network logs
    authorization_token, client_token = None, None
    for entry in driver.get_log("performance"):
        try:
            log = json.loads(entry["message"])["message"]
            if log["method"] == "Network.requestWillBeSent":
                headers = log["params"]["request"].get("headers", {})
                if "authorization" in headers and "client-token" in headers:
                    authorization_token = headers["authorization"]
                    client_token = headers["client-token"]
                    break
        except Exception:
            continue

    if authorization_token and client_token:
        print("Authorization Token:", authorization_token)
        print("Client Token:", client_token)
    else:
        print("Tokens not found in network logs.")

finally:
    driver.quit()
