from pydantic import BaseModel, Field, ConfigDict, field_validator
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
    location_name: Optional[str] = None  # Human-readable location name
    latitude: float
    longitude: float
    radius: float
    start_time: datetime
    end_time: datetime
    check_in_start: Optional[datetime] = None  # When check-in opens
    check_in_end: Optional[datetime] = None    # When check-in closes
    check_out_start: Optional[datetime] = None # When check-out opens
    check_out_end: Optional[datetime] = None   # When check-out closes
    is_active: Optional[bool] = True           # Event visibility status
    
    @field_validator('start_time', 'end_time', 'check_in_start', 'check_in_end', 'check_out_start', 'check_out_end', mode='before')
    @classmethod
    def parse_datetime(cls, v):
        if v is None or isinstance(v, datetime):
            return v
        if isinstance(v, str):
            # Parse ISO string from frontend as local time (no timezone conversion)
            # Frontend sends local time strings in format YYYY-MM-DDTHH:mm:ss
            try:
                # Remove 'Z' suffix if present (but keep the date-time structure)
                dt_str = v.rstrip('Z')
                # Remove timezone offset info if present (e.g., +08:00 or -05:00)
                if '+' in dt_str:
                    dt_str = dt_str.split('+')[0]
                elif dt_str.count('-') > 2:  # More than 2 hyphens means there's a timezone offset
                    # Keep YYYY-MM-DD but remove timezone (e.g., "2025-11-16T18:46:00-05:00" -> "2025-11-16T18:46:00")
                    parts = dt_str.rsplit('-', 1)
                    if ':' in parts[-1]:  # Last part looks like timezone offset
                        dt_str = parts[0]
                # Parse as naive local datetime (no timezone info)
                return datetime.fromisoformat(dt_str)
            except ValueError:
                try:
                    return datetime.fromisoformat(v)
                except ValueError:
                    # If all else fails, return as-is and let pydantic handle the error
                    return v
        return v

class EventInDB(Event):
    pass
