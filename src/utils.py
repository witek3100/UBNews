import os
import json
import pymongo

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

config_path = os.path.join(project_root, 'src', 'config.json')
with open(config_path) as config_file:
    config = json.load(config_file)

# MONGO CLIENT
mongo_uri = config["mongo"]["uri"]
mongo_db = config["mongo"]["db"]
mongo_client = pymongo.MongoClient(mongo_uri)[mongo_db]
sources_collection = mongo_client['sources']
