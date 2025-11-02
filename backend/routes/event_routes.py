from fastapi import APIRouter, Body, HTTPException, status, Depends
from backend.controllers import event_controller
from backend.models.event_model import Event
from backend.utils.jwt_handler import decodeJWT

router = APIRouter(
    prefix="/events",
    tags=["Events"],
)

@router.post("/", response_description="Add new event")
async def create_event(event: Event = Body(...), token: dict = Depends(decodeJWT)):
    try:
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )
        
        # Only teachers can create events
        if token.get("role") != "teacher":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only teachers can create events",
            )
        
        user_id = token.get("user_id")
        
        # Get teacher's approved department enrollment
        from backend.database.connection import enrollment_collection, department_collection, user_collection
        from bson import ObjectId
        
        teacher_enrollment = await enrollment_collection.find_one({
            "user_id": user_id,
            "status": "approved"
        })
        
        if not teacher_enrollment:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You must be enrolled and approved in a department before creating events",
            )
        
        # Auto-assign the teacher's department to the event
        event_dict = event.dict(exclude_unset=True)
        # Remove _id if it's None
        if "_id" in event_dict and event_dict["_id"] is None:
            del event_dict["_id"]
        if "id" in event_dict and event_dict["id"] is None:
            del event_dict["id"]
        
        event_dict["department_id"] = teacher_enrollment["department_id"]
        
        # Update teacher's department_id in user collection (for backward compatibility)
        await user_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"department_id": teacher_enrollment["department_id"]}}
        )
        
        # Create event with department_id
        new_event = await event_controller.create_event(Event(**event_dict))
        return {
            "message": "Event created successfully",
            "event_id": str(new_event["_id"]),
            "event": new_event,
            "department_id": teacher_enrollment["department_id"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create event: {str(e)}",
        )

@router.get("/", response_description="Get all events")
async def get_events(token: dict = Depends(decodeJWT)):
    try:
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )
        
        # Get all events
        events = await event_controller.get_events()
        
        # Filter events based on user role and enrollment
        user_role = token.get("role")
        user_id = token.get("user_id")
        
        if user_role == "student" or user_role == "teacher":
            # Students and teachers can only see events from societies they're enrolled in and approved
            from backend.database.connection import enrollment_collection
            from bson import ObjectId
            
            # Get approved enrollments for this user
            enrollments = await enrollment_collection.find({
                "user_id": user_id,
                "status": "approved"
            }).to_list(1000)
            
            # Convert ObjectIds to strings for comparison
            approved_dept_ids = [str(e["department_id"]) for e in enrollments]
            
            print(f"🔍 Event filtering for {user_role} (user_id: {user_id}):")
            print(f"   Total events: {len(events)}")
            print(f"   Approved enrollments: {len(enrollments)}")
            print(f"   Approved department IDs: {approved_dept_ids}")
            
            # Filter events by department_id
            filtered_events = []
            for event in events:
                event_dept_id = event.get("department_id")
                print(f"   Event '{event.get('name')}' - dept_id: {event_dept_id} - Match: {event_dept_id in approved_dept_ids}")
                if event_dept_id in approved_dept_ids:
                    filtered_events.append(event)
            
            print(f"   Filtered events: {len(filtered_events)}")
            return filtered_events
        
        # Admins see all events
        print(f"🔍 Event filtering for admin - returning all {len(events)} events")
        return events
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch events: {str(e)}",
        )

@router.delete("/{event_id}", response_description="Delete an event")
async def delete_event(event_id: str, token: dict = Depends(decodeJWT)):
    try:
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )
        
        # Only teachers can delete events
        if token.get("role") != "teacher":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only teachers can delete events",
            )
        
        from bson import ObjectId
        from bson.errors import InvalidId
        
        try:
            event_id_obj = ObjectId(event_id)
        except InvalidId:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid event ID format",
            )
        
        # Delete the event
        from backend.database.connection import event_collection, attendance_collection
        
        result = await event_collection.delete_one({"_id": event_id_obj})
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found",
            )
        
        # Also delete all attendance records for this event
        await attendance_collection.delete_many({"event_id": event_id_obj})
        
        return {
            "message": "Event and associated attendance records deleted successfully",
            "event_id": event_id
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Delete event error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete event: {str(e)}",
        )
