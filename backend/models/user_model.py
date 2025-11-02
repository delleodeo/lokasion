from pydantic import BaseModel, EmailStr, Field, ConfigDict
from pydantic_core import core_schema
from typing import Optional
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.str_schema(),
        )
    
    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

class User(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    first_name: str
    last_name: str
    id_number: str
    name: Optional[str] = None  # Keep for backward compatibility
    email: EmailStr
    password: str
    role: str  # admin, teacher, student
    department_id: Optional[str] = None
class UserInDB(User):
    hashed_password: str
