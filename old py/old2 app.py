import os
from urllib import response
import hellohello
from flask import Flask, redirect, render_template, request, jsonify, json, session, url_for

app = Flask(__name__) #creating an instance of the flask object
playlist = ""

@app.route("/", methods=["POST", "GET"])
def index():
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "static", "playlistsSave.json")
    data = json.load(open(json_url)) #get_json()
    #return render_template('index.html', data=data["playlists"][0]["name"]) #prints out a single data. i can loop this in a list with { % for loop % } changing the 0 value with x in a list
    
    return render_template('index.html', data=data)

@app.route("/createplaylist", methods=["POST", "GET"])
def createplaylist():
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "static", "playlistsSave.json")
    data = json.load(open(json_url)) #get_json()
    
    try: #this basically allows us to submit the form into this method on the first try, and when we submit the second time it will bypass it
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
                return redirect(url_for('playlist')) #should redirect to some spotify page
            elif submission == 'no':
                return redirect(url_for('index', playlist=playlist))
        except:
            redirect(url_for('error')) #if it reaches here, error   
        redirect(url_for('error')) # if it reaches here, error
    else:
        return render_template('index.html', data=data)

    return render_template('index.html', data=data) #if it reaches here, then there was an error. print to console?

@app.route("/playlist") #maybe /playlist<status?> for loading bar?
def playlist():
    #playlist = request.args['playlist']  # counterpart for url_for()
    #playlist = session['playlist']
    #playlist = getplaylist()
    global playlist
    return render_template('finished.html',playlist=playlist) #should redirect to some spotify page

@app.route("/404")
def error():
    return render_template('404.html') #pass error message


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=80)
    
