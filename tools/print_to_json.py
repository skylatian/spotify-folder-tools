from seleniumbase import SB
import json
import os
import gzip
from io import BytesIO
from bs4 import BeautifulSoup  # For parsing HTML
from credentials import username, password  # Import credentials

# Directory setup for logs and HTML files
os.makedirs("logs", exist_ok=True)
os.makedirs("logs/html_bodies", exist_ok=True)

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
        # Look for <script> tags containing the JSON with the token data
        script_tags = soup.find_all("script")
        for script in script_tags:
            if "accessToken" in script.text:  # Narrow down to relevant script
                try:
                    # Extract JSON-like structure from script content
                    json_start = script.text.find("{")
                    json_end = script.text.rfind("}") + 1
                    token_data = json.loads(script.text[json_start:json_end])
                    
                    # Extract desired keys
                    access_token = token_data.get("accessToken")
                    expiration_timestamp = token_data.get("accessTokenExpirationTimestampMs")
                    
                    if access_token and expiration_timestamp:
                        return {
                            "accessToken": access_token,
                            "accessTokenExpirationTimestampMs": expiration_timestamp
                        }
                except json.JSONDecodeError:
                    pass
        print("Access token not found in the HTML.")
    except Exception as e:
        print(f"Error extracting tokens: {e}")
    return {}

# Cache file for tokens
cache_file = "token_cache.json"

with SB(wire=True) as sb:
    # Log in to Spotify
    sb.open("https://accounts.spotify.com/en/login?continue=https:%2F%2Fopen.spotify.com%2F")
    sb.type('input[autocomplete="username"]', username)
    sb.type('input[autocomplete="current-password"]', password)
    sb.click("#login-button")

    # Wait for the main page to load
    sb.wait_for_element("body", timeout=15)  # Ensure the page loads

    # Introduce a small delay to allow all requests to complete
    sb.sleep(5)

    # Capture raw network logs
    raw_logs = []
    token_cache = {}
    for idx, request in enumerate(sb.driver.requests, start=1):
        if 'https://open.spotify.com/' in request.url:
            body_filename = None
            token_data = {}
            if request.response and request.response.body:
                # Decode the body if necessary
                body_content = request.response.body
                if isinstance(body_content, bytes):
                    body_content = decode_gzip_body(body_content)
                
                # Save the response body to an HTML file
                body_filename = f"logs/html_bodies/body_{idx}.html"
                with open(body_filename, "w", encoding="utf-8") as html_file:
                    html_file.write(body_content)

                # Extract tokens from the HTML content
                token_data = extract_tokens_from_html(body_content)
                if token_data:
                    token_cache.update(token_data)  # Update token cache with extracted values

            # Save metadata and reference to the HTML file
            log_entry = {
                'url': request.url,
                'status_code': request.response.status_code if request.response else None,
                'headers': dict(request.response.headers) if request.response else None,
                'body_file': body_filename
            }
            raw_logs.append(log_entry)

    # Save logs to an iterative JSON file
    i = 1
    while os.path.exists(f"logs/network_logs_{i}.json"):
        i += 1
    log_file_path = f"logs/network_logs_{i}.json"
    with open(log_file_path, "w") as f:
        json.dump(raw_logs, f, indent=2)
    print(f"Logs saved to {log_file_path}")

    # Save token cache to a separate file
    if token_cache:
        with open(cache_file, "w") as f:
            json.dump(token_cache, f, indent=2)
        print(f"Access token and expiration saved to {cache_file}")
    else:
        print("No tokens were found.")
