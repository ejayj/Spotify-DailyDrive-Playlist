import json
from urllib.parse import urlencode
import webbrowser
from dotenv import load_dotenv
import os
import base64
import requests
from flask import session
#from bs4 import BeautifulSoup

#from main or authtoken import getuserdbinfo
#user_id = authtoken.get_user_db_info().uid

load_dotenv()

client_id = "1f69a9d216f6424f92fb177324f1e06c"
client_secret = "6049a8ed4fc9431b92cd0476b6ba039a"
#user_id = session["uid"]

auth_headers = {
    "client_id": client_id,
    "response_type": "code",
    "redirect_uri": "http://127.0.0.1:80/authorize",
    "scope": "playlist-read-private playlist-modify-public playlist-modify-private ugc-image-upload user-read-private"
}

#client = requests.Session()
#webbrowser.open("https://accounts.spotify.com/authorize?" + urlencode(auth_headers))

def runauth():
    return "https://accounts.spotify.com/authorize?" + urlencode(auth_headers)