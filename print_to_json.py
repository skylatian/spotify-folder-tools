import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as cond
from selenium.webdriver.common.keys import Keys
import time

import os

from credentials import username, password, chromedriver_path

# prints all network logs to a JSON file

# Set up Chrome for performance logging
caps = DesiredCapabilities.CHROME.copy()
caps['goog:loggingPrefs'] = {'performance': 'ALL'}

service = Service(ChromeDriverManager().install())
#service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service, desired_capabilities=caps)

try:
    # Log in to Spotify
    driver.get("https://accounts.spotify.com/en/login?continue=https:%2F%2Fopen.spotify.com%2F")
    username_field = WebDriverWait(driver, 10).until(cond.presence_of_element_located((By.CSS_SELECTOR, 'input[autocomplete="username"]')))
    username_field.clear()
    username_field.send_keys(username)

    password_field = driver.find_element(By.CSS_SELECTOR, 'input[autocomplete="current-password"]')
    password_field.clear()
    password_field.send_keys(password)
    driver.find_element(By.ID, "login-button").send_keys(Keys.ENTER)

    # Wait for the main page to load
    WebDriverWait(driver, 15).until(cond.url_contains("https://open.spotify.com"))

    # Introduce a small delay to allow all requests to complete
    #time.sleep(5)

    # Extract all network logs
    performance_logs = driver.get_log("performance")

    # Save logs to a file
    log_file = "logs/network_logs.json"

    # increment the file name if it already exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    i = 1
    while os.path.exists("logs/network_logs_%s.json" % i):
        i += 1

    with open("logs/network_logs_%s.json" % i, "w") as f:
        logs = []
        for entry in performance_logs:
            try:
                log_message = json.loads(entry["message"])
                logs.append(log_message)  # Collect logs in a list
            except Exception as e:
                print(f"Error processing log entry: {e}")
        json.dump(logs, f, indent=2)  # Save all logs to file

    print(f"All logs have been saved to {log_file}")

finally:
    driver.quit()
