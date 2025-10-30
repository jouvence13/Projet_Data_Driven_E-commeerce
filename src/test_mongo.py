from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))

try:
    client.admin.command('ping')
    print("Connexion à MongoDB réussie")
except Exception as e:
    print("Erreur de connexion à MongoDB: ", e)