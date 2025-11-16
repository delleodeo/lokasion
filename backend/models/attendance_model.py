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
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    check_in_status: Optional[str] = None  # "Present", "Absent", "Late"
    check_out_status: Optional[str] = None # "Present", "Absent", "Early"
    timestamp: datetime
    status: str  # Present, Absent

class AttendanceInDB(Attendance):
    pass
