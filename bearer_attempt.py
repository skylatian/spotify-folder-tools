# https://github.com/vimfn/get-spotify-refresh-token/blob/main/main.py

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import dotenv_values
from credentials import credentials

config = dotenv_values(".env")

# Initialize Spotipy with user credentials
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(credentials.client_id,
                                               credentials.client_secret,
                                               redirect_uri=credentials.redirect_uri,
                                               scope="playlist-modify-private, user-library-modify, user-library-read"))


current_user = sp.current_user()

assert current_user is not None

print(current_user["id"], "token saved in '.cache' file.")