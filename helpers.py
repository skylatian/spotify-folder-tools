import json
import http.client
from pprint import pprint
import re
import requests

# private
from playlists import daily_mix_hub
from playlists import daylist

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

def get_daylist_info(access_token, playlist_id):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
    headers = {"Authorization": f"{access_token}"}

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch playlist info: {response.status_code} {response.json()}")
    
    data = response.json()

    # Extract playlist metadata
    playlist_info = {
        "id": data["id"],
        "name": data["name"],
        "description": data.get("description", ""),
        "owner": data["owner"]["display_name"],
        "total_tracks": data["tracks"]["total"],
        "url": data["external_urls"]["spotify"]
    }

    print(f"Playlist '{playlist_info['name']}' info retrieved successfully.")
    return playlist_info

def get_daylist(access_token, playlist_id):
    """
 Fetches all tracks from a playlist, intended specifically for Daylist use.
 (Daylists do not work with Spotipy, as far as I can tell)
    """
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = {"Authorization": f"{access_token}"}
    tracks = []
    trackIDs = []
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
            trackIDs.append(track_id)
        
        if len(items) < limit:  # If fewer than limit results, we're done
            break
        
        offset += limit

    print(f"Retrieved {len(tracks)} tracks.")
    return tracks, trackIDs

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

def create_blank_playlist(sp, user_id,blankName, blankDescription):
    try:
        # Get the current user
        new_playlist = sp.user_playlist_create(user=user_id,name=blankName,public=False, collaborative=False, description= blankDescription)
        #pprint(new_playlist)  # Debugging response
        new_playlist_uri = new_playlist['uri']
        new_playlist_id = new_playlist['id']
        print(new_playlist_uri, new_playlist_id)
        
        return new_playlist_uri, new_playlist_id
    #print(new_playlist)

    except Exception as e:
        print(f"Error creating playlist: {e}")
        return None
    
def add_to_playlist(sp, playlist_id, song_ids):
    try:
        #sp.playlist_add_items(playlist_id, song_ids)
        chunk_size = 100
        for i in range(0, len(song_ids), chunk_size):
            chunk = song_ids[i:i+chunk_size]
            sp.playlist_add_items(playlist_id, chunk)
            b = f"Added {len(chunk)}/{len(song_ids)}"
            print (b, end="\r")

    except Exception as e:
        print(f"Error adding songs to playlist: {e}")

def get_daylist_share_link(bearer_token):
    """
    This gets the sharable, public link for your Daylist.
    This should be easier to use with spotipy and not require copying an entire playlist! hopefully.
    """

    conn = http.client.HTTPSConnection('spclient.wg.spotify.com')

    headers = {
        'accept': 'application/protobuf',
        'accept-language': 'en',
        'app-platform': 'WebPlayer',
        'authorization': bearer_token,
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
        'entityRequest': [
            {
                'entityUri': f'spotify:playlist:{daylist}',
                'query': [
                    {
                        'extensionKind': 105,
                        'etag': '',
                    },
                ],
            },
        ],
    }

    conn.request(
        'POST',
        'https://spclient.wg.spotify.com/extended-metadata/v0/extended-metadata',
        json.dumps(json_data),
        headers
    )


    response = conn.getresponse()
    decoded_data = response.read().decode('utf-8', errors='ignore') # decode data into a string

    # use regex to extract the ResolvedShare link
    match = re.search(r"ResolvedShare\x12\)\n'spotify:playlist:([^\x00]*)", decoded_data)
    if match:
        playlist_id = match.group(1)  # extract the playlist ID only
        #print("Playlist ID:", playlist_id)
        return playlist_id
    else:
        print("Playlist ID not found.")
        raise Exception("Playlist ID not found.") # not sure if I want to raise exception or return None
        #return None
    
