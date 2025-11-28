from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import os

# Try to load from environment variable, fallback to localhost
MONGO_DETAILS = os.getenv("MONGO_DETAILS", "mongodb+srv://doroshop01_db_user:lokasion@cluster0.ys6oklr.mongodb.net/?appName=Cluster0")

print(f"[CONNECT] Attempting to connect to MongoDB: {MONGO_DETAILS[:50]}...")

# Configure MongoDB to use naive (non-timezone-aware) datetimes
# This ensures datetimes are stored and retrieved exactly as provided
client = AsyncIOMotorClient(
    MONGO_DETAILS, 
    serverSelectionTimeoutMS=5000,
    tz_aware=False  # Disable timezone-aware datetimes
)

database = client.attendance_system

user_collection = database.get_collection("users")
event_collection = database.get_collection("events")
attendance_collection = database.get_collection("attendance")
department_collection = database.get_collection("departments")
enrollment_collection = database.get_collection("enrollments")

