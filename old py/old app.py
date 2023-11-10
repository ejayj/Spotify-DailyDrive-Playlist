import os
from urllib import response
import hellohello
from flask import Flask, redirect, render_template, request, jsonify, json, url_for

app = Flask(__name__) #creating an instance of the flask object

@app.route("/", methods=["POST", "GET"])
def index():
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "static", "playlistsSave.json")
    data = json.load(open(json_url)) #get_json()
    #return render_template('index.html', data=data["playlists"][0]["name"]) #prints out a single data. i can loop this in a list with { % for loop % } changing the 0 value with x in a list
  
    if request.method == "POST":
        index = request.form["playlist"]
        #playlist = json.loads(playlist)
        index = int(index)-1
        gotocreateplaylist(index, data)
    else:
        return render_template('index.html', data=data)
    
    return render_template('index.html', data=data)

@app.route("/createplaylist", methods=["POST", "GET"])
def createplaylist():
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "static", "playlistsSave.json")
    data = json.load(open(json_url)) #get_json()
    
    index = request.form["playlist"]
    #playlist = json.loads(playlist)
    index = int(index)-1
    playlist = data["playlists"][int(index)]
    playlistid=data["playlists"][int(index)]["id"]
        
    if request.method == "POST":
        index = request.form["playlist"]
        #playlist = json.loads(playlist)
        index = int(index)-1
        gotocreateplaylist(index, data)
    else:
        return render_template('createplaylist.html', data=data)
    
    return render_template('createplaylist.html', index=index, id=playlistid, playlist=playlist) #should redirect to some spotify page

def gotocreateplaylist(index,data):
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__)) #instead of reloading the whole file, i want to just pass the one elemnt in the json and be able to load it as json in createplaylist.html using data["playlist"][1]["name"] and etc.
    json_url = os.path.join(SITE_ROOT, "static", "playlistsSave.json")
    data = json.load(open(json_url))
    playlist = data["playlists"][int(index)]
    playlistid=data["playlists"][int(index)]["id"]
    
    if request.method == "POST":
        return render_template('createplaylist.html', index=index, id=playlistid, playlist=playlist)
    else:
        return render_template('createplaylist.html', data=data)
    
    return render_template('createplaylist.html', index=index, id=playlistid, playlist=playlist)
    

@app.route("/playlist") #maybe /playlist<status?> for loading bar?
def pp():
    return render_template('finished.html') #should redirect to some spotify page

@app.route("/test")
def test():
    return hellohello.hello() #this about how to 

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=80) #port=80
    
    
    
#info
#use source ./venv/bin/activate to activate the venv
#can also do flask run app.py
#to run python -m flask run 
#or python3 app.py
#or use $ flask --app hello run --debug