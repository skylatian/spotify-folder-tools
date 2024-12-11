import json
import time
import http.client
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as cond
from selenium.webdriver.chrome.options import Options

from credentials import username, password, chromedriver_path
from playlists import playlist, folder
from pprint import pprint



def get_tokens(): 

    # set some options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # remove if you want to see the browser window
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    #chrome_options.add_argument("--no-sandbox") # enable if having difficulties running in Docker or something
    #chrome_options.add_argument("--disable-dev-shm-usage") # see above

    # Set up Chrome with performance logging
    service = Service(ChromeDriverManager().install())

    caps = DesiredCapabilities.CHROME.copy()
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}

    #driver = webdriver.Chrome(service=Service(chromedriver_path), desired_capabilities=caps)#, options=chrome_options)
    driver = webdriver.Chrome(service=service, desired_capabilities=caps, options=chrome_options)

    try:
        # Log in to Spotify
        driver.get("https://accounts.spotify.com/en/login?continue=https:%2F%2Fopen.spotify.com%2F")
        WebDriverWait(driver, 10).until(cond.presence_of_element_located((By.CSS_SELECTOR, 'input[autocomplete="username"]'))).send_keys(username)
        driver.find_element(By.CSS_SELECTOR, 'input[autocomplete="current-password"]').send_keys(password)
        driver.find_element(By.ID, "login-button").click()

        # Wait for the main page to load and allow network requests to complete
        WebDriverWait(driver, 15).until(cond.url_contains("https://open.spotify.com"))
        time.sleep(3) # might not be necessary

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
            #print("Authorization Token:", authorization_token)
            #print("")
            #print("Client Token:", client_token)
            return authorization_token, client_token
        else:
            print("Tokens not found in network logs.")
            return None, None

    finally:
        driver.quit()
    

def send_request(auth_token, user, moving_playlsit, destination_folder):
    conn = http.client.HTTPSConnection('spclient.wg.spotify.com')
    headers = {
        'accept': 'application/json',
        'accept-language': 'en',
        'app-platform': 'WebPlayer',
        'authorization': auth_token,
        'cache-control': 'no-cache',
        #'client-token': client_token,
        'content-type': 'application/json;charset=UTF-8',
        'dnt': '1',
        'origin': 'https://open.spotify.com',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': 'https://open.spotify.com/',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
    }
    json_data = {
        'deltas': [
            {
                'ops': [
                    {
                        'kind': 4,
                        'mov': {
                            'items': [
                                {
                                    'uri': moving_playlsit,
                                    'attributes': {
                                        'formatAttributes': [],
                                        'availableSignals': [],
                                    },
                                },
                            ],
                            'addAfterItem': {
                                'uri': destination_folder,
                                'attributes': {
                                    'formatAttributes': [],
                                    'availableSignals': [],
                                },
                            },
                        },
                    },
                ],
                'info': {
                    'source': {
                        'client': 5,
                    },
                },
            },
        ],
        'wantResultingRevisions': False,
        'wantSyncResult': False,
        'nonces': [],
    }
    conn.request(
        'POST',
        f'/playlist/v2/user/{user}/rootlist/changes',
        json.dumps(json_data),
        headers
    )
    response = conn.getresponse()
    response = response.read().decode()
    response = json.loads(response)
    pprint(response)


def auth_and_request():
    authT, cliT = get_tokens()
    if authT:
        print("Tokens found")
        print(authT, cliT)
    else:
        print("Tokens not found")
        exit(1)

    send_request(authT, username, playlist, folder)


auth_and_request()