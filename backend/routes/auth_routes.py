from fastapi import APIRouter, Body, HTTPException, status
from backend.controllers import auth_controller
from backend.models.user_model import User
from pydantic import BaseModel, EmailStr
from typing import Optional

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

class RegisterRequest(BaseModel):
    """Request model for user registration."""
    first_name: str
    last_name: str
    id_number: str
    name: str
    email: EmailStr
    password: str
    role: str
    department_id: Optional[str] = None

class LoginRequest(BaseModel):
    """Request model for user login."""
    email: EmailStr
    password: str

@router.post("/register", response_description="Register a new user")
async def register(reg_data: RegisterRequest = Body(...)):
    try:
        # Convert to dictionary for processing
        user_data = {
            "first_name": reg_data.first_name,
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
