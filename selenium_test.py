from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as cond
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# https://github.com/Shubh0405/automate_spotify_login/blob/master/practice_file.py
# Input Spotify credentials
print('Please enter your username:')
username = input()
print('Please enter your password:')
password = input()

# Path to ChromeDriver
chromedriver_path = r"C:\path\to\chromedriver.exe"  # Update this path

# Set up ChromeDriver with options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Remove this line if you want to see the browser
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # Navigate to Spotify login page
    driver.get("https://accounts.spotify.com/en/login?continue=https:%2F%2Fopen.spotify.com%2F")
    
    # Log in to Spotify
    username_field = WebDriverWait(driver, 10).until(cond.presence_of_element_located((By.NAME, "username")))
    username_field.clear()
    username_field.send_keys(username)

    password_field = driver.find_element(By.NAME, "password")
    password_field.clear()
    password_field.send_keys(password)

    driver.find_element(By.ID, "login-button").send_keys(Keys.ENTER)

    # Wait for navigation to Web Player
    WebDriverWait(driver, 15).until(cond.url_contains("https://open.spotify.com"))

    # Extract tokens from cookies (as a fallback)
    cookies = {cookie['name']: cookie['value'] for cookie in driver.get_cookies()}
    authorization = cookies.get('sp_dc')  # Common for Spotify sessions
    client_token = cookies.get('sp_key')  # Possible alternate session key

    if authorization:
        print("Authorization Token:", authorization)
    else:
        print("Authorization token not found.")

    if client_token:
        print("Client Token:", client_token)
    else:
        print("Client token not found.")

finally:
    driver.quit()
