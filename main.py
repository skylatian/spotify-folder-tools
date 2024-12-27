from better_authenticate import main_authentication
from helpers import *


token = main_authentication()
print(token)

print(get_daylist_share_link(token))