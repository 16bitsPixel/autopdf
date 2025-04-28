import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the MongoDB URI from the .env file
MONGODB_URI = os.getenv("MONGODB_URI")

# Check if the MONGODB_URI is set
if not MONGODB_URI:
    raise ValueError("MONGODB_URI is not set in the .env file")

# Connect to MongoDB
client = MongoClient(MONGODB_URI)
db = client["pdf_mining"]
collection = db["documents"]
