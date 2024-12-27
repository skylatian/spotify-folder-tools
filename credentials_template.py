

username = "" # spotify username
password = "" # spotify password

class credentials:
     def __init__(self):
        self.client_secret = 'client secret' # these three are for the normal, public Spotify API. Using this for the time being until I get things working smoothly (?) with the private API
        self.client_id = 'client ID'
        self.redirect_uri = 'http://127.0.0.1:8080/callback' # or whatever you set it to
        self.username = username 
        self.password = password

credentials = credentials()