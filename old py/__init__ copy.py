import os
from os import path
from urllib import response
from flask import Flask, redirect, render_template, request, jsonify, json, session, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta

#from config import app
from db import db

#security stuff:
#secret key
#and access code state in javascript file
#hashing db and cookies/session info

#app = Flask(__name__) 

#db = SQLAlchemy(app)
def create_app():
    app = Flask(__name__)
    
    app.secret_key = "SECRET KEY" # change later
    app.permanent_session_lifetime = timedelta(minutes=1) #how long you stay logged in automatically
    app.config["SESSION_TYPE"] = "filesystem"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///application.db'
    
    app.app_context().push()
    app.test_request_context().push()
    #with app.app_context():
        #db.init_db()
    #    db.init_app(app)
    db.init_app(app)
    #session(app)
    # you can do any blueprint registration if any:
    # app.register_blueprint(example_blueprint)
    return app

app = create_app()

#db.init_app(app)
from models import User
db.create_all()



#with app.app_context():
#   db.init_app(app)
#    db.create_all()

#@app.before_first_request  #or 
#def create_database():
#     db.create_all()

#db.create_all()


#i can reload this data after its been populated with userid pages
#reload(themodule)
#from themodule import AClass

#has to be imported after database starts
#authtoken=""
#is this cookies?


#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite3.db'

#app.app_context().push()

#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
#db = SQLAlchemy(app)
#app.app_context().push()
#db.init_app(app) # to add the app inside SQLAlchemy() # db.app(ap)

#so next for db, after user authorization and get_userinfo(), if user is not in db
# if uid is not is in db
#create a new user instance with this user's data

playlist = ""
session["refreshtoken"]=""
session["accesstoken"]=""
#**** DB FUNCTIIONS******
def getdb():
    return None

import main

#create random cookie hash upon sucessful spotify login
#if you can get this cookie from the web browser:
# set everything equal to the user whose cookie matches this value

#NEXT: do notes on this function below
@app.route("/", methods=["POST", "GET"]) #set the authorize redirect code into here. Also, complete authorize code; #set redirect to just http://127.0.0.1/
def index():
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "static", "playlistsSave.json")
    data = json.load(open(json_url))
    token = request.args.get('code')
    
    #change this to: if user is not logged in & has no auth code in db
    if token == None and not "user" in session: #or if user not already logged in
        #return redirect(authcode.runauth()) #{{ visibility }}
        #visibility="is-active" #show modal
        print("index 1 USER NOT IN SESSION")
        return render_template('authorize.html', data=data)
    elif token and not "user" in session: #if user is not logged in/has auth code in header
        info = main.get_userinfo(token) #saves user if not in database, updates their info if they are
        session.permanent = True
        session["user"]=info["uid"] #...log them in
        print("index 2 USER NOT IN SESSION")
        #print(session["user"])
        #print("next:")
        #print(main.get_sessionid())
        
        main.set_uid(session["user"])
        #print("next:")
        #print(main.get_sessionid())
        main.get_user_playlists()
        #im going to want a loading div for while this happens as it gets all the user owned playlists
        return render_template('index.html', data=data)
    elif "user" in session: #if you're already logged in
        return render_template('index.html', data=data)

@app.route("/createplaylist", methods=["POST", "GET"])
def createplaylist():
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "static", "playlistsSave.json")
    data = json.load(open(json_url))
    
    #print("next1:")
    #print(main.get_sessionid())
    if not "user" in session:
        print("create playist: USER NOT IN SESSION")
        return render_template('authorize.html', data=data)

    try:
        index = request.form["playlist"]
        index = int(index)-1
        global playlist
        playlist = data["playlists"][int(index)]
        playlistid=data["playlists"][int(index)]["id"]
        return render_template('createplaylist.html', index=index, id=playlistid, playlist=playlist, data=data) #if it reaches here, it is the first page load
    except:
        pass
    
    if request.method == "POST":
        try:
            submission = request.form["submission"]
            if submission == 'yes':
                return redirect(url_for('playlist'))
            elif submission == 'no':
                return redirect(url_for('index', playlist=playlist))
        except:
            redirect(url_for('error')) #error
        redirect(url_for('error')) #error
    else:
        return render_template('index.html', data=data)
    redirect(url_for('error')) #error

@app.route("/playlist") #i could even make a pop up saying its been created, and a green spotify go button to go to playlist
def playlist(): #should redirect to some spotify page (or put it in the address bar)
    global playlist
    #print("last:")
    #print(main.get_sessionid2()) 
    url=main.run_playlist_script(playlist["id"])
    return redirect(url) #or url_for(url) ?

@app.route("/404") #figure out how to pass error message! request.args? sessions?
def error():
    return render_template('404.html') 

@app.route("/login", methods=["POST", "GET"])
def login():
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "static", "playlistsSave.json")
    data = json.load(open(json_url))
    token = request.args.get('code')
    if token and not "user" in session: #if user is not logged in/has auth code in header
        info = main.get_userinfo()
        main.save_userinfo(token, user=info) #save user in db if not already in db, and...
        session.permanent = True
        session["uid"]=info["uid"] #...log them in
        return render_template('index.html', data=data)
    elif token == None and "user" in session:
        return redirect(url_for('index'))
    return render_template('authorize.html', data=data)
    
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=80)

#print()
#print("query all")
#print(User.query.all()) 

#print(User.query.filter_by(email="itworks@gmail.com").first())
#print(session.get('user'))
#print(session["user"])


#print(main.set_uid(session.get('user')))
#print(main.set_uid(session["user"]))
#print("next:")
#print(main.get_uid())
#print(main.get_sessionid())

#print("popping")
#user = User.query.filter_by(uid='31dck52ytkqtrzfat2rb6ox5z72y').first()
#print(user)
#db.session.delete(user)
#db.session.commit()
#print(user) just a check
#NEXT:
#IF Person is not logged in
#       show login modal
#ELSe
#Display home creation page
#show if they are logged in on top navbrar
#how to show you're logged into spotify



#next, how to query/print a list?; then sync database with the fetch/playlist function (should update/run every startup or login)
#i need to make a function: OnStartUp() or maybe OnLogin() that runs - fetch playlist (or on sync with spotify)
#i also need to write  afunction that saves the authcode to a db and plugs it in where needed
#and also saves the token, and refresh token to db
#needs to save uid too
#token, refresh token

#need to make a link to another user table?
#below are some table ideas


#table for json data? where to store json data?
#remember the multple playlsits config: a json for all playlist, a json for yours, a playlist for spotify saved, all spotify, and then other random saved playlist
#cookies? store on the user's side? this may save space for me in the meantime if im hosting website
#html5 local storage? session storage[which whipes at end of session: this may save storage data for me/thes user in the future, but also adds to applicaiton loag lag such as the music shift app's lag? (also an html5 thing)
#login with spotify button?
#or apple music?
#or generic login, and if you want access to features, login with spotify

#it works!!!
#Up next:
#1. - store authcode in in a database
#maybe skip to 4. wait - is it gonna get me playlist if its my first login/and all of them are empty?   
# make it to where if the website gives you an auth error, you need to sign in again. set up database for email/password?
#2. upon login, app should gather all of the user's playlist
#3. clean some files, and make app more secure (ada and gdpr complian )
#3a. make website secure
#4. learn how to publish website (i may need to add more to start so maybe do this first after db setup)

#minor stuff:
#ui/ux styling

#last:
#continue learning flask so i can publicize the website:
# II. i'll need to create a database to store all the json and txt files that i have
#see beolow III.
#login to spotify - i should make an error code where if the website lets you in for some reasom without logging in, and you try to run a playlist, itll redirect you to login with spotify
#make option to just choose from spotify playlists or others that you have saved (this will be a 3 part checklist)
#there's an error where if the playlist doesn't hve enough songs, it sends the error and creates a radio of said playlist, then adds songs from said radio to that playlist, then deletes radio in case user doesnt want it (or maybe i can fill it with suggestions based off the song using spotify ai; i think some guy did that in a tutorial before)
#be sure to change th spotify redirect routing to the website


#IMPORTANT BAC
#write a function that just automatically updates the playlist every hour until deleted
#make it to where they can choose between their playlist, spotify playlist, or saved playlsits. how to do this??
#and also how to add the functionality options
#how to add those configureation settings? and make it look nice and neat?

#soupy dommy mommy notes
#make a modal login for spotify, you login
#mytopspotify.io
#website inspo
#select from your playlists, or second one by your genres (categorized from most to least) songs by genre
#step 1 pick ur genre, next page is choose ur podcasts, (maybe i can have a fast track button to wher eit jsut saves the settings form last playlist)
#OR
#write a function that just automatically updates the playlist every hour until deleted
#two columns styled after myspotoify .io



#if the playlist is too short, dfo that radio thing


#write 404 errors for errors from db queries


#read data

#user = User.query.filter_by(email="itworks@gmail.com").first() #or User.query.all() and filter with a for loop, or db.session.scalars(db.select(User).where(User.email == "itworks@gmail.com")).first() for more control
#print(user.username) #or user.email to return email, etc.
#print("i reach here2")


#write data 

#username = User(username="james", email="james@james.com", password="password")
#db.session.add(username)
#db.session.commit()\
    
    
    
# FIRST - set up database login info, authcode and authtoken grabbing - MAKE IT SECURE!!! #will probably have to do a lot of hashing of project
# SECOND - how to make store data secured and access it 
# THIRD - how to store json data-> put in sql? or use mongodb? these will be potentially large json files
# question? - separate json files for playlist types? or just get all playlist and have different filters/query types
# #NOW the next question is how should i store the playlist information? maybe 



#redirect location links:
#script.js RA() function, get code
#index.html if statement
#authcode.py, authtoken.py