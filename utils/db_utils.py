from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Read MongoDB URI from environment variable, fallback to local MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "auto_secure"

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

def get_residents_collection():
    return db["residents"]

def get_logs_collection():
    return db["logs"]
