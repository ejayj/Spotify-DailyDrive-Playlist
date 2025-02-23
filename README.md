# PythonSpotifyAPI
Creates a custom 'my daily drive' spotify playlist with your choice of music and podcasts
#info
#use source ./venv/bin/activate to activate the venv; source .venv/bin/activate
#can also do flask run app.py
#to run python -m flask run **Main method
#or python3 app.py
#or use $ flask --app hello run --debug


#use deactivate to exit venv
#create venv using vscode command pallet
#see which version using python3 --version
#use pip install requirements to get set up,

#project requires pythong 3.10



TODO: 
try pyton 3.10 as a new method to fix these errors

Also: try to fix the "AttributeError: attribute '__default__' of 'typing.ParamSpec' objects is not writable"
or try going from scratch since there' sso many issues to solve....


i needd .flaskenv to say 
FLASK_APP=__init__.py

dont forget to start mongo db



mongodb:
install homebrew
install mongodb via homebrew
brew services start mongodb-community@8.0 [or stop, can also take out @8.0]


to check if mongodb is working: brew services list

use: mongosh
> to start using mongodb
use mongo compass app for a gui of the data base
or use: brew services stop mongodb-community@8.0

next: 
add the redirect URI to the JavaScript code and make sure it is in line with the allowed redirect UR as on Spotify
change the redirect uri everywhere it shows up: so far: authtoken.py, and script.js


If i want another user to use my app, i have to approve them