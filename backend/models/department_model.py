from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from .user_model import PyObjectId
from bson import ObjectId

class Department(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    name: str

class DepartmentInDB(Department):
    pass
