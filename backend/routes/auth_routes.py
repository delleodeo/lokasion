from fastapi import APIRouter, Body, HTTPException, status, UploadFile, File, Depends
from backend.controllers import auth_controller
from backend.models.user_model import User
from backend.utils.jwt_handler import decodeJWT
from pydantic import BaseModel, EmailStr
from typing import Optional
from bson import ObjectId

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

class RegisterRequest(BaseModel):
    """Request model for user registration."""
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    id_number: str
    name: str
    email: EmailStr
    password: str
    role: str
    department_id: Optional[str] = None
    admin_secret_code: Optional[str] = None

class LoginRequest(BaseModel):
    """Request model for user login."""
    email: EmailStr
    password: str

@router.post("/register", response_description="Register a new user")
async def register(reg_data: RegisterRequest = Body(...)):
    try:
        # Validate admin secret code if role is admin
        ADMIN_SECRET_CODE = "MinSUAttendanceSystem"
        if reg_data.role == "admin":
            if not reg_data.admin_secret_code or reg_data.admin_secret_code != ADMIN_SECRET_CODE:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid admin secret code",
                )
        
        # Convert to dictionary for processing
        user_data = {
            "first_name": reg_data.first_name,
            "middle_name": reg_data.middle_name,
            "last_name": reg_data.last_name,
            "id_number": reg_data.id_number,
            "name": reg_data.name,
            "email": reg_data.email,
            "password": reg_data.password,
            "role": reg_data.role,
            "department_id": reg_data.department_id
        }
        
        existing_user = await auth_controller.user_collection.find_one({"email": user_data["email"]})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )
        new_user = await auth_controller.register_user(user_data)
        return {
            "message": "User created successfully",
            "user_id": str(new_user["_id"]),
            "email": new_user["email"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}",
        )

@router.post("/login", response_description="Login a user")
async def login(login_data: LoginRequest = Body(...)):
    try:
        token = await auth_controller.login_user(login_data.email, login_data.password)
        if token:
            return token
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}",
        )

@router.post("/register-face", response_description="Register user face")
async def register_face(file: UploadFile = File(...), token: dict = Depends(decodeJWT)):
    user_id = token.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
        
    success, message = await auth_controller.register_face(user_id, file)
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
        
    return {"message": message}

@router.get("/me", response_description="Get current user")
async def get_me(token: dict = Depends(decodeJWT)):
    user_id = token.get("user_id")
    user = await auth_controller.user_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        return {
            "id": str(user["_id"]),
            "first_name": user.get("first_name", ""),
            "middle_name": user.get("middle_name", ""),
            "last_name": user.get("last_name", ""),
            "name": user.get("name", ""),
            "id_number": user.get("id_number", ""),
            "email": user["email"],
            "role": user["role"],
            "department_id": user.get("department_id"),
            "has_face_registered": bool(user.get("face_encoding"))
        }
    raise HTTPException(status_code=404, detail="User not found")

@router.put("/profile", response_description="Update own profile")
async def update_profile(update_data: dict = Body(...), token: dict = Depends(decodeJWT)):
    try:
        user_id = token.get("user_id")
        
        # Import admin_controller for update_user function
        from backend.controllers import admin_controller
        
        # Users can only update their own profile (not role)
        updated_user = await admin_controller.update_user(user_id, update_data, is_admin=False)
        
        return {
            "message": "Profile updated successfully",
            "user": updated_user
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}",
        )
