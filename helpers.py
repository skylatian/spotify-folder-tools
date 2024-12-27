import json
import http.client
from pprint import pprint
from playlists import daily_mix_hub
import requests

def move_playlist(auth_token, user, moving_playlist, destination_folder):
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
        f'/playlist/v2/user/{user}/rootlist/changes',
        json.dumps(json_data),
        headers
    )
    response = conn.getresponse()
    response = response.read().decode()
    response = json.loads(response)
    pprint(response)

def get_playlist_info(sp, playlistID):
    playlist = sp.playlist(playlistID)
    return playlist

def get_daylistO(sp, user_id):
    dl_endpoint = f"https://api.spotify.com/v1/browse/categories/{daily_mix_hub}/playlists" # this might work. needs testing.
    return None


def get_daylist(access_token, playlist_id):
    """
    Fetches all tracks from a Spotify playlist using a non-Spotipy method.

    Parameters:
        access_token (str): Spotify API access token.
        playlist_id (str): ID of the playlist to fetch.

    Returns:
        List of track metadata (IDs, names, artists).
    """
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = {"Authorization": f"{access_token}"}
    tracks = []
    offset = 0
    limit = 100  # Spotify's maximum allowed per request

    while True:
        response = requests.get(url, headers=headers, params={"offset": offset, "limit": limit})
        if response.status_code != 200:
            raise Exception(f"Failed to fetch tracks: {response.status_code} {response.json()}")
        
        data = response.json()
        items = data.get('items', [])
        
        for item in items:
            track = item['track']
            track_id = track['id']
            track_name = track['name']
            artist_name = track['artists'][0]['name']
            tracks.append(f"{artist_name}, {track_name}, {track_id}")
        
        if len(items) < limit:  # If fewer than limit results, we're done
            break
        
        offset += limit

    print(f"Retrieved {len(tracks)} tracks.")
    return tracks

def get_all_in_playlist(sp, playlistID):
    returned_chunk = 100
    returned = 0
    ids = []
    tracks = []
    i = 0
    chunk = 100

    while returned_chunk == chunk:
        items = sp.playlist_items(playlistID, limit=100, offset=returned)
        
        for i,j in enumerate(items['items']):
            # pprint(j)
            songId = j['track']['id']
            ids.append(songId)

            trackname = j['track']['name']
            artist = j['track']['artists'][0]['name']
            trackInfo = f"{artist}, {trackname}, {songId}"
            tracks.append(trackInfo)
            
            returned += 1
            #print(returned)

        returned_chunk = i+1
        
        #print(returned_chunk,len(ids),returned_chunk == chunk)
        
        b = f"Found {returned} songs..."
        print (b, end="\r")

    return ids, tracks

def create_blank_playlist(sp, user_id):
    try:
        # Get the current user
        new_playlist = sp.user_playlist_create(user=user_id,name="this is another test playlist",public=False, collaborative=False, description= "date, time and note here")
        #pprint(new_playlist)  # Debugging response
        new_playlist_uri = new_playlist['uri']
        
        return new_playlist_uri
    #print(new_playlist)

    except Exception as e:
        print(f"Error creating playlist: {e}")
        return None
    