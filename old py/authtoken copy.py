import json
from types import SimpleNamespace
from urllib.parse import urlencode
import webbrowser
from dotenv import load_dotenv
import os
import base64
from requests import post, get
import requests
from flask_sqlalchemy import SQLAlchemy
from flask import session
from __init__ import app
#from . import db
from db import db
from models import User

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
#get this after getting user data
user_id = "31dck52ytkqtrzfat2rb6ox5z72y"
#store this code in a secure database
code="AQCXBezXXLfPSGAo8jS1qHoXFb6nlwBn8W8txObA3ZawAMtYfyp-vKL08iTDFZa1OdgFpoP3DkVvqJYsPrDW_BiTKF49Fhs0u7f44Ywjss0ywTQHE5B8U4zy4WlkmLjlH9t33ar46o3vhClVOmbmRnmKU41T6DuqqZdRnAiimkm3wZN5HLKuFpPdNTQ2IftoNJbltOeu2mQQBgQz3sOV46VjtLQQPqng9V3sq6IciIhGNvFAU2IguRceNaFhpwdP9OL3qVQmO0C33Zjv0-bdyMgChX2VjvCKajSvlw"

refresh_token = "" #set this to database value

def get_token():
    global refresh_token
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"code": get_user_db_info().authcode,
            "redirect_uri": "http://localhost:7777/callback",
            "grant_type": "authorization_code" } #was client_credentials
    result = post(url, data=data, headers=headers)
    json_result = json.loads(result.content)
    token = checktoken(json_result) #this converts the result into an access_token or refresh_token via parse if successful

    return token

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def checktoken(json_result): #makes sure we recieved a token from spotify response url
    global refresh_token
    try:    #if this results in an error, then token is successful
        if(json_result['error']=="invalid_grant"):
            pass
            #print()
            #print("REFRESHING TOKEN") #this will run the get_code function to authorize again
            #print()
    except: #the above is an error, token is successful, save refresh token
        #print("No Errors In get_token()")
        set_refresh_token(json_result['refresh_token']) #save refresh token
        token=json_result['access_token']
    else:  #the above is not an error, and we need to return the refresh token
        token=request_refreshed_access_token() #set token to the new refresh token value
        
    return token

def request_refreshed_access_token(): #if this doesn't work then I know I'll need a new authcode
    refresh_token=get_refresh_token()
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "refresh_token",
            "refresh_token": refresh_token}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result['access_token']
    return token

def get_refresh_token(): #get from db, we'll need current user info
        global refresh_token
        f= open("spotifyrefreshtoken.txt","r")
        refresh_token=f.read() #open the file and retrieve refresh token from save 
        f.close()
        return refresh_token 
    
def set_refresh_token(refreshed_token): #save to db, we'll need current user info
        f= open("spotifyrefreshtoken.txt","w+") #save refresh token to text file
        f.write(refreshed_token) #save refresh token to a file for later
        f.close() # close file
#use user session to get db user info once snd srore it in session as “user”
def get_autbbase64():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    return auth_base64

def get_userinfo_nodb(): #how to get only my playlists, -> NOTE: {offset} simply offsets the playlist numbers listed, NOT the page (so offset=5 means it will omit the first 5 playlist, not page of playlists. offset should =limit%2=0)
    url = "https://api.spotify.com/v1/me"
    headers = {"Authorization": "Bearer " + get_token()}#, "Content-Type": "image/jpeg"} 
    result = requests.get(url, headers=headers)
    json_result = json.loads(result.content)
    #print('Playlist Image Updated')
    #set these values equal to database stuff
    username = json_result['display_name']  #this will be important when filtering playlists by "created by user"
    uid = json_result['id']
    image = json_result['images'][0]['url'] #i can also replace url with height and width for dimensions. They are 64 x 64 normally though
    return json_result #this will just run one time on auth, and all subsequent data will be retrieved from db

def get_userinfo(): #how to get only my playlists, -> NOTE: {offset} simply offsets the playlist numbers listed, NOT the page (so offset=5 means it will omit the first 5 playlist, not page of playlists. offset should =limit%2=0)
    url = "https://api.spotify.com/v1/me"
    headers = {"Authorization": "Bearer " + get_token()}#, "Content-Type": "image/jpeg"} 
    result = requests.get(url, headers=headers)
    json_result = json.loads(result.content)
    #print('Playlist Image Updated')
    #set these values equal to database stuff
    data= {
        "name" : json_result["display_name"],
        "uid" : json_result["id"],
        "image" : json_result['images'][0]['url']
    }

    username = json_result['display_name']  #this will be important when filtering playlists by "created by user"
    uid = json_result['id']
    image = json_result['images'][0]['url'] #i can also replace url with height and width for dimensions. They are 64 x 64 normally though
    return data #this will just run one time on auth, and all subsequent data will be retrieved from db

def save_userinfo(token, user):
    if not User.query.filter_by(uid=user["uid"]).first(): #if they don't exist, save them
        username = User(username=user["name"], uid=user["uid"], image_file=user["image"], authcode=token) #this can go into get_userinfo now
        db.session.add(username)
        db.session.commit()
    return None

def get_user_db_info(): #takes sesssion 
    #only works if user is logged into session
    try:
        user = session["uid"]
        user = User.query.filter_by(uid=user).first()
        #admin.email = 'my_new_email@example.com'
        #db.session.commit()
        return user
    except:
        print("error: no user in session? no user found in db?")
    return None
#app.app_context().push()
#print(User.query.all()) #this works now!!
#print(db.session.query())
# OTHER CHANGES I COULD MAKE
#if refresh_token_on:
#        if(json_result['error']=="invalid_grant"):
#            print()
#            print("NEED NEW ACCESS CODE") #this will run the get_code function to authorize again
#            exit()
#Use the refresh_token_on as a saved text file boolean value; and use get/set methods to keep track of if we're using a refresh token or not.
#if the refresh token ever fails currently, we'll expect an error from spotify but that's all.