from helpers import move_playlist, create_blank_playlist, get_all_in_playlist, get_playlist_info, get_daylist, add_to_playlist, get_daylist_info
from playlists import folder as dest_folder
from credentials import credentials
from pprint import pprint
from better_authenticate import main_authentication
from playlists import daylist, playlist, daily_mix_hub
# spotipy
import spotipy
from spotipy.oauth2 import SpotifyOAuth

## this does things differently - it actually copies your Daylist to a new playlist, then moves the new playlist intp your desired folder
## this is contrast to the other method, which gets the sharable link for the Daylist and saves it to your library, then moves it into your folder

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
dl_tracks, dl_trackIDs = get_daylist(token, daylist)

pprint(dl_trackIDs)

# create and move blank playlist

daylist_info = get_daylist_info(token, daylist)

playlistURI, plID = create_blank_playlist(sp, user_id,daylist_info['name'],daylist_info['description'])
add_to_playlist(sp, playlist_id=plID, song_ids=dl_trackIDs)
move_playlist(token, user_id, playlistURI, dest_folder)