import os
import json
import gzip
from io import BytesIO
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from seleniumbase import SB
from credentials import credentials

CACHE_FILE = ".token_cache.json"

def decode_gzip_body(body):
    """Decode gzip-compressed response bodies."""
    try:
        with gzip.GzipFile(fileobj=BytesIO(body)) as gz:
            return gz.read().decode('utf-8')
    except Exception as e:
        print(f"Error decoding gzip body: {e}")
        return body.decode('utf-8', errors='ignore')  # Fallback if not gzip

def extract_tokens_from_html(html_content):
    """Extract accessToken and accessTokenExpirationTimestampMs from HTML content."""
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        script_tags = soup.find_all("script")
        for script in script_tags:
            if "accessToken" in script.text:
                try:
                    json_start = script.text.find("{")
                    json_end = script.text.rfind("}") + 1
                    token_data = json.loads(script.text[json_start:json_end])
                    return {
                        "accessToken": token_data.get("accessToken"),
                        "accessTokenExpirationTimestampMs": int(token_data.get("accessTokenExpirationTimestampMs")),
                    }
                except json.JSONDecodeError as e:
                    print(f"JSON Decode Error: {e}")
    except Exception as e:
        print(f"Error extracting tokens: {e}")
    return {}

def authenticate():
    """Authenticate with Spotify and fetch a new access token."""
    with SB(wire=True) as sb:
        sb.open("https://accounts.spotify.com/en/login?continue=https:%2F%2Fopen.spotify.com%2F")
        sb.type('input[autocomplete="username"]', credentials.username)
        sb.type('input[autocomplete="current-password"]', credentials.password)
        sb.click("#login-button")
        sb.wait_for_element("body", timeout=15)
        sb.sleep(10)

        for request in sb.driver.requests:
            if 'https://open.spotify.com/' in request.url:
                if request.response and request.response.body:
                    body = request.response.body
                    html_content = decode_gzip_body(body)
                    token_data = extract_tokens_from_html(html_content)
                    if token_data:
                        # Save token data to cache file
                        with open(CACHE_FILE, "w") as f:
                            json.dump(token_data, f, indent=2)
                        return token_data
    return {}

def load_cached_token():
    """Load the cached token and check its validity."""
    if not os.path.exists(CACHE_FILE):
        return None

    with open(CACHE_FILE, "r") as f:
        token_data = json.load(f)

    expiration_timestamp = token_data.get("accessTokenExpirationTimestampMs")
    if not expiration_timestamp:
        return None

    # Convert timestamp to datetime and check if it will expire in less than 5 minutes
    expiration_time = datetime.fromtimestamp(expiration_timestamp / 1000)
    if expiration_time - timedelta(minutes=5) > datetime.now():
        return token_data
    return None

def main_authentication():
    """Main authentication function."""
    token_data = load_cached_token()
    if token_data:
        print("Using cached token.")
        return f"Bearer {token_data['accessToken']}"

    print("Cached token is missing or expired. Re-authenticating...")
    token_data = authenticate()
    if token_data:
        print("New token obtained.")
        return f"Bearer {token_data['accessToken']}"

    raise RuntimeError("Failed to authenticate and obtain a new token.")
