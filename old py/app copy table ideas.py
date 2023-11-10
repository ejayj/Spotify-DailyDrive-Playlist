import os
from os import path
from urllib import response
import main, authcode
from flask import Flask, redirect, render_template, request, jsonify, json, session, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__) 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
app.app_context().push()

def create_app():
    app = Flask(__name__) 
    
    with app.app_context():
        db.create_all()
        #init_db()
    
    return app


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(20), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    
    def __repr__(self):
        return f'User("{self.username}", "{self.email}", "{self.image_file}")'

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))

playlist = ""

@app.route("/", methods=["POST", "GET"])
def index():
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "static", "playlistsSave.json")
    data = json.load(open(json_url))
    return render_template('index.html', data=data)

@app.route("/authorize", methods=["GET"]) 
def authorize(): 
    token = request.args.get('code')
    if token == None:
        return redirect(authcode.runauth())
    else:
        #save token in database.
        # 
        # it will be retrieved by authcod.py. This authorization page will only be accessed when we reach an auth eprror/first login time/if you get signed out [maybe they can login with spotify]? or sign up with their own username and password and itll be stored in database
        return render_template('index.html')

@app.route("/createplaylist", methods=["POST", "GET"])
def createplaylist():
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "static", "playlistsSave.json")
    data = json.load(open(json_url))
    
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
    url=main.run_playlist_script(playlist["id"])
    return redirect(url) #or url_for(url) ?

@app.route("/404") #figure out how to pass error message! request.args? sessions?
def error():
    return render_template('404.html') 


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=80)


#username = User(username="james", email="james@james.com", password="password")
#db.session.add(username)
#db.session.commit()

#next, how to query/print a list?; then sync database with the fetch/playlist function (should update/run every startup or login)
#i need to make a function: OnStartUp() or maybe OnLogin() that runs - fetch playlist (or on sync with spotify)
#i also need to write  afunction that saves the authcode to a db and plugs it in where needed
#and also saves the token, and refresh token to db
#needs to save uid too
#token, refresh token

#need to make a link to another user table?
#below are some table ideas

class User2(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(20), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    uid = db.Column(db.String(20), unique=True, nullable=False, default="NULL")
    token = db.Column(db.String(20), unique=True, nullable=False, default="NULL")
    refreshtoken = db.Column(db.String(20), unique=True, nullable=False, default="NULL")
    playlist_id = db.Column(db.String(20), unique=True, nullable=False, default="NULL")
    
    def __repr__(self):
        return f'User2("{self.username}", "{self.email}", "{self.image_file}")'

class UserSpotifyData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(20), unique=True, nullable=False, default="NULL")
    token = db.Column(db.String(20), unique=True, nullable=False, default="NULL")
    refreshtoken = db.Column(db.String(20), unique=True, nullable=False, default="NULL")
    playlist_id = db.Column(db.String(20), unique=True, nullable=False, default="NULL")
    
    #link this to the User2 Table somehow 
    def __repr__(self):
        return f'UserSpotifyData("{self.id}", "{self.user_id}", "{self.playlist_id}")'
    
class UserSpotifyData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(20), unique=True, nullable=False, default="NULL")
    user_name = db.Column(db.String(20), unique=True, nullable=False, default="NULL") #this is important for finding playlists owned by user. Spotify finds this by name, not UID
    token = db.Column(db.String(20), unique=True, nullable=False, default="NULL")
    refreshtoken = db.Column(db.String(20), unique=True, nullable=False, default="NULL")
    playlist_id = db.Column(db.String(20), unique=True, nullable=False, default="NULL")
    
    #link this to the User2 Table somehow 
    def __repr__(self):
        return f'User("{self.username}", "{self.email}", "{self.image_file}")'

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

user = db.session.execute(db.select(User).filter_by(username="james"))
print(user)

print("i reach here")