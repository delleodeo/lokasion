from motor.motor_asyncio import AsyncIOMotorClient
import os

# Try to load from environment variable, fallback to localhost
MONGO_DETAILS = os.getenv("MONGO_DETAILS", "mongodb://localhost:27017")

print(f"🔗 Attempting to connect to MongoDB: {MONGO_DETAILS[:50]}...")

client = AsyncIOMotorClient(MONGO_DETAILS, serverSelectionTimeoutMS=5000)

database = client.attendance_system

user_collection = database.get_collection("users")
event_collection = database.get_collection("events")
attendance_collection = database.get_collection("attendance")
department_collection = database.get_collection("departments")
enrollment_collection = database.get_collection("enrollments")

