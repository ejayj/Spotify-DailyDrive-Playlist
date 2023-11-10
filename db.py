from flask_sqlalchemy import SQLAlchemy
from pymongo import MongoClient

db = SQLAlchemy()
mongo = MongoClient("mongodb://localhost:27017/")
#app.app_context().push()
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite3.db'