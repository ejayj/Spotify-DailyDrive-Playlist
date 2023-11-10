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
#from __init__ import app
#from . import db
from db import db
from models import User

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
#get this after getting user data
code = ""
refresh_token = "" #set this to database value
#uid= get_uid()
accesstoken = ""
user_db = None

    
def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"code": code,
            "redirect_uri": "http://192.168.1.19:80/",
            "grant_type": "authorization_code" } #was client_credentials
    result = post(url, data=data, headers=headers)
    json_result = json.loads(result.content)
    try:
        #set_refreshtoken(json_result['refresh_token']) #save this to database after we get user
        #print(f"0 setting refreshtoken {refresh_token}")
        pass
    except:
        #print("no refresh token")
        pass
    token = checktoken(json_result) #this converts the result into an access_token or refresh_token via parse if successful
    set_accesstoken(token) #save access token
    return token
    
def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def checktoken(json_result): #makes sure we recieved a token from spotify response url
    global refresh_token
    try:    #if this results in an error, then token is successful
        if "invalid_grant" in json_result:
            pass
            #print()
            #print("REFRESHING TOKEN") #this will run the get_code function to authorize again
            #print()
    except: #the above is an error, token is successful, save refresh token
        #print("No Errors In get_token()")
        try: #if this is an error, then db has not added user yet
            user=get_user_db_info(uid)
            user.refreshtoken=json_result['refresh_token'] #save refresh token
            db.session.commit()
            print(json_result['refresh_token'])
            token=json_result['access_token']
            print(token)
            set_refreshtoken(json_result['refresh_token'])
            #print(f"1 setting refreshtoken {refresh_token}")
        except:
            set_refreshtoken(json_result['refresh_token'])
            #print(f"2 setting refreshtoken {refresh_token}")
    else:  #the above is not an error, and we need to return the refresh token
            token=request_refreshed_access_token()
            
        
    return token

def request_refreshed_access_token(): #if this doesn't work then I know I'll need a new authcode
    try:
        print(uid)
        print("TRY TO GET USER TOKEN")
        print(user_db)
        print("session:")
        print(session.get('user'))
        refresh_token=user_db.refreshtoken #get refresh token
        print(f"refresh token: {refresh_token}")
    except:
        pass #refresh token will be the global variable
    
    #print(f"refresh token: {refresh_token}")
    #print()
    refresh_token=['refreshtoken'] #getrefre
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
    #print(json_result)
    try:
        token = json_result['access_token']
    except:
        print(json_result) #im probably reaching this error because they need to retrieve this data from the databse
        print("error")
        token = None
    return token


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

def get_userinfo(code): #how to get only my playlists, -> NOTE: {offset} simply offsets the playlist numbers listed, NOT the page (so offset=5 means it will omit the first 5 playlist, not page of playlists. offset should =limit%2=0)
    global  uid
    set_code(code)
    url = "https://api.spotify.com/v1/me"
    headers = {"Authorization": "Bearer " + get_token()}#, "Content-Type": "image/jpeg"} 
    result = requests.get(url, headers=headers)
    json_result = json.loads(result.content)
    #print('Playlist Image Updated')
    #set these values equal to database stuff
    #print(json_result)

    data= {
        "name" : json_result["display_name"],
        "uid" : json_result["id"],
        "image" : json_result['images'][0]['url']
    }
    if not User.query.filter_by(uid=data["uid"]).first(): #if they don't exist, save them
        username = User(username=data["name"], uid=data["uid"], image_file=data["image"], authcode=code, refreshtoken=refresh_token) #this can go into get_userinfo now
        db.session.add(username)
        db.session.commit()
        set_uid(data["uid"])
        set_user_db(User.query.filter_by(uid=data["uid"]).first())
    else: #update user data
        user = User.query.filter_by(uid=data["uid"]).first()
        user.name = data["name"]
        user.image_file=data["image"]
        user.authcode=code
        user.refreshtoken=refresh_token
        db.session.commit() #save changes
        set_uid(data["uid"])
        set_user_db(user)
    set_uid(data["uid"])    
    session["user"]=data["uid"]
    return data #this will just run one time on auth, and all subsequent data will be retrieved from db

def set_code(c):
    global code
    code = c
    return c

def set_refreshtoken(c):
    global refresh_token
    refresh_token = c
    return refresh_token

def set_accesstoken(c):
    global accesstoken
    accesstoken = c
    return accesstoken

def set_uid(c):
    global uid
    uid = c
    return uid

def set_user_db(c):
    global user_db
    user_db = c
    return user_db

def get_accesstoken():  
    uid=session.get('user')
    set_uid(uid)
    accesstoken = get_token()
    print(uid)
    #get_userinfo(code) #refreshes set user id if not already set and user is logged in
    return accesstoken

def get_accesstokenold():  
    global uid
    if not uid == None:
        
        uid=session.get('user')
        accesstoken = get_token()
        print(uid)
    else:
        get_userinfo(code) #refreshes set user id if not already set and user is logged in
    return accesstoken

try:
    uid=session.get('user')
    print(session["user"])
    print('try to')
except:
    print("could not set uid to session")
    print("uid:")
    print(uid)
#fawkk. SO THE PROBELM IS i need to get a token to get the user id becasuef ucking flask didnt store it. im going to have to pass it in session
#def save_userinfo(token, user):
#    if not User.query.filter_by(uid=user["uid"]).first(): #if they don't exist, save them
#        username = User(username=user["name"], uid=user["uid"], image_file=user["image"], authcode=token) #this can go into get_userinfo now
#        db.session.add(username)
#        db.session.commit()
#    return None

def get_sessionid():
    return session.get('user')

uid= get_sessionid()

def get_uid():
    print("get_uid:")
    print(uid)
    print(get_sessionid())
    return uid

def get_user_db_info(userid): #takes sesssion 
    #only works if user is logged into session
    try:
        #user = session["uid"]
        #print(f" userid: {user}")
        #does this work? and change global uid in time? what if get user info isnt called? then what? such as if the user is already logged in....
        user = User.query.filter_by(uid=userid).first()
        #admin.email = 'my_new_email@example.com'
        #db.session.commit()
        
        #print(f"user: {user}")
        #print()
        #print(user.name)
        #print(user.refreshtoken)
        return user
    except:
        print("error: no user in session? no user found in db?")
    return None

#print(session.get('user_id',0))
print("session:")
print(session.get('user'))
            
def test():
    session['refreshtoken']='poop'
    return session['refreshtoken']

#print("new test")
#print(test())
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