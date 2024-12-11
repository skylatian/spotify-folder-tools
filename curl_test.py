import http.client
import json
from credentials import auth_token, client_token, username
from playlists import playlist, folder
from pprint import pprint

destination_folder = folder
moving_playlsit = playlist

conn = http.client.HTTPSConnection('spclient.wg.spotify.com')
headers = {
    'accept': 'application/json',
    'accept-language': 'en',
    'app-platform': 'WebPlayer',
    'authorization': auth_token,
    'cache-control': 'no-cache',
    'client-token': client_token,
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
    f'/playlist/v2/user/{username}/rootlist/changes',
    json.dumps(json_data),
    headers
)
response = conn.getresponse()
response = response.read().decode()
response = json.loads(response)
pprint(response)
