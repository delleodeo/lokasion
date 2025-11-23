from backend.database.connection import user_collection, department_collection
from backend.models.user_model import User
from backend.models.department_model import Department
from backend.utils.serializer import serialize_doc, serialize_list
from bson import ObjectId
from fastapi import HTTPException
import bcrypt

async def add_user(user: User):
    # Logic to add a user
    pass

async def add_department(department: Department):
    department_dict = department.dict(by_alias=True, exclude_unset=True)
    # Remove _id if it exists and is None
    department_dict.pop("_id", None)
    department_dict.pop("id", None)
    
    new_department = await department_collection.insert_one(department_dict)
    created_department = await department_collection.find_one({"_id": new_department.inserted_id})
    return created_department

async def get_user_profile(user_id: str):
    """Get user profile by user_id"""
    try:
        user = await user_collection.find_one({"_id": ObjectId(user_id)})
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Remove password from response
        user.pop("password", None)
        user.pop("hashed_password", None)
        
        return serialize_doc(user)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail=str(e))

async def get_all_users():
    """Get all users - for admin"""
    try:
        users = []
        async for user in user_collection.find():
            user.pop("password", None)
            user.pop("hashed_password", None)
            users.append(user)
        return serialize_list(users)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

async def update_user(user_id: str, update_data: dict, is_admin: bool = False):
    """Update user details - admin can update anyone, users can update themselves"""
    try:
        existing_user = await user_collection.find_one({"_id": ObjectId(user_id)})
        
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Prepare update data
        update_fields = {}
        
        # Fields that can be updated
        allowed_fields = ["first_name", "middle_name", "last_name", "id_number", "email", "department_id"]
        
        for field in allowed_fields:
            if field in update_data and update_data[field] is not None:
                update_fields[field] = update_data[field]
        
        # Admin can also change role
        if is_admin and "role" in update_data and update_data["role"]:
            update_fields["role"] = update_data["role"]
        
        # Handle password update if provided
        if "password" in update_data and update_data["password"]:
            hashed = bcrypt.hashpw(update_data["password"].encode('utf-8'), bcrypt.gensalt())
            update_fields["password"] = hashed.decode('utf-8')
        
        if update_fields:
            await user_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_fields}
            )
        
        # Return updated user
        updated_user = await user_collection.find_one({"_id": ObjectId(user_id)})
        updated_user.pop("password", None)
        updated_user.pop("hashed_password", None)
        
        return serialize_doc(updated_user)
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail=str(e))
