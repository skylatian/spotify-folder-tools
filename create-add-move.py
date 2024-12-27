from helpers import move_playlist, create_blank_playlist, get_all_in_playlist, get_playlist_info, get_daylist
from playlists import folder as dest_folder
from credentials import credentials
from pprint import pprint
from better_authenticate import main_authentication
from playlists import daylist, playlist, daily_mix_hub
# spotipy
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Initialize Spotipy with user credentials
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(credentials.client_id,
                                               credentials.client_secret,
                                               redirect_uri=credentials.redirect_uri,
                                               scope="playlist-read-private playlist-modify-private user-library-read"))

sp.trace = True  # Enable debugging

user = sp.current_user()
user_id = user['id']

token = main_authentication()
print(token)
dl = get_daylist(token, daylist)
pprint(dl)
#playlistURI = create_blank_playlist(sp, user_id)



#move_playlist(token, user_id, playliatURI, dest_folder)


#move_playlist(authTok, username, playlist, folder)


# OK!! here's the plan:
# 1. Create a new playlist. Should have date, time in title. More info in description? not sure what. Maybe only time in description. idk
# 2. Move the playlist to a folder. Could implement a way to search through folders
# 3. Add songs to the playlist (this is smoother - makes the new playlist get hidden faster)

# Authentication:
# - Needs to be revamped to be more efficient. cache tokens until one fails
# - also, check if there's an easier way to get a token that works in the private API
# - Either way, cache the token, check if it needs renewal (either with a timestamp provided with the original call, or by sending a test request to the API)

# we want to figure out how to turn an access token into a bearer token - this MIGHT let us move things using a token from the normal api, but I doubt it.
# I think there's a way to do this with the oauth flow as well
# - maybe it's this? https://developer.spotify.com/documentation/web-api/tutorials/client-credentials-flow NOPE

## THIS IS SUPER HELPFUL!! https://community.spotify.com/t5/Spotify-for-Developers/Does-Client-Credential-flow-allow-access-to-user-tracks-amp/td-p/5386382#

