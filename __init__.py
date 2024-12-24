import os
from os import path
from urllib import response
from flask import Flask, g, redirect, render_template, request, jsonify, json, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from datetime import timedelta
from db import db, mongo


mongo_client=""
def create_app():
    global mongo_client
    app = Flask(__name__)
    
    app.secret_key = "SECRET KEY" # change later
    app.permanent_session_lifetime = timedelta(minutes=5) #how long you stay logged in automatically
    app.config["SESSION_TYPE"] = "filesystem"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///application.db'
    app.config["SECRET_KEY"] = 'YourSecretKey@123'
    
    app.app_context().push()
    app.test_request_context().push()
    
    db.init_app(app)

    return app

app = create_app()

from models import User
db.create_all()
SESSION_TYPE = 'redis'
Session(app)
playlist = ""
session["refreshtoken"]=""
session["accesstoken"]=""
session["user"]=""
session.permanent = True
import main

#Next:
#write and sort all of my playlists alphabetically to my db
#delete jsons, javascriptes, and other trash uneeded files. Where to place my scripts?
#add footer
#where to ptu python script?

        
    #two things:
    #1: I'm gonna have to create a separate page for login, so data[0] on html side doesnt create an error
    #sign up button
    #load time is ridiculuous 

#look through misc notes
#playlists radio thing (if <25), create radio (or, if below needed for x amount of playlists (4 songs x per podcasts) [ so 4 songs per x 5 poddcasts] = 20 length playlists needd, if below this, create radiom and fill in space)

#NEXT: LOADING DIV for get user playlists, and authorize redirect code here (to hide it)
@app.route("/", methods=["POST", "GET"]) #set the authorize redirect code into here. Also, complete authorize code; #set redirect to just http://127.0.0.1/
def index():
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "static", "playlistsSave.json")
    data = json.load(open(json_url)) #change data to mongodb stuff when possible
    token = request.args.get('code')
    
    data = list(mongo.db.playlists.find({ "_id" : "Default" })) #or playlist id or name ( i can make my own search function)
    try:
        data=data[0]["playlists"]
        maxindex=len(data)-1
    except:
        print("error with Data, line 67")
        pass
    maxindex=len(data)-1
    
    if token == None and not "user" in session: #or if user not already logged in
        print("index 1 USER NOT IN SESSION")
        return render_template('authorize.html', data=data, maxindex=maxindex)
    elif token and not "user" in session: #if user is not logged in/has auth code in header
        print("index 2 USER NOT IN SESSION")
        info = main.get_userinfo(token) #saves user if not in database, updates their info if they are
        session.permanent = True
        session["user"]=info["uid"] #...log them in
        print("user now in session:")
        print(session.get('user'))
        #main.set_uid(session.get('user')) #THIS IS IMPORTANT*** -it gets all of the user's playlists. This is commented out to save the amount of API requests we make to spotify :)
        #data=list(mongo.db.playlists.find({ "_id" : info["uid"] })) 
        
        
        #data=data[0]["playlists"] #we cant check to see if we have all of their playlists, if it returns and error of 0 for getingt their playlists
        #main.get_user_playlists(session.get('user'))
        #if len(data) == mongo.db.user.find({ "_id" : info["uid"] })[0]['playlists_amount']: #if the length of data in db equals the playlist number we have on file for them, skip this  step
        #    main.get_user_playlists()
        #im going to want a loading div for while this happens as it gets all the user owned playlists
        #print("we reach here")
        data = list(mongo.db.playlists.find({ "_id" : session.get('user') })) #or playlist id or name ( i can make my own search function)
        data=data[0]["playlists"]
        maxindex=len(data)-1

        
        #print("printing")
        #print(data)
        return render_template('index.html', data=data, maxindex=maxindex)
    elif "user" in session: #if you're already logged in
        print("we reach here")
        data = list(mongo.db.playlists.find({ "_id" : session.get('user') })) #or playlist id or name ( i can make my own search function)
        data=data[0]["playlists"]
        maxindex=len(data)-1
        #print("printing")
        #print(data)
        print("3 user already logged in. user:")
        print(session.get('user'))
        session["user"]=session.get('user')
        return render_template('index.html', data=data, maxindex=maxindex)

@app.route("/createplaylist", methods=["POST", "GET"])
def createplaylist():
    print("user now in session:")
    print(session.get('user'))
    
    data = list(mongo.db.playlists.find({ "_id" : session.get('user') })) #or playlist id or name ( i can make my own search function)
    data=data[0]["playlists"]
        
    #im going to need to split these two up into two different statments
    if not "user" in session: #make this into a "check if logged in ()" function
        print("create playist: USER NOT IN SESSION")
        return redirect(url_for('index'))

    #i can just replace with a session.get('id') or name if the post requests become a problem, because the logic is a bit convoluted
    try:
        id = request.form["id"] #should this be playlsitname as per line 20 of index.html?
        playlistname=request.form["playlistname"]
        session["id"]=id
        return render_template('createplaylist.html', id=id, playlistname=playlistname, data=data) #if it reaches here, it is the first page load
    except:
        pass
    
    
    if request.method == "POST":
        try:
            if request.form["submission"]:
                submission = request.form["submission"]
                if submission == 'yes':
                    #print(session.get('id'))
                    return redirect(url_for('playlist'))
                elif submission == 'no':
                    return redirect(url_for('index', playlist=playlist))
        except:
            print("ERROR") #this error may be caused from the previous page sending post data, and it getting flated with the post data above the if statement, and the post data in this try catch statement
            redirect(url_for('error')) #error
        print("ERROR")
        redirect(url_for('error')) #error
    else:
        return render_template('index.html', data=data)
    print("if we reached here, errror")

@app.route("/playlist") #i could even make a pop up saying its been created, and a green spotify go button to go to playlist
def playlist():
    url=main.run_playlist_script(session.get('id'))
    return redirect(url)

@app.route("/404") #figure out how to pass error message! request.args? sessions?
def error():
    return render_template('404.html') 


 
@app.route("/login", methods=["POST", "GET"]) #make this a modal with similar functionality to the index page
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

@app.route("/podcasts", methods=["POST", "GET"]) #add podcasts page
def podcasts():
    #<a href="{{ url_for('{{ urlarray[i]  }} ') }}"> {{podcasts[i]["name"] }} </a>
    #want to implementth is above, upon click open episode in new window
    message=""
    data = list(mongo.db.playlists.find({ "_id" : session.get('user') })) #or playlist id or name ( i can make my own search function)
    podcasts=data[0]["podcasts"]
    maxindex=len(podcasts)
    
    urlarray=[]

    for podcast in podcasts:
        id = podcast["uri"].split(':')
        id=id[2]
        #print(id)
        url=f"https://open.spotify.com/episode/{id}"
        urlarray.append(url)
        #print(url)
        #we should make an erro rmessage - podcast already added!

    if request.method == "POST": #find a way to automatically load changes but also display message?
        try:
            if request.form["submission"]: #this should be a more efficient search, should display your saved/followed podcasts, and also allowm for a paste of a url 
                submission = request.form["submission"]
                message=main.add_podcast_to_list(submission)

        except:
            if request.form["podname"]:
                pod = request.form["podname"]
                podid= request.form["podid"]
                message=f"deleted: {pod}" #this should probably be an alert asking if you're sure you want to delete podname
                result = mongo.db.playlists.update_one({"_id": session.get('user')}, { '$pull': {"podcasts": { "id" : podid}} } )
                print("deleting")
                print(result)
                
        #reload data based on changes above
 
        data = list(mongo.db.playlists.find({ "_id" : session.get('user') })) #or playlist id or name ( i can make my own search function)
        podcasts=data[0]["podcasts"]
        maxindex=len(podcasts) #i had to set this without -5 because it wouldn't show the last podcast :()
        urlarray=[]
        
        for podcast in podcasts:
            id = podcast["uri"].split(':')
            id=id[2]
            #print(id)
            url=f"https://open.spotify.com/episode/{id}"
            urlarray.append(url)
    
    #todo next: allow a reshuffle of which order the playlists are in!
    return render_template('podcasts.html', message=message, podcasts=podcasts, maxindex=maxindex, urlarray=urlarray)

@app.route("/deleteuser", methods=["POST", "GET"])
def deleteuser():
    print(main.delete_user(session.get('user'))) #fionakennedyyep
    return None

@app.route("/test", methods=["POST", "GET"])
def test():
    #v=main.add_podcast_to_list("FOX News Hourly Update")
    #print(v)
    #v=main.get_podcast("Radio Headspace")
    #print(v)
    
    
    #THIS IS HOW WE FIND ALL PLAYLISTS
    #result = mongo.db.playlists.find({"_id" : session.get("user")}, {"podcasts.id" : "5ulnZFwoLkEv566YCZwTvY"}) #or playlist id or name ( i can make my own search function)
    #print(result)
    #for x in result:
    #    for y in x["podcasts"]:
    #        print(y['name'])
    #search if it exists
    
    #query with specificed document number
    ##THIS IS ANOTHER WAY TO FIND THE PLAYLISTS. 
    #query= {"_id": session.get('user'), "podcasts": { '$elemMatch': {"name": "Radio Headspace"} } }
    #item = { '$set': {"podcasts.name" : "ok"} } #
    #result=mongo.db.playlists.update_one(query, item)
    ##print(result)
    #
    ##THHIS IS HOW WE SELECT A SINGLE ARRAY IN A PLAYLIST.JSON TO EDIT/UPDATE INFO
    #query = {"_id": "31dck52ytkqtrzfat2rb6ox5z72y", 'podcasts.id' : "28hRDWxeu4r8LF3vubetm3"}
    #update = { "$set": {f"podcasts.$.name" : "poop2"}}
    #result2=mongo.db.playlists.update_one(query, update)
    #print(result2)

    ##THHIS IS HOW WE SELECT A SINGLE ARRAY IN A PLAYLIST.JSON TO EDIT/UPDATE INFO
    #query = {"_id": "31dck52ytkqtrzfat2rb6ox5z72y"}
    #update = { "$set": {f"playlists_amount" : "633"}}
    #result2=mongo.db.user.update_one(query, update)
    #print(result2)
    
    #result = list(mongo.db.user.find({ "_id" : "31dck52ytkqtrzfat2rb6ox5z72y"})) 
    #print(result[0]['playlists_amount'])
    
    #playlist stuff (print all playlists given my id)
    #result = list(mongo.db.playlists.find({ "_id" : "31dck52ytkqtrzfat2rb6ox5z72y"})) #or playlist id or name ( i can make my own search function)
    
    #print(len(result[0]["playlists"]))
    
    #print(result[0]["playlists"][1]["name"])
    
    #OMG THIS WORKS SO MUCH BETTER

    #print(result)
    
    #result = mongo.db.playlists.find({ 'playlists': { '$exists': 'True'} }) #or playlist id or name ( i can make my own search function)
    #for x in result:
    #    for y in x["playlists"]:
    #        print(y['name'])
    #        
    #print(result)
    #print(main.delete_user("31dck52ytkqtrzfat2rb6ox5z72y")) #fionakennedyyep
    return render_template('test.html')

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=80)


#print(main.add_podcast_to_list("Radio Headspace"))

#display podcasts you already have
#PROBLEM:
#EVEN PLAYLIST DB IS SET, IT ITTERATES THROUGH ALL PLAYLISTS TO TRY TO ADD TO SET...
#problem 2
#maybe save the amount of playlists from last save - if that number is equal to the amount of playlists now, then it will skip the iteration process

#search function to lists podcasts to choose from?
#if cant find it, search it on spotify and paste link here

#main.delete_user("31dck52ytkqtrzfat2rb6ox5z72y")
#print(mongo.db.playlists.find_one())

#user = User.query.filter_by(username="poop").first()
#print(user)
#db.session.delete(user)
#db.session.commit()
#print(User.query.filter_by(username="poop").delete())
#print(User.query.all())

#result = mongo.db.playlists.find_one({ "_id" : "31dck52ytkqtrzfat2rb6ox5z72y" }, { "playlist" : {'id': 12345} })
#print(result)

#USER STUFF TODO:
#user stuff:
#login/logout functionality
#homepage for new users, what will the background be?
#show if they are logged in on top navbrar

#DELETE user: 
#(if they want to delete their account)
#print("popping")
#user = User.query.filter_by(uid='31dck52ytkqtrzfat2rb6ox5z72y').first()
#print(user)
#db.session.delete(user)
#db.session.commit()
#print(user) just a check
#upon deletion, also delete mongodb

#BACKEND STUFF TODO:
#continue learning flask so i can publicize the website & maker sure i dont miss anything out
#automatically fill songs based on playlist radio /algo reccomendations if there's not enough *or if 0 songs, do recommended playlist for user), propose error so user knows)
#write a function that just automatically updates the playlist every hour until deleted
#make it to where they can choose between their playlist, spotify playlist, or saved playlsits. how to do this?? (like a filter checklist)
#and also how to add the functionality options
#how to add those configureation settings? and make it look nice and neat?
#(later)
#or apple music?
#or generic login, and if you want access to features, login with spotify
#ideas
#i need to make a function: OnStartUp() or maybe OnLogin() that runs - fetch playlist (or on sync with spotify)
#DM
#select from your playlists, or second one by your genres (categorized from most to least) songs by genre
#step 1 pick ur genre, next page is choose ur podcasts, (maybe i can have a fast track button to wher eit jsut saves the settings form last playlist)


#last:
#how to secure sql and mongodb database?
#3. clean some files, and make app more secure (ada and gdpr complian )
#4. learn how to publish website (i may need to add more to start so maybe do this first after db setup)


#before deployment: do these fixes
#next, upon deployment: fix redirect location links:
#script.js RA() function, get code
#index.html if statement
#authcode.py, authtoken.py

#implement relational pathing ("from .db import db")



#soupy dommy mommy notes
#two columns styled after mytopspotify.io
#select from your playlists, or second one by your genres (categorized from most to least) songs by genre
#step 1 pick ur genre, next page is choose ur podcasts, (maybe i can have a fast track button to wher eit jsut saves the settings form last playlist)


#get permission from spotify to monetize or advertize app?