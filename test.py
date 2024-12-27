import json
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from pprint import pprint

# converted from https://github.com/FrostBreker/spotify-private-api/blob/main/helpers.go with chatgpt

def get_spotify_client_id():
    url = "https://clienttoken.spotify.com/v1/clienttoken"
    headers = {
        "accept": "application/json",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/json",
        "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Brave\";v=\"114\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "sec-gpc": "1",
        "Referer": "https://open.spotify.com/",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }
    payload = {
        "client_data": {
            "client_version": "1.2.16.334.g29fe6bdc",
            "client_id": "d8a5ed958d274c2e8ee717e6a4b0971d",
            "js_sdk_data": {
                "device_brand": "unknown",
                "device_model": "unknown",
                "os": "windows",
                "os_version": "NT 10.0",
                "device_id": "653eea96ea4044e6725f27bc508ea9a5",
                "device_type": "computer"
            }
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

def fetch_spotify_client_token():
    url = "https://open.spotify.com/intl-fr"
    response = requests.get(url)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, "html.parser")
    script_tag = soup.find("script", {"id": "session", "data-testid": "session"})
    if not script_tag:
        raise ValueError("Could not find the session script tag in the HTML")

    token_data = script_tag.string
    return json.loads(token_data)

# Example usage
if __name__ == "__main__":
    client_id_response = get_spotify_client_id()
    print("Client Token:", client_id_response)

    client_token_response = fetch_spotify_client_token()
    print("Bearer Token:", client_token_response["accessToken"])
