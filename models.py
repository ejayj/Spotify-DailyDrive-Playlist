#from . import db
#from .db import db
from db import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    uid = db.Column(db.String(30), unique=True, nullable=False)
    image_file = db.Column(db.String(60), nullable=False, default='default.jpg')
    authcode = db.Column(db.String(320), nullable=False, default='CODE')
    refreshtoken = db.Column(db.String(320), nullable=False, default='REFRESH_TOKEN')
    accesstoken = db.Column(db.String(320), nullable=False, default='ACCESS_TOKEN') #this value always changes, so it makes no sense to store it. we just need refresh token
    ddplaylistid = db.Column(db.String(30), nullable=False, default='playlist') 
    #cookie = db.Column(db.String(60), nullable=False, default='COOKIE'); flask session handles cookies
    
    def __repr__(self):
        return f'User("{self.id}", "{self.username}", "{self.uid}", "{self.image_file}", "{self.authcode}", "{self.refreshtoken}", "{self.accesstoken}", "{self.ddplaylistid}")' #make into a list?

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    

