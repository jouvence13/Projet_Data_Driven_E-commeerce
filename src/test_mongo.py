from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

client = MongoClient(os.getenv("MONGO_URL"))

try:
    client.admin.command('ping')
    print("Connexion à MongoDB réussie")
except Exception as e:
    print(f"Erreur de connexion à MongoDB: ", e)