from backend.database.connection import event_collection
from backend.models.event_model import Event
from backend.utils.serializer import serialize_doc, serialize_list
from bson import ObjectId
from fastapi import HTTPException

async def create_event(event: Event):
    event_dict = event.dict(by_alias=True, exclude_unset=True)
    # Remove any _id or id fields to let MongoDB generate them
    event_dict.pop("_id", None)
    event_dict.pop("id", None)
    new_event = await event_collection.insert_one(event_dict)
    created_event = await event_collection.find_one({"_id": new_event.inserted_id})
    return serialize_doc(created_event)

async def get_events():
    events = []
    async for event in event_collection.find():
        events.append(event)
    return serialize_list(events)

async def update_event(event_id: str, event_data: dict, teacher_id: str):
    """Update an event - only the teacher who created it can edit"""
    try:
        # Find the event
        existing_event = await event_collection.find_one({"_id": ObjectId(event_id)})
        
        if not existing_event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        # Check if the teacher is the creator
        if str(existing_event.get("created_by")) != teacher_id:
            raise HTTPException(status_code=403, detail="You can only edit events you created")
        
        # Update the event
        update_data = {k: v for k, v in event_data.items() if v is not None}
        
        if update_data:
            await event_collection.update_one(
                {"_id": ObjectId(event_id)},
                {"$set": update_data}
            )
        
        # Return updated event
        updated_event = await event_collection.find_one({"_id": ObjectId(event_id)})
        return serialize_doc(updated_event)
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail=str(e))
