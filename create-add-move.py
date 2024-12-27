from functionize import auth_output
from playlists import folder as dest_folder
from credentials import credentials
import http.client
#import logging
from pprint import pprint
import json

#logging.basicConfig(level=logging.DEBUG)

# spotipy
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Initialize Spotipy with user credentials
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(credentials.client_id,
                                               credentials.client_secret,
                                               redirect_uri=credentials.redirect_uri,
                                               scope="playlist-read-private playlist-modify-private user-library-read"))

sp.trace = True  # Enable debugging
# Get the current user
user = sp.current_user()
user_id = user['id']
print(user_id)



def create_blank_playlist():
    try:
        new_playlist = sp.user_playlist_create(user=user_id,name="this is a test playlist",public=False, collaborative=False, description= "date, time and note here")
        #pprint(new_playlist)  # Debugging response
        new_playlist_uri = new_playlist['uri']
        
        return new_playlist_uri
    #print(new_playlist)
    #sp.playlist_add_items(new_playlist, ["32x2evaEmK4mBvY4uXzQ6o"])

    except Exception as e:
        print(f"Error creating playlist: {e}")
        return None


def move_playlist(auth_token, user_username, moving_playlist, destination_folder):
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
                                    'uri': moving_playlist,
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
        f'/playlist/v2/user/{user_username}/rootlist/changes',
        json.dumps(json_data),
        headers
    )
    response = conn.getresponse()
    
    response = response.read().decode()
    if response == 'Invalid access token':
        print("'Invalid access token' error")
        # THIS IS WHERE YOU RE-TRY FOR A TOKEN MAYBE?
        return
    else:
        response = json.loads(response)
        pprint(response)


nplURI = create_blank_playlist()

print("created playlist, now moving")



# authorize separately (streamline this massivley)
print("authorizing in the silly way...")
authTok, cliTok = auth_output()

print("authorized, moving")

move_playlist(authTok, "songsinthesky", nplURI, dest_folder)
#playlist = # ID of created playlist
#move_playlist(authTok, username, playlist, folder)
