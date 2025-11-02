from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from .user_model import PyObjectId
from bson import ObjectId

class Attendance(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    student_id: str
    event_id: str
    timestamp: datetime
    status: str  # Present, Out of Range

class AttendanceInDB(Attendance):
    pass
