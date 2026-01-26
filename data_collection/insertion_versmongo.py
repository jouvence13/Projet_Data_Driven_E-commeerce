import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Charger les variables d'environnement
load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("MONGO_DB_NAME")]

# Liste de fichiers CSV à insérer
csv_files = [
    r"..\Data\row\item_properties_part1.csv",
]

# Insérer chaque CSV dans la collection
for csv_path in csv_files:
    print(f"Insertion du fichier : {csv_path}")
    df = pd.read_csv(csv_path)
    documents = df.to_dict(orient="records")
    result = db["db_driven"].insert_many(documents)
    print(f"{len(result.inserted_ids)} documents insérés depuis {csv_path}")
        

print("Tous les fichiers CSV ont été insérés dans MongoDB.")