import bcrypt
import face_recognition
import numpy as np
from backend.database.connection import user_collection
from backend.models.user_model import User
from backend.utils.jwt_handler import signJWT
from fastapi import UploadFile, HTTPException
from fastapi.concurrency import run_in_threadpool
from bson import ObjectId
import io

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    # Convert password to bytes and hash it
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash.
    
    Supports both bcrypt (new) and argon2 (legacy) hashes.
    New registrations use bcrypt.
    """
    try:
        # Check if it's a bcrypt hash (starts with $2b$ or $2a$ or $2y$)
        if hashed_password.startswith('$2'):
            password_bytes = plain_password.encode('utf-8')
            hashed_bytes = hashed_password.encode('utf-8')
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        
        # Otherwise, try argon2 (for legacy passwords)
        # We'll use passlib only for verification of old passwords
        try:
            from passlib.context import CryptContext
            pwd_context_legacy = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")
            return pwd_context_legacy.verify(plain_password, hashed_password)
        except ImportError:
            print(f"[WARNING] Cannot verify argon2 password (passlib not available)")
            print(f"[WARNING] Please re-register your account or install passlib[argon2]")
            return False
        except Exception as argon2_error:
            print(f"[WARNING] Legacy password verification failed: {str(argon2_error)}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Password verification error: {str(e)}")
        return False

async def register_user(user_data: dict):
    """Register a new user.
    
    Args:
        user_data: Dictionary containing user registration data
    """
    try:
        print(f"[REGISTER] Registering user: {user_data.get('email')}")
        print(f"[REGISTER] User data received:")
        print(f"   First Name: {user_data.get('first_name')}")
        print(f"   Middle Name: {user_data.get('middle_name')}")
        print(f"   Last Name: {user_data.get('last_name')}")
        print(f"   ID Number: {user_data.get('id_number')}")
        print(f"   Email: {user_data.get('email')}")
        print(f"   Role: {user_data.get('role')}")
        
        # Check if id_number already exists
        existing_user = await user_collection.find_one({"id_number": user_data.get('id_number')})
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail=f"ID Number {user_data.get('id_number')} is already registered. Please use a different ID number."
            )
        
        # Hash the password using bcrypt
        user_data['password'] = get_password_hash(user_data['password'])
        print(f"[SECURITY] Password hashed successfully")
        
        # Remove _id if present (will be auto-generated)
        user_data.pop("_id", None)
        user_data.pop("id", None)
        
        # Insert into database
        new_user = await user_collection.insert_one(user_data)
        created_user = await user_collection.find_one({"_id": new_user.inserted_id})
        
        print(f"[OK] User registered successfully: {created_user['email']} (role: {created_user['role']})")
        print(f"[OK] Stored ID Number: {created_user.get('id_number', 'NOT STORED')}")
        return created_user
    except Exception as e:
        print(f"[ERROR] Registration error: {str(e)}")
        raise Exception(f"Failed to register user: {str(e)}")

async def login_user(email: str, password: str):
    """Authenticate a user and return a JWT token."""
    try:
        # Find user by email
        user = await user_collection.find_one({"email": email})
        
        if not user:
            print(f"[ERROR] Login failed: User not found for email: {email}")
            return None
        
        # Verify password
        is_valid = verify_password(password, user["password"])
        print(f"[SECURITY] Password verification for {email}: {is_valid}")
        
        if is_valid:
            print(f"[OK] Login successful for {email} (role: {user['role']})")
            return signJWT(str(user["_id"]), user["role"], user["name"])
        
        print(f"[ERROR] Login failed: Invalid password for {email}")
        return None
    except Exception as e:
        print(f"[ERROR] Login exception: {str(e)}")
        raise Exception(f"Login error: {str(e)}")

def _get_face_encodings(image_bytes):
    """Helper to run face recognition in a thread pool"""
    image = face_recognition.load_image_file(io.BytesIO(image_bytes))
    return face_recognition.face_encodings(image)

async def register_face(user_id: str, image_file: UploadFile):
    """Register a face for a user."""
    try:
        contents = await image_file.read()
        
        # Run CPU-intensive face recognition in a separate thread
        face_encodings = await run_in_threadpool(_get_face_encodings, contents)
        
        if not face_encodings:
            return False, "No face found in the image"
            
        if len(face_encodings) > 1:
            return False, "Multiple faces found. Please ensure only your face is visible."
            
        # Get the first face encoding
        face_encoding = face_encodings[0].tolist()
        
        # Update user
        result = await user_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"face_encoding": face_encoding}}
        )
        
        if result.matched_count == 0:
            return False, "User not found"
            
        return True, "Face registered successfully"
    except Exception as e:
        print(f"Face registration error: {e}")
        return False, str(e)
