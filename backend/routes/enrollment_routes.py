from fastapi import APIRouter, Body, HTTPException, status, Depends
from backend.models.enrollment_model import Enrollment
from backend.utils.jwt_handler import decodeJWT
from backend.database.connection import enrollment_collection, department_collection, user_collection
from datetime import datetime
from bson import ObjectId

router = APIRouter(
    prefix="/enrollments",
    tags=["Enrollments"],
)

@router.get("/societies", response_description="Get all available societies/departments")
async def get_societies(token: dict = Depends(decodeJWT)):
    """Get all departments that students can enroll in (only those with approved teachers)"""
    try:
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )
        
        user_role = token.get("role")
        
        # Get departments based on role
        if user_role == "student":
            # Students only see departments with approved teachers
            approved_teacher_enrollments = await enrollment_collection.find({
                "status": "approved"
            }).to_list(1000)
            
            # Get department IDs with approved teachers
            dept_ids_with_teachers = set()
            for enrollment in approved_teacher_enrollments:
                user = await user_collection.find_one({"_id": ObjectId(enrollment["user_id"])})
                if user and user.get("role") == "teacher":
                    dept_ids_with_teachers.add(enrollment["department_id"])
            
            # Get departments that have approved teachers
            departments = []
            for dept_id_str in dept_ids_with_teachers:
                dept = await department_collection.find_one({"_id": ObjectId(dept_id_str)})
                if dept:
                    dept["_id"] = str(dept["_id"])
                    departments.append(dept)
            
            # Get student's enrollment status for each department
            user_id = token.get("user_id")
            enrollments = await enrollment_collection.find({"user_id": user_id}).to_list(1000)
            enrollment_map = {e["department_id"]: {"status": e["status"], "id": str(e["_id"])} for e in enrollments}
            
            for dept in departments:
                enrollment_info = enrollment_map.get(dept["_id"], {"status": "not_enrolled", "id": None})
                dept["enrollment_status"] = enrollment_info["status"]
                if enrollment_info["id"]:
                    dept["enrollment_id"] = enrollment_info["id"]
        
        elif user_role == "teacher":
            # Teachers see all departments to request enrollment
            departments = await department_collection.find().to_list(1000)
            for dept in departments:
                dept["_id"] = str(dept["_id"])
            
            # Get teacher's enrollment status
            user_id = token.get("user_id")
            enrollment = await enrollment_collection.find_one({"user_id": user_id})
            
            for dept in departments:
                if enrollment and enrollment["department_id"] == dept["_id"]:
                    dept["enrollment_status"] = enrollment["status"]
                    dept["enrollment_id"] = str(enrollment["_id"])
                else:
                    dept["enrollment_status"] = "not_enrolled"
        
        else:
            # Admins see all departments
            departments = await department_collection.find().to_list(1000)
            for dept in departments:
                dept["_id"] = str(dept["_id"])
        
        return departments
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch societies: {str(e)}",
        )

@router.post("/request", response_description="Request enrollment to a society")
async def request_enrollment(department_id: str = Body(..., embed=True), token: dict = Depends(decodeJWT)):
    """Student or Teacher requests to enroll in a society/department"""
    try:
        if not token or token.get("role") not in ["student", "teacher"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only students and teachers can request enrollment",
            )
        
        user_id = token.get("user_id")
        user_role = token.get("role")
        
        # Teachers can only enroll in ONE department
        if user_role == "teacher":
            existing_enrollment = await enrollment_collection.find_one({"user_id": user_id})
            if existing_enrollment:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Teachers can only be enrolled in one department",
                )
        
        # Check if already enrolled or pending
        existing = await enrollment_collection.find_one({
            "user_id": user_id,
            "department_id": department_id
        })
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"You already have a {existing['status']} enrollment request",
            )
        
        # Create enrollment request
        enrollment_data = {
            "user_id": user_id,
            "department_id": department_id,
            "status": "pending",
            "requested_at": datetime.now().isoformat(),
            "reviewed_at": None,
            "reviewed_by": None
        }
        
        result = await enrollment_collection.insert_one(enrollment_data)
        created = await enrollment_collection.find_one({"_id": result.inserted_id})
        
        # Convert ObjectId to string
        created["_id"] = str(created["_id"])
        
        return {
            "message": "Enrollment request submitted successfully",
            "enrollment": created
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to request enrollment: {str(e)}",
        )

@router.get("/my-enrollments", response_description="Get student's enrollments")
async def get_my_enrollments(token: dict = Depends(decodeJWT)):
    """Get current user's enrollment requests"""
    try:
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )
        
        user_id = token.get("user_id")
        enrollments = await enrollment_collection.find({"user_id": user_id}).to_list(1000)
        
        # Populate department info and convert ObjectId to string
        for enrollment in enrollments:
            enrollment["_id"] = str(enrollment["_id"])
            dept = await department_collection.find_one({"_id": ObjectId(enrollment["department_id"])})
            enrollment["department_name"] = dept.get("name", "Unknown") if dept else "Unknown"
        
        return enrollments
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch enrollments: {str(e)}",
        )

@router.get("/pending", response_description="Get pending enrollment requests")
async def get_pending_enrollments(token: dict = Depends(decodeJWT)):
    """Get pending enrollments based on role:
    - Admins see teacher enrollment requests
    - Teachers see student enrollment requests for their department"""
    try:
        if not token or token.get("role") not in ["teacher", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only teachers and admins can view enrollment requests",
            )
        
        user_role = token.get("role")
        user_id = token.get("user_id")
        
        enrollments = []
        
        if user_role == "admin":
            # Admin sees teacher enrollment requests
            all_pending = await enrollment_collection.find({"status": "pending"}).to_list(1000)
            for enrollment in all_pending:
                user = await user_collection.find_one({"_id": ObjectId(enrollment["user_id"])})
                if user and user.get("role") == "teacher":
                    enrollment["_id"] = str(enrollment["_id"])
                    dept = await department_collection.find_one({"_id": ObjectId(enrollment["department_id"])})
                    enrollment["user_name"] = user.get("name", "Unknown")
                    enrollment["user_email"] = user.get("email", "Unknown")
                    enrollment["user_role"] = user.get("role", "Unknown")
                    enrollment["department_name"] = dept.get("name", "Unknown") if dept else "Unknown"
                    enrollments.append(enrollment)
        else:
            # Teachers see student enrollment requests for their department
            # First get teacher's approved department
            teacher_enrollment = await enrollment_collection.find_one({
                "user_id": user_id,
                "status": "approved"
            })
            
            if teacher_enrollment:
                teacher_dept_id = teacher_enrollment["department_id"]
                
                # Get pending student enrollments for this department
                all_pending = await enrollment_collection.find({
                    "status": "pending",
                    "department_id": teacher_dept_id
                }).to_list(1000)
                
                for enrollment in all_pending:
                    user = await user_collection.find_one({"_id": ObjectId(enrollment["user_id"])})
                    if user and user.get("role") == "student":
                        enrollment["_id"] = str(enrollment["_id"])
                        dept = await department_collection.find_one({"_id": ObjectId(enrollment["department_id"])})
                        enrollment["user_id"] = str(user["_id"])
                        enrollment["user_name"] = user.get("name", "Unknown")
                        enrollment["user_email"] = user.get("email", "Unknown")
                        enrollment["user_role"] = user.get("role", "Unknown")
                        enrollment["department_name"] = dept.get("name", "Unknown") if dept else "Unknown"
                        enrollments.append(enrollment)
        
        return enrollments
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch pending enrollments: {str(e)}",
        )

@router.get("/approved", response_description="Get approved students")
async def get_approved_enrollments(token: dict = Depends(decodeJWT)):
    """Teachers can view all approved students in their department"""
    try:
        if not token or token.get("role") != "teacher":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only teachers can view approved enrollments",
            )
        
        user_id = token.get("user_id")
        
        # Get teacher's approved department
        teacher_enrollment = await enrollment_collection.find_one({
            "user_id": user_id,
            "status": "approved"
        })
        
        if not teacher_enrollment:
            return []
        
        teacher_dept_id = teacher_enrollment["department_id"]
        
        # Get approved student enrollments for this department
        approved_enrollments = await enrollment_collection.find({
            "status": "approved",
            "department_id": teacher_dept_id
        }).to_list(1000)
        
        result = []
        for enrollment in approved_enrollments:
            user = await user_collection.find_one({"_id": ObjectId(enrollment["user_id"])})
            if user and user.get("role") == "student":
                enrollment["_id"] = str(enrollment["_id"])
                dept = await department_collection.find_one({"_id": ObjectId(enrollment["department_id"])})
                result.append({
                    "enrollment_id": str(enrollment["_id"]),
                    "user_id": str(user["_id"]),
                    "user_name": user.get("name", "Unknown"),
                    "user_email": user.get("email", "Unknown"),
                    "user_role": user.get("role", "Unknown"),
                    "department_name": dept.get("name", "Unknown") if dept else "Unknown",
                    "approved_at": enrollment.get("reviewed_at", enrollment.get("requested_at"))
                })
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch approved enrollments: {str(e)}",
        )

@router.post("/review/{enrollment_id}", response_description="Approve or decline enrollment")
async def review_enrollment(
    enrollment_id: str, 
    action: str = Body(..., embed=True),
    token: dict = Depends(decodeJWT)
):
    """Teacher approves or declines an enrollment request"""
    try:
        if not token or token.get("role") not in ["teacher", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only teachers and admins can review enrollments",
            )
        
        if action not in ["approved", "declined"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Action must be 'approved' or 'declined'",
            )
        
        # Update enrollment
        result = await enrollment_collection.update_one(
            {"_id": ObjectId(enrollment_id)},
            {
                "$set": {
                    "status": action,
                    "reviewed_at": datetime.now().isoformat(),
                    "reviewed_by": token.get("user_id")
                }
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enrollment not found",
            )
        
        return {
            "message": f"Enrollment {action} successfully",
            "status": action
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to review enrollment: {str(e)}",
        )

@router.delete("/{enrollment_id}", response_description="Cancel/Leave enrollment")
async def cancel_enrollment(enrollment_id: str, token: dict = Depends(decodeJWT)):
    """Allow teachers to cancel their enrollment in a society"""
    try:
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )
        
        user_id = token.get("user_id")
        user_role = token.get("role")
        
        # Get the enrollment
        enrollment = await enrollment_collection.find_one({"_id": ObjectId(enrollment_id)})
        
        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enrollment not found",
            )
        
        # Check if the user owns this enrollment
        if enrollment["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only cancel your own enrollments",
            )
        
        # Teachers can cancel their approved enrollments
        if user_role == "teacher" and enrollment["status"] == "approved":
            # Delete the enrollment
            result = await enrollment_collection.delete_one({"_id": ObjectId(enrollment_id)})
            
            if result.deleted_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to cancel enrollment",
                )
            
            return {
                "message": "Successfully left the society",
                "enrollment_id": enrollment_id
            }
        elif enrollment["status"] == "pending":
            # Anyone can cancel pending enrollments
            result = await enrollment_collection.delete_one({"_id": ObjectId(enrollment_id)})
            
            if result.deleted_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to cancel enrollment",
                )
            
            return {
                "message": "Enrollment request cancelled",
                "enrollment_id": enrollment_id
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot cancel this enrollment",
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel enrollment: {str(e)}",
        )
