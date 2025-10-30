import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv
import os
load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("MONGO_DBNAME")]      
collection = db["categorie"]          
csv_path = r"..\data\category_tree.csv"
df = pd.read_csv(csv_path)
documents = df.to_dict(orient="records")
result = collection.insert_many(documents)
print(f" {len(result.inserted_ids)} documents insérés dans MongoDB.")
 