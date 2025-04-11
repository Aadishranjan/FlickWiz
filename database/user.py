from datetime import datetime, timedelta
from pymongo import MongoClient
from os import getenv
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(getenv("MONGO_URI"))
db = client["flickwiz_db"]
users_col = db["users"]

def add_user(user_id, username):
    """Add a new user to the database."""
    if not users_col.find_one({"user_id": user_id}):
        users_col.insert_one({
            "user_id": user_id,
            "username": username,
            "membership": "normal",
            "last_verified": None
        })

def get_user(user_id):
    """Fetch user data."""
    return users_col.find_one({"user_id": user_id})

def update_membership(user_id, membership_type):
    """Update the membership type of a user."""
    users_col.update_one({"user_id": user_id}, {"$set": {"membership": membership_type}})

def update_verification(user_id):
    """Update the user's verification timestamp."""
    users_col.update_one({"user_id": user_id}, {"$set": {"last_verified": datetime.utcnow()}})

def is_verified(user_id):
    """Check if the user has verified within the last 24 hours."""
    user = users_col.find_one({"user_id": user_id}, {"last_verified": 1})
    if user and user.get("last_verified"):
        return datetime.utcnow() - user["last_verified"] < timedelta(hours=24)
    return False

def set_verification_token(user_id, token):
    """Store verification token and timestamp."""
    users_col.update_one({"user_id": user_id}, {"$set": {"verification_token": token, "token_timestamp": datetime.utcnow()}})

def get_verification_token(user_id):
    """Retrieve the user's stored verification token."""
    user = users_col.find_one({"user_id": user_id}, {"verification_token": 1, "token_timestamp": 1})
    return user if user else None

def remove_verification_token(user_id):
    """Remove the stored verification token after successful verification."""
    users_col.update_one({"user_id": user_id}, {"$unset": {"verification_token": "", "token_timestamp": ""}})