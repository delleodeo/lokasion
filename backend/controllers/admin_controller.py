from backend.database.connection import user_collection, department_collection
from backend.models.user_model import User
from backend.models.department_model import Department

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
