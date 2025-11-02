from fastapi import APIRouter, Body, Depends, HTTPException, status
from backend.controllers import attendance_controller
from backend.utils.jwt_handler import decodeJWT
from pydantic import BaseModel
from bson import ObjectId
from bson.errors import InvalidId

class CheckInRequest(BaseModel):
    event_id: str
    latitude: float
    longitude: float

router = APIRouter(
    prefix="/attendance",
    tags=["Attendance"],
)

@router.post("/checkin", response_description="Check in for an event")
async def check_in(request: CheckInRequest = Body(...), token: dict = Depends(decodeJWT)):
    try:
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token or expired token",
            )
        
        try:
            event_id_obj = ObjectId(request.event_id)
        except InvalidId:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid event ID format",
            )
        
        current_user_id = token.get("user_id")
        
        attendance, check_in_status = await attendance_controller.check_in(
            student_id=current_user_id,
            event_id=event_id_obj,
            user_lat=request.latitude,
            user_lon=request.longitude
        )
        
        # Handle different check-in statuses
        if check_in_status == "Event not found":
            raise HTTPException(status_code=404, detail="Event not found")
        elif check_in_status == "Already checked in":
            raise HTTPException(status_code=400, detail="You have already checked in for this event")
        elif check_in_status == "Out of Range":
            raise HTTPException(status_code=400, detail="You are out of range. Please move closer to the event location.")
        elif check_in_status == "Present":
            return {
                "status": "Present",
                "message": "Successfully checked in!",
                "attendance": attendance
            }
        else:
            raise HTTPException(status_code=500, detail="Unexpected check-in status")
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Check-in error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Check-in failed: {str(e)}",
        )

@router.get("/history/{student_id}", response_description="Get attendance history for a student")
async def get_history(student_id: str):
    try:
        history = await attendance_controller.get_attendance_history(student_id)
        return history
    except Exception as e:
        print(f"❌ History fetch error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch history: {str(e)}",
        )

@router.get("/event/{event_id}", response_description="Get attendance for a specific event")
async def get_event_attendance(event_id: str, token: dict = Depends(decodeJWT)):
    try:
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )
        
        # Verify the user is a teacher
        if token.get("role") != "teacher":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only teachers can view event attendance",
            )
        
        try:
            event_id_obj = ObjectId(event_id)
        except InvalidId:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid event ID format",
            )
        
        # Get attendance records for this event
        attendance_records = await attendance_controller.get_event_attendance(event_id_obj)
        
        return {
            "event_id": event_id,
            "total_checkins": len(attendance_records),
            "attendance": attendance_records
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Event attendance fetch error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch event attendance: {str(e)}",
        )

@router.post("/event/{event_id}/finalize", response_description="Finalize attendance - mark absent students")
async def finalize_attendance(event_id: str, token: dict = Depends(decodeJWT)):
    try:
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )
        
        # Verify the user is a teacher
        if token.get("role") != "teacher":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only teachers can finalize attendance",
            )
        
        try:
            event_id_obj = ObjectId(event_id)
        except InvalidId:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid event ID format",
            )
        
        # Finalize attendance
        result = await attendance_controller.finalize_event_attendance(event_id_obj)
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Finalize attendance error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to finalize attendance: {str(e)}",
        )

@router.get("/event/{event_id}/export", response_description="Export event attendance to Excel")
async def export_event_attendance(event_id: str, token: dict = Depends(decodeJWT)):
    try:
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )
        
        # Verify the user is a teacher
        if token.get("role") != "teacher":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only teachers can export event attendance",
            )
        
        try:
            event_id_obj = ObjectId(event_id)
        except InvalidId:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid event ID format",
            )
        
        # Export to Excel
        from fastapi.responses import StreamingResponse
        import io
        
        excel_file = await attendance_controller.export_event_attendance_to_excel(event_id_obj)
        
        return StreamingResponse(
            io.BytesIO(excel_file),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename=event_{event_id}_attendance.xlsx"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Export error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export attendance: {str(e)}",
        )
