from better_authenticate import main_authentication
from helpers import *
from pprint import pprint
from credentials import username
from playlists import daylist_folder

token = main_authentication()
print(token)

save_and_move_daylist(token)