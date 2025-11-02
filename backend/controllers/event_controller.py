from backend.database.connection import event_collection
from backend.models.event_model import Event
from backend.utils.serializer import serialize_doc, serialize_list

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
