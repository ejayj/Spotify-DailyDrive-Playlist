from flask_sqlalchemy import SQLAlchemy
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
MongoClient_url=os.getenv("MongoClient_url")

db = SQLAlchemy()
mongo = MongoClient(f"{MongoClient_url}")
#app.app_context().push()
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite3.db'