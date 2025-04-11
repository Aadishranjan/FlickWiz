from difflib import get_close_matches
from pymongo import MongoClient
from config import MONGO_URI
from bson import ObjectId  # Import ObjectId to fetch movie by _id

client = MongoClient(MONGO_URI)
db = client["flickwiz_db"]
filters_collection = db["filters"]

print("✅ Connected to MongoDB")

# ✅ Function to Get Movie by Name (With Pagination)


def normalize(text):
    return ''.join(e.lower() for e in text if e.isalnum())

def get_filter(movie_name, page_number=0, page_size=8):
    """Fetch movies with pagination and suggest close matches."""
    movie_name = normalize(movie_name)
    skip_count = page_number * page_size

    all_movies = list(filters_collection.find({}, {"movie_name": 1, "file_id": 1}))
    
    # Normalize all names for matching
    matched = [
        movie for movie in all_movies 
        if movie.get("movie_name") and movie_name in normalize(movie["movie_name"])
    ]

    if matched:
        return matched[skip_count: skip_count + page_size]
    
    # If no match, suggest closest titles
    all_names = [movie["movie_name"] for movie in all_movies if "movie_name" in movie]
    close_matches = get_close_matches(movie_name, [normalize(name) for name in all_names], n=5, cutoff=0.6)

    suggestions = [
        movie for movie in all_movies 
        if normalize(movie["movie_name"]) in close_matches
    ]

    return suggestions[:page_size]


# ✅ Function to Get Movie by ID
def get_movie_by_id(movie_id):
    """Fetches a movie from MongoDB using its `_id`"""
    movie = filters_collection.find_one({"_id": ObjectId(movie_id)}, {"movie_name": 1, "file_id": 1})
    return movie if movie else None
    
    