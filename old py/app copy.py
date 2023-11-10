import os
from urllib import response
import main
from flask import Flask, redirect, render_template, request, jsonify, json, session, url_for

app = Flask(__name__) 
playlist = ""

@app.route("/", methods=["POST", "GET"])
def index():
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "static", "playlistsSave.json")
    data = json.load(open(json_url))
    return render_template('index.html', data=data)

@app.route("/authorize", methods=["GET"]) #if there is nothing in code, then go to authorize page. This code uses the authorize copy 3 .html which is a javascript focused way to get the auth code. 
def authorize(): #currently, it goes to test.html and pastes the token there. i need to send the token to the database and save it in authcode.py
    token = request.args.get('code') 
    if token == None: #if requests.get isnt successful, load regular page
        return render_template('authorize.html')
    else:
        return render_template('test.html', token=token) #if it is, move on with code. this prevents us from repeating the same page over and over again

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
    
    
#it works!!!
#Up next:
#1. - get the auth code/token variables to change for when someone else loggs in
#1a. - find a way to where i can copy url from authtoken spotify page [do this in separate instance to test and not break website!]
#1b. - store this in a database
#2. upon login, app should gather all of the user's playlist
#3. clean some files, and make app more secure (ada and gdpr complian )
#3a. make website secure

#minor stuff:
#ui/ux styling

#last:
#continue learning flask so i can publicize the website:
# II. i'll need to create a database to store all the json and txt files that i have
