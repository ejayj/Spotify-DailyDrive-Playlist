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
from flask_session import Session
# from __init__ import app
#from . import db
from db import db, mongo
from models import User
from datetime import datetime

load_dotenv()

#put this in .env file ventually
#client_id = os.getenv("CLIENT_ID")
#client_secret = os.getenv("CLIENT_SECRET")

client_id="1f69a9d216f6424f92fb177324f1e06c"
client_secret="6049a8ed4fc9431b92cd0476b6ba039a"
#get this after getting user data
code = ""
refresh_token = "" #set this to database value
#uid= get_uid()
accesstoken = ""
user_db = None
mongouser=mongo.db.user
mongoplaylist=mongo.db.playlists
uid=""
    
def get_token():
    #saved_in_code=code
    if session.get('user'): #if they are logge din
        #print('user here:')
        #print(session.get('user'))
        #print("LOOK AT MEEEE")
        code=get_db_authcode() #auto gets code for use rin session
        #print("session code:")
        #print(code)
        #get saved code
    else:
        print(session.get('user'))
        print(get_uid())
        print(get_sessionid())
        print("how did we end up here? No user in session, yet we're getting an auth code.")
        exit(0)
        
    auth_string = f"{client_id}:{client_secret}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"code": code,
            "redirect_uri": "http://127.0.0.1:5000/",
            "grant_type": "authorization_code"} #was client_credentials
    result = post(url, data=data, headers=headers)
    json_result = json.loads(result.content)
    try:
        #set_refreshtoken(json_result['refresh_token']) #save this to database after we get user
        #print(f"0 setting refreshtoken {refresh_token}")
        pass
    except:
        #print("no refresh token")
        pass
    # print("token:")
    # print(json_result)
    # print("code:")
    # print(code)
    # print("json result")
    token = checktoken(json_result) #this converts the result into an access_token or refresh_token via parse if successful
    session['token']=token #save access token
    # print("token test")
    # print(token)
    # print("token to be passed:")
    # print(token)
    return token
    
def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def checktoken(json_result): #makes sure we recieved a token from spotify response url
    #print(json_result)
    try:
        if json_result['error']=='invalid_grant':
            #print('its error')
            #print()
            #print("REFRESHING TOKEN") #this will run the get_code function to authorize again
            #print()
            #the above error exists, and we need to return the refresh token
            token=request_refreshed_access_token()
        elif json_result['error']:
            print("SOME SORT OF CHECK TOKEN ERROR")
            print(json_result)
        #else:
            #print("no error")
    except:
        print("no error2 get authtoken refreshed.. what si the expiration?")
        
        #the above try is an error, token is successful, save refresh token
        #session['refreshtoken']=json_result['refresh_token'] #save refresh token
        
        #print(f"1 setting refreshtoken {refresh_token}")   
        
        if session.get('user'):
            #save to db, otherwise just save to session. get db later
            user=get_user_db_info(session.get('user'))
            user.refreshtoken=json_result['refresh_token']
            user.accesstoken=json_result['access_token']
            
        session['refreshtoken']=json_result['refresh_token'] #save refresh token
        session['accesstoken']=json_result['access_token']
        token =json_result['access_token']
        
            
    #i see the problem. when logging in if i need
    #a refresh token, i will have to acess the old, last
    #available access token to me OR just re-login.
    #i think re-logging in is the way... or store in db?
    
    #if user is logged in, save refresh token to db and session
    #if user is not logged in, save refresh token to session. Upon logout/session time out or use end session
    # save last refresh token to db
    #print("check token:")
    #print(token)
    return token

def request_refreshed_access_token(): #if this doesn't work then I know I'll need a new authcode
    #print(f"refresh token: {refresh_token}")
    #print()
    #refresh_token=session.get("refreshtoken") #getrefresh token
    
    #try to get refresh token from db first, if not-> check session?
    
    if session.get("refreshtoken"): 
        refresh_token=session.get("refreshtoken")
    elif not session.get("refreshtoken"): #if there's no refreshtoken in session, check db
        if session.get('user'): #if they are logged in 
            #save to db, otherwise just save to session. get db later
            user=get_current_user_db_info()
            if not user.refreshtoken=="REFRESH_TOKEN": #if refresh token is not null, get it 
                refresh_token=user.refreshtoken
    else:
        print("error: no refresh token in db or session. is user in db and or logged in?")
        return None
    #or get it from database?
    #print("this is refresh token:")
    #print(refresh_token)
    
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
    # print("refresh token results:")
    # print(json_result)
    try:
        token = json_result['access_token']
        session['tokentimeout']=[json_result['expires_in'],datetime.now().strftime("%X")] #does this work?
        session["rtoken"]=token
        #print(session.get('tokentimeout'))
    except:
        print("error")
        print(json_result) #im probably reaching this error because they need to retrieve this data from the databse
        token = None
        
    #print("refresh token")
    #print(token)
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

def get_token_firsttime(code):
    #saved_in_code=code
        
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"code": code,
            "redirect_uri": "http://127.0.0.1:5000/",
            "grant_type": "authorization_code",
            "scope": "playlist-read-private playlist-modify-public playlist-modify-private ugc-image-upload user-read-private playlist-read-private"} #was client_credentials
    result = post(url, data=data, headers=headers)
    json_result = json.loads(result.content)
    try:
        #set_refreshtoken(json_result['refresh_token']) #save this to database after we get user
        #print(f"0 setting refreshtoken {refresh_token}")
        pass
    except:
        #print("no refresh token")
        pass
    #print("token:")
    #print(json_result)
    #print("code:")
    #print(code)
    #print("json result")
    token = checktoken(json_result) #this converts the result into an access_token or refresh_token via parse if successful
    session['token']=token #save access token #should be saved as refresh taken
    
    #print("token test")
    #print(token)
    #print("token to be passed:")
    #print(token)
    return token

def get_userinfo(code): #how to get only my playlists, -> NOTE: {offset} simply offsets the playlist numbers listed, NOT the page (so offset=5 means it will omit the first 5 playlist, not page of playlists. offset should =limit%2=0)
    global  uid
    print("GETTING USER INFO")
    #print(session.get('user'))
    set_code(code)
    #print(code)
    url = "https://api.spotify.com/v1/me"
    headers = {"Authorization": "Bearer " + get_token_firsttime(code)}#, "Content-Type": "image/jpeg"} 
    result = requests.get(url, headers=headers)
    json_result = json.loads(result.content)
    #print('Playlist Image Updated')
    #set these values equal to database stuff
    #print(json_result)

    #print(json_result)
    try:
        data= {
            "name" : json_result["display_name"],
            "uid" : json_result["id"],
            "image" : json_result['images'][0]['url']
        }
    except:
        data= {
            "name" : json_result["display_name"],
            "uid" : json_result["id"],
            "image" : "None"
        }
    
    if not User.query.filter_by(uid=data["uid"]).first(): #if they don't exist, save them
        user = User(username=data["name"], uid=data["uid"], image_file=data["image"], authcode=code, refreshtoken=refresh_token, accesstoken=session.get('accesstoken')) #this can go into get_userinfo now
        db.session.add(user)
        db.session.commit()
        set_uid(data["uid"])
        set_user_db(User.query.filter_by(uid=data["uid"]).first())
        sqlid=(User.query.filter_by(uid=data["uid"]).first()).id
        createMongoUser(sqlid,data["uid"],data["name"])
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
        #refresh user playlists  
    #session["user"]=data["uid"]
    return data #this will just run one time on auth, and all subsequent data will be retrieved from db

def set_code(c):
    global code
    code = c
    return c

def get_code():
    global code
    return code

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

def get_uid():
    global uid
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
        #print(uid)
    else:
        get_userinfo(code) #refreshes set user id if not already set and user is logged in
    return accesstoken

#try:
#    uid=session.get('user')
#    print(session["user"])
#    print('try to')
#except:
#    print("could not set uid to session")
#    print("uid:")
#    print(uid)
#fawkk. SO THE PROBELM IS i need to get a token to get the user id becasuef ucking flask didnt store it. im going to have to pass it in session
#def save_userinfo(token, user):
#    if not User.query.filter_by(uid=user["uid"]).first(): #if they don't exist, save them
#        username = User(username=user["name"], uid=user["uid"], image_file=user["image"], authcode=token) #this can go into get_userinfo now
#        db.session.add(username)
#        db.session.commit()
#    return None

def get_sessionid():
    return session.get('user')

#def get_uid():
#    print("get_uid:")
#    print(uid)
#    print(get_sessionid())
#    return uid

def save_playlist_amount(amount):
    query = {"_id": session.get('user')}
    update = { "$set": {f"playlists_amount" : amount}}
    result2=mongo.db.user.update_one(query, update)
    return result2

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

def get_current_user_db_info():
    try:
        user = User.query.filter_by(uid=session.get('user')).first()
        #print(user)
    except:
        print("ERROR: NO USER IN SESSION , CANT RETURN USER INFO")
        return None
    return user

def get_db_authcode():
    user=get_current_user_db_info()
    try:
        code=user.authcode
        #print(code)
    except:
        print("there is no user.authcode (is there an error above me?)")
        #print(user)
        return None
    return code
#print(session.get('user_id',0))
#print("session:")
#print(session.get('user'))
            
#def test():
#    session['refreshtoken']='poop'
#    return session['refreshtoken']

def save_playlistid_db(playlistid):
    user=get_current_user_db_info()
    user.ddplaylistid=playlistid
    db.session.commit()
    #try catch, if error, return none. but the first error will be if there is no user in session
    return "success"

def get_saved_db_playlistid():
    user=get_current_user_db_info()
    playlistid=user.ddplaylistid
    if playlistid=="playlist":
        print("ERROR, no playlist id found in db")
        return None
    return playlistid

def createMongoUser(sqlid, uid, name): #creates the mongo user
    user = { 
        "_id" : uid,
        "sqlid" : sqlid,
        "name" : name,
        "date_joined" : datetime.now().isoformat(),
        "playlists_amount" : "null",
        "playlist_id" : []
    }
    
    playlist = {
        "_id" : uid,
        "playlists" : [], #playlists blanks
        "podcasts" : []
    }
    
    resultA=mongo.db.user.insert_one(user)
    resultB=mongo.db.playlists.insert_one(playlist)

    if "acknowledged=True" in str(resultA) and "acknowledged=True" in str(resultB):
        print("Scuess")
        return True
    
    return None

def delete_user(userid):
    user=User.query.filter_by(uid=userid).first()
    db.session.delete(user)
    db.session.commit()
    resultA=mongo.db.user.delete_one({"_id": userid})
    resultB=mongo.db.playlists.delete_one({"_id": userid})
    if "acknowledged=True" in str(resultA) and "acknowledged=True" in str(resultB):
        print("Sucess - user deteleted")
        return True
    print("error")
    print(resultA)
    print(resultB)
    return None

#uid= get_sessionid()


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


