from pymongo import MongoClient
from pymongo.errors import OperationFailure

client = MongoClient("mongodb://localhost:27017/")
db = client["notes_db"]
users_collection = db["users"]
notes_collection = db["notes"]

try:
    notes_collection.create_index([("content", "text")])
except OperationFailure as e:
    print(f"Error creating text index: {e}")