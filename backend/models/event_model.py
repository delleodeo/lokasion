from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from .user_model import PyObjectId
from bson import ObjectId

class Event(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    name: str
    teacher_id: str
    department_id: Optional[str] = None
    latitude: float
    longitude: float
    radius: float
    start_time: datetime
    end_time: datetime

class EventInDB(Event):
    pass
