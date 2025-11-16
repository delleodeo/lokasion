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
        
        # Get teacher's approved department enrollment(s)
        from backend.database.connection import enrollment_collection, department_collection, user_collection
        from bson import ObjectId
        
        teacher_enrollments = await enrollment_collection.find({
            "user_id": user_id,
            "status": "approved"
        }).to_list(1000)
        
        if not teacher_enrollments:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You must be enrolled and approved in a department before creating events",
            )
        
        # Check if department_id is provided and valid
        event_dict = event.dict(exclude_unset=True)
        # Remove _id if it's None
        if "_id" in event_dict and event_dict["_id"] is None:
            del event_dict["_id"]
        if "id" in event_dict and event_dict["id"] is None:
            del event_dict["id"]
        
        # Verify teacher has access to the specified department
        if "department_id" not in event_dict or not event_dict["department_id"]:
            # If no department specified, use the first approved one
            event_dict["department_id"] = teacher_enrollments[0]["department_id"]
        else:
            # Verify teacher is approved in this department
            teacher_dept_ids = [e["department_id"] for e in teacher_enrollments]
            if event_dict["department_id"] not in teacher_dept_ids:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not approved in this department",
                )
        
        # Create event with department_id
        new_event = await event_controller.create_event(Event(**event_dict))
        return {
            "message": "Event created successfully",
            "event_id": str(new_event["_id"]),
            "event": new_event,
            "department_id": event_dict["department_id"]
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
        
        if user_role == "student":
            # Students can only see events from societies they're enrolled in and approved
            # AND only active events (not ended)
            from backend.database.connection import enrollment_collection
            from bson import ObjectId
            from datetime import datetime
            
            # Get approved enrollments for this user
            enrollments = await enrollment_collection.find({
                "user_id": user_id,
                "status": "approved"
            }).to_list(1000)
            
            # Convert ObjectIds to strings for comparison
            approved_dept_ids = [str(e["department_id"]) for e in enrollments]
            
            print(f"[DEBUG] Event filtering for student (user_id: {user_id}):")
            print(f"   Total events: {len(events)}")
            print(f"   Approved enrollments: {len(enrollments)}")
            print(f"   Approved department IDs: {approved_dept_ids}")
            
            # Filter events by department_id and end time
            # Use local time - no UTC conversion
            now = datetime.now()
            filtered_events = []
            print(f"\n[TIME] Current local time: {now}\n")
            
            for event in events:
                event_dept_id = event.get("department_id")
                event_end_time = event.get("end_time")
                check_out_end = event.get("check_out_end")
                is_active = event.get("is_active", True)
                
                # Determine if event is still available
                # Priority: check_out_end > end_time
                event_is_available = False
                end_deadline = None
                
                if check_out_end:
                    event_is_available = now <= check_out_end
                    end_deadline = check_out_end
                elif event_end_time:
                    event_is_available = now <= event_end_time
                    end_deadline = event_end_time
                
                # Only show events that:
                # 1. Belong to student's enrolled department
                # 2. Have not ended yet
                # 3. Are marked as active
                is_enrolled = event_dept_id in approved_dept_ids
                
                if is_enrolled and event_is_available and is_active:
                    filtered_events.append(event)
                    print(f"   [OK] Event '{event.get('name')}' - Available (ends: {end_deadline})")
                else:
                    if not is_enrolled:
                        reason = "not enrolled"
                    elif not is_active:
                        reason = "inactive"
                    elif not event_is_available:
                        reason = f"ended (deadline was: {end_deadline})"
                    else:
                        reason = "unknown"
                    print(f"   [HIDDEN] Event '{event.get('name')}' - Hidden ({reason})")
            
            print(f"\n   Total events: {len(events)}, Filtered events: {len(filtered_events)}\n")
            return filtered_events
        
        elif user_role == "teacher":
            # Teachers can only see events from societies they're enrolled in and approved
            from backend.database.connection import enrollment_collection
            from bson import ObjectId
            
            # Get approved enrollments for this user
            enrollments = await enrollment_collection.find({
                "user_id": user_id,
                "status": "approved"
            }).to_list(1000)
            
            # Convert ObjectIds to strings for comparison
            approved_dept_ids = [str(e["department_id"]) for e in enrollments]
            
            print(f"[DEBUG] Event filtering for teacher (user_id: {user_id}):")
            print(f"   Total events: {len(events)}")
            print(f"   Approved enrollments: {len(enrollments)}")
            print(f"   Approved department IDs: {approved_dept_ids}")
            
            # Filter events by department_id
            filtered_events = []
            for event in events:
                event_dept_id = event.get("department_id")
                if event_dept_id in approved_dept_ids:
                    filtered_events.append(event)
            
            print(f"   Filtered events: {len(filtered_events)}")
            return filtered_events
        
        # Admins see all events
        print(f"[DEBUG] Event filtering for admin - returning all {len(events)} events")
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
        print(f"[ERROR] Delete event error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete event: {str(e)}",
        )
