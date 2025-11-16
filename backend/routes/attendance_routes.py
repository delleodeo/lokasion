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

class CheckOutRequest(BaseModel):
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
        if not attendance:
            # Status message contains the error
            if "not yet open" in check_in_status or "has ended" in check_in_status:
                raise HTTPException(status_code=400, detail=check_in_status)
            elif check_in_status == "Event not found":
                raise HTTPException(status_code=404, detail="Event not found")
            elif check_in_status == "Already checked in":
                raise HTTPException(status_code=400, detail="You have already checked in for this event")
            elif check_in_status == "Out of Range":
                raise HTTPException(status_code=400, detail="You are out of range. Please move closer to the event location.")
            else:
                raise HTTPException(status_code=400, detail=check_in_status)
        
        return {
            "status": "Success",
            "message": check_in_status,
            "attendance": attendance
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Check-in error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Check-in failed: {str(e)}",
        )

@router.post("/checkout", response_description="Check out from an event")
async def check_out(request: CheckOutRequest = Body(...), token: dict = Depends(decodeJWT)):
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
        
        attendance, check_out_status = await attendance_controller.check_out(
            student_id=current_user_id,
            event_id=event_id_obj,
            user_lat=request.latitude,
            user_lon=request.longitude
        )
        
        # Handle different check-out statuses
        if not attendance:
            # Status message contains the error
            if "not yet open" in check_out_status or "has ended" in check_out_status:
                raise HTTPException(status_code=400, detail=check_out_status)
            elif check_out_status == "Event not found":
                raise HTTPException(status_code=404, detail="Event not found")
            elif check_out_status == "Already checked out":
                raise HTTPException(status_code=400, detail="You have already checked out from this event")
            elif check_out_status == "You must check in first before checking out":
                raise HTTPException(status_code=400, detail="You must check in first before checking out")
            elif check_out_status == "Out of Range":
                raise HTTPException(status_code=400, detail="You are out of range. Please move closer to the event location.")
            else:
                raise HTTPException(status_code=400, detail=check_out_status)
        
        return {
            "status": "Success",
            "message": check_out_status,
            "attendance": attendance
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Check-out error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Check-out failed: {str(e)}",
        )

@router.get("/history/{student_id}", response_description="Get attendance history for a student")
async def get_history(student_id: str):
    try:
        history = await attendance_controller.get_attendance_history(student_id)
        return history
    except Exception as e:
        print(f"[ERROR] History fetch error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch history: {str(e)}",
        )

@router.get("/status/{event_id}", response_description="Check attendance status for current user")
async def get_attendance_status(event_id: str, token: dict = Depends(decodeJWT)):
    try:
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )
        
        try:
            event_id_obj = ObjectId(event_id)
        except InvalidId:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid event ID format",
            )
        
        current_user_id = token.get("user_id")
        status_info = await attendance_controller.get_attendance_status(current_user_id, event_id_obj)
        
        return status_info
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Status check error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check status: {str(e)}",
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
        print(f"[ERROR] Event attendance fetch error: {str(e)}")
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
        print(f"[ERROR] Finalize attendance error: {str(e)}")
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
        print(f"[ERROR] Export error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export attendance: {str(e)}",
        )
