import os
from os import path
from urllib import response
from flask import Flask, g, redirect, render_template, request, jsonify, json, session, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
#from flask_pymongo import PyMongo
from pymongo import MongoClient
#from pymongo.errors import DuplicateKeyError, OperationFailure

#from config import app
from db import db

mongo_client=""
#security stuff:
#secret key
#and access code state in javascript file
#hashing db and cookies/session info

def create_app():
    global mongo_client
    app = Flask(__name__)
    
    app.secret_key = "SECRET KEY" # change later
    app.permanent_session_lifetime = timedelta(minutes=1) #how long you stay logged in automatically
    app.config["SESSION_TYPE"] = "filesystem"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///application.db'
    
    mongo_client = MongoClient("mongodb://localhost:27017/")
    
    app.app_context().push()
    app.test_request_context().push()
    
    db.init_app(app)
    
    return app

app = create_app()

#***************************************
#HOW TO START USING MONGOSH IN TERMINAL (step one: type mongosh?)
#***************************************
#to start db type in conscole: brew services start mongodb-community@7.0
#to stop: brew services stop mongodb-community@7.0
#to run manually: mongod --config /opt/homebrew/etc/mongod.conf --fork
#mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.0.2
#db = mongodb_client.db

#insert data example:
#mdb.poop.insert_one({
#    "name": "poop"
#})


#print(mongo_client.db.myDatabase.user.find_one({}))
#print(mongo_client) #proves i have a connection

#Example data
post = {
  "name": "Super Widget",
  "description": "This is the most useful item in your toolbox.",
  "price": { "value": "119.99", "currency": "USD" },
  "reviews": [
    {
      "review_id": 786,
      "review_author": "Kristina",
      "review_text": "This is indeed an amazing widget.",
      "published_date": "2019-02-18"
    },
    {
      "review_id": 777,
      "review_author": "Pablo",
      "review_text": "Amazing!",
      "published_date": "2019-02-16"
    }
  ]
}


#***************************************
#TO START/GET INTO MOGNO:
#***************************************

#brew services list - to see if its up an running
#brew mongo " " " " to turn it on/off
#mongosh to sh into the db

#userdb = mongo_client.db["user"]
#print(userdb.insert_one(post).inserted_id)
#print(userdb.insert_one(post))


#userdb = mongo_client.myDatabase["user"]
#print(userdb.insert_one(post).inserted_id)
#print(userdb.insert_one(post))

#Different Ways To Declare Database:
# mongo_client. #Databse name . #Collection Name
#userdb = mongo_client.test_database["user"]
#userdb=mongo_client["test_database"].user
#userdb=mongo_client["test_database"]["user"]
#userdb= mongo_client.test_database.user

userdb= mongo_client.test_database.user #main way



#***************************************
#INSERTING DATA
#***************************************


#***************************************
#Insert a new document: #setting 
#***************************************

#insert one document
#print(userdb.insert_one(post)) #return: InsertOneResult(ObjectId('654b39d731b120078a9798dc'), acknowledged=True)
#print(userdb.insert_one(post).inserted_id) #this returns the id we sent or that was generated so we can keep track of successs

#Insert many documents, separated by commas in a python list. I could also put list objects in here
#print(userdb.insert_many( [
#      { "_id": 10, "item": "large box", "qty": 20 },
#      { "_id": 11, "item": "small box", "qty": 55 },
#      { "_id": 12, "item": "medium box", "qty": 30 }
#   ] ))

#Insert into an existing document
#print(userdb.update({ '_id': 12 }, 
#    { '$push': { 
#        'item': "small box"
#    }}
#))
#print(userdb.update({ '_id': 12 }, 
#    { '$push': { 
#        'emp_address': {
#            street: "125 Fake2 Street2",
#            city: "Faketon2",
#            state: "SA"
#        }
#    }}
#))

#***************************************
#update data in a document:
#***************************************

#update a specific document, adding to arrays
#print(userdb.update_one(
#   { '_id': 6 }, #specify the document
#   { '$addToSet': { 'reviews': "accessories2" } } # must be array. addtoset only adds if it doesnt already exist in array! useful for playlist@
#))

#i can also replace $addtoSet with '$push' if i want to allow duplication
#print(userdb.update_one(
#   { '_id': 6 }, #specify the document
#   { '$push': { 'reviews': "accessories2" } } # must be array. addtoset only adds if it doesnt already exist in array! useful for playlist@
#))

#change value in document. if value doesn't exist, it will simply add one
#result=userdb.update_one({ "_id": 6 },  #specify document
#                        {'$set' : { "item": "venti box" }} #set, field, value
#                        )
#it will return 'updatedExisting: true if it is successful
#print(result)

#***************************************
#update many documents(
#***************************************

#query = {"qty": { "$gt": 25 } } #i can search above a certain value, or string name (Can hash if trouble with strings vars) #i can search id's or an id range #regrex searchesf or the filed that match the value. ^S means it starts with the letter s
#new_values = { "$set": { "name": "above 25 POOP" } }
##
#result = userdb.update_many(query, new_values) #For places where the field is a certain value, set whatever value i want to it. or add it
#print(result)

#how to copy/dupe a collection
#below allows you to add fields to a dcocument, similar to set, but adds the field even if it already exists
#result=userdb.aggregate(
#[
#        { "$addFields": {  #functiom
#            "name": { "$concat": [ "$firstName", " ", "$lastName" ] } 
#        }},
#        { "$out": '<output collection name>' } #this creates a new collection based off the change i want to make, saving the original db!!!
#    ]
#)



#update all documents
#result=userdb.update_many( 
#        {}, 
#        {"$set": 
#            { 
#                "name": "POOOOP"
#            } 
#        }, 
#    
#   # don't insert if no document found 
#   upsert=False, 
#   array_filters=None
#   ) 
#print(result)

#other operations (see references mongodb in bookmarks)
#i can alszo $setOnInsert: Update value only if a new document insertion.
#$unset: Remove the field and its value.
#$rename: Renames a field




#***************************************
#RETREIEVEING & DELETING DATA
#***************************************



#how to delete data/collections. i can use update_many with delete_many and change the query. in this case i would query playlist info
#myQuery ={'qty': 30}
#result=userdb.delete_one(myQuery)
#print(result)

#Delete documents:
#result= my_collection.delete_many({}) #deletes all documents
# result = my_collection.delete_many({"name": "Mr.Geek"}) #deletes certain documents
#or  result = my_collection.remove() # to delete all documents (better method though is below if im going to do this)

#delete specific data or instance in document: (similar to update section)
#result = userdb.update_one({"_id": 6}, { '$unset': {"name": "POOOOP"} } ) #i can also leave name field blank, and it i will just remove the field
#if i leave id field blank, it will remove all instances of the unset category throughout documents, useful if the data i want to delete is immutable and specific, meaning it wont be deleted fo rothers (some playlists may br saved by others,so this may be dangerosu for that purpose)
#print(result)
#i can do the same thing with update many if i want, leaving id field blank

#delete an element out of an array 
#result = userdb.update_one({"_id": 6}, { '$pull': {"reviews": "accessories"} } ) #it will delete accessories from the array 
#if i leave id field blank with 'id', it will not remove all instances of the unset category throughout documents, useful if the data i want to delete is immutable and specific, meaning it wont be deleted fo rothers (some playlists may br saved by others,so this may be dangerosu for that purpose)
#i may have to replace it with a $ operator to find
#print(result)
#it will find the id where the context is the case
#e.g. it will deelte ['playlist']['2'], the entire id 2 entry #maybe i can set playlsit id to id

#delete or update and item in the array that matches the given sub-sequent layered information
#result = userdb.update_one({"_id": 6}, { '$pull': {"reviews": { "review_author" : "Pablo"}} } ) #deletes the entire entry from array where author is pablo,
#print(result)
#you can delete by array index
#db.lists.update({}, {$unset : {"interests.3" : 1 }}) 
#db.lists.update({}, {$pull : {"interests" : null}})

#how to access an embeded document, a subsequent elemtn in an array of element
#delete or update an item within the element of the array (e.g. ['playlists']['1232387']['owner'])

#if unknwon index number in array, it will find it in the first instance it exits within the documents
#query= { "reviews": { '$elemMatch': {"review_author":"Kristina"} } }
#item = { '$set': {'reviews.$.published_date':"POOOP"} } #
#result=userdb.update_one(query, item)
#print(result)

#query with specificed document number
#query= {"_id": 1, "reviews": { '$elemMatch': {"review_author":"Kristina"} } }
#item = { '$set': {'reviews.$.published_date':"POOO432542P"} } #
#result=userdb.update_one(query, item)
#print(result)

#if known index number in array
#result=userdb.update_one(
#    {'_id' : 1},
#    {'$set' : {"reviews.0.published_date" : "New content B"}}
#)
#print(result)


#print(userdb.update_one(
#   { '_id': 6 }, #specify the document
#   { '$addToSet': { 'reviews': "accessories2" } } # must be array. addtoset only adds if it doesnt already exist in array! useful for playlist@
#))

#Delete collection:
#db.my_collection.drop() #removes collection
#print(mongo_client["test_database"]["<output collection name>"].drop())

#i can sort, find and upate, and just find



#***************************************
#FIND/RETRIEVE data
#***************************************



#print all instances/documents in a collection individually
#for x in userdb.find():
#  print(x)
#  #print(x["_id"])#i can also parse this data
  
#find a specific data / RETRIEVE SPECIFIC DATA
#result = userdb.find_one({'author': 'Mike'}) #(returns first instance) if there's many
#print(result)

#i can also specy multiple datafields:
#result = mycollection.find_one({'Branch': 'CSE'},
#                               {'_id': 0, 'name': 1, 'Roll No': 1})
#print(result)

#or find many specific data
#result = userdb.find({'author':"Mike"}) #or playlist id or name ( i can make my own search function)
#for x in result:
#    print(x)

#print(result) #if i just print a single instance, it will return an object type, not everything to me at once. so i have to filer/query/search through each instance/document using a for lloop

#i can print all data
#print(userdb.find()) #or use for loop for it 

#how to sort all playlists in a certain order
#alphabetical, ascending (a-z):
#result = userdb.find().sort("name")

#for x in result:
#    print(x)

#for descending, you would append '.sort("name",-1)'

#find specific and update data specific data:
#query = {"qty": 25 } #data i want to find
#new_values = { "$set": { "name": "above 25 POOP" } }
#result = userdb.update_many(query, new_values) #For places where the field is a certain value, set whatever value i want to it. or add it
#print(result)
#i can also userdb.find_one_and_update(filter, update, options)  where filter is query and update is dew value



#***************************************
#ARRAY STUFFF:
#***************************************



#delete an element out of an array 
#result = userdb.update_one({"_id": 6}, { '$pull': {"reviews": "accessories"} } ) #it will delete accessories from the array 
#if i leave id field blank with 'id', it will not remove all instances of the unset category throughout documents, useful if the data i want to delete is immutable and specific, meaning it wont be deleted fo rothers (some playlists may br saved by others,so this may be dangerosu for that purpose)
#i may have to replace it with a $ operator to find
#print(result)
#it will find the id where the context is the case
#e.g. it will deelte ['playlist']['2'], the entire id 2 entry #maybe i can set playlsit id to id

#delete or update and item in the array that matches the given sub-sequent layered information
#result = userdb.update_one({"_id": 6}, { '$pull': {"reviews": { "review_author" : "Pablo"}} } ) #deletes the entire entry from array where author is pablo,
#print(result)
#you can delete by array index
#db.lists.update({}, {$unset : {"interests.3" : 1 }}) 
#db.lists.update({}, {$pull : {"interests" : null}})

#how to access an embeded document, a subsequent elemtn in an array of element
#delete or update an item within the element of the array (e.g. ['playlists']['1232387']['owner'])

#if unknwon index number in array, it will find it in the first instance it exits within the documents
#query= { "reviews": { '$elemMatch': {"review_author":"Kristina"} } }
#item = { '$set': {'reviews.$.published_date':"POOOP"} } #
#result=userdb.update_one(query, item)
#print(result)

#query with specificed document number
#query= {"_id": 1, "reviews": { '$elemMatch': {"review_author":"Kristina"} } }
#item = { '$set': {'reviews.$.published_date':"POOO432542P"} } #
#result=userdb.update_one(query, item)
#print(result)

#if known index number in array
#result=userdb.update_one(
#    {'_id' : 1},
#    {'$set' : {"reviews.0.published_date" : "New content B"}}
#)
#print(result)


#print(userdb.update_one(
#   { '_id': 6 }, #specify the document
#   { '$addToSet': { 'reviews': "accessories2" } } # must be array. addtoset only adds if it doesnt already exist in array! useful for playlist@
#))

#delete something out of an array 
#result = userdb.update_one({"_id": 6}, { '$unset': {"reviews": "POOOOP"} } ) #i can also leave name field blank, and it i will just remove the field
#if i leave id field blank, it will remove all instances of the unset category throughout documents, useful if the data i want to delete is immutable and specific, meaning it wont be deleted fo rothers (some playlists may br saved by others,so this may be dangerosu for that purpose)
#print(result)

#print(userdb.update_one(
#   { '_id': 6 }, #specify the document
#   { '$addToSet': { 'reviews': "accessories2" } } # must be array. addtoset only adds if it doesnt already exist in array! useful for playlist@
#))
#db.list_collection_names()
#print(mongo.db)





#***************************************#***************************************#***************************************

from models import User
db.create_all()




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