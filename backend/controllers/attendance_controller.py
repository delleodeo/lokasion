from backend.database.connection import attendance_collection, event_collection
from backend.models.attendance_model import Attendance
from backend.utils.location_validator import is_within_radius
from backend.utils.serializer import serialize_doc
from datetime import datetime
from bson import ObjectId

async def check_in(student_id: str, event_id: ObjectId, user_lat: float, user_lon: float):
    from geopy.distance import geodesic
    
    event = await event_collection.find_one({"_id": event_id})
    if not event:
        return None, "Event not found"

    # Check if student already checked in for this event
    existing_attendance = await attendance_collection.find_one({
        "student_id": student_id,
        "event_id": event_id
    })
    
    if existing_attendance:
        print(f"⚠️  Student {student_id} already checked in for event {event.get('name')}")
        return None, "Already checked in"

    # Calculate distance for debugging
    event_location = (event["latitude"], event["longitude"])
    user_location = (user_lat, user_lon)
    distance = geodesic(user_location, event_location).meters
    
    print(f"🔍 Check-in Debug:")
    print(f"   Event: {event.get('name', 'Unknown')}")
    print(f"   Event Location: {event['latitude']}, {event['longitude']}")
    print(f"   User Location: {user_lat}, {user_lon}")
    print(f"   Distance: {distance:.2f} meters")
    print(f"   Allowed Radius: {event['radius']} meters")
    
    # Only record attendance if student is within range (Present)
    if is_within_radius(user_lat, user_lon, event["latitude"], event["longitude"], event["radius"]):
        print(f"   ✅ Status: PRESENT (within range)")
        
        # Create attendance dict directly (bypassing Pydantic validation with ObjectId)
        attendance_dict = {
            "student_id": student_id,
            "event_id": event_id,
            "timestamp": datetime.utcnow(),
            "status": "Present"
        }

        new_attendance = await attendance_collection.insert_one(attendance_dict)
        created_attendance = await attendance_collection.find_one({"_id": new_attendance.inserted_id})
        return serialize_doc(created_attendance), "Present"
    else:
        print(f"   ❌ Status: OUT OF RANGE (distance exceeds radius)")
        return None, "Out of Range"

async def get_attendance_history(student_id: str):
    history = []
    async for record in attendance_collection.find({"student_id": student_id}):
        history.append(serialize_doc(record))
    return history

async def get_event_attendance(event_id: ObjectId):
    """Get all attendance records for a specific event with student details
    Includes all enrolled students (Present or Absent)"""
    from backend.database.connection import user_collection, enrollment_collection
    
    # Get the event
    event = await event_collection.find_one({"_id": event_id})
    if not event:
        return []
    
    department_id = event.get("department_id")
    
    # Get all enrolled students in the department
    enrolled_students = {}
    if department_id:
        async for enrollment in enrollment_collection.find({
            "department_id": department_id,
            "status": "approved"
        }):
            student_id = str(enrollment["user_id"])
            enrolled_students[student_id] = {
                "student_id": student_id,
                "status": "Absent",  # Default to Absent
                "timestamp": None
            }
    
    # Update with actual attendance records
    async for record in attendance_collection.find({"event_id": event_id}):
        student_id = record["student_id"]
        if student_id in enrolled_students or not department_id:
            enrolled_students[student_id] = {
                "student_id": student_id,
                "status": record.get("status", "Absent"),
                "timestamp": record.get("timestamp"),
                "_id": str(record.get("_id", ""))
            }
    
    # Build attendance records with student details
    attendance_records = []
    for student_id, attendance_info in enrolled_students.items():
        # Get student information
        student = await user_collection.find_one({"_id": ObjectId(student_id)})
        
        attendance_data = {
            "_id": attendance_info.get("_id", ""),
            "student_id": student_id,
            "status": attendance_info["status"],
            "timestamp": attendance_info["timestamp"]
        }
        
        if student:
            attendance_data["student_name"] = student.get("name", "Unknown")
            attendance_data["student_email"] = student.get("email", "Unknown")
            attendance_data["student_id_number"] = student.get("id_number", "N/A")
            attendance_data["student_first_name"] = student.get("first_name", "")
            attendance_data["student_last_name"] = student.get("last_name", "")
        else:
            attendance_data["student_name"] = "Unknown"
            attendance_data["student_email"] = "Unknown"
            attendance_data["student_id_number"] = "N/A"
            attendance_data["student_first_name"] = ""
            attendance_data["student_last_name"] = ""
        
        attendance_records.append(attendance_data)
    
    return attendance_records

async def export_event_attendance_to_excel(event_id: ObjectId):
    """Export event attendance to Excel format - only Present students with first/last name"""
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    from backend.database.connection import user_collection
    from io import BytesIO
    
    # Get event details
    event = await event_collection.find_one({"_id": event_id})
    if not event:
        raise ValueError("Event not found")
    
    # Get all attendance records (Present and Absent)
    attendance_records = await get_event_attendance(event_id)
    
    # Create workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Attendance"
    
    # Add header with event info
    ws.merge_cells('A1:E1')
    ws['A1'] = f"Attendance Report - {event.get('name', 'Event')}"
    ws['A1'].font = Font(size=16, bold=True)
    ws['A1'].alignment = Alignment(horizontal='center')
    
    ws.merge_cells('A2:E2')
    ws['A2'] = f"Date: {event.get('start_time', 'N/A')}"
    ws['A2'].alignment = Alignment(horizontal='center')
    
    # Column headers
    headers = ['No.', 'ID Number', 'Last Name', 'First Name', 'Status']
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True)
    
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=4, column=col_num)
        cell.value = header
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center')
    
    # Add data - only Present students
    for idx, record in enumerate(attendance_records, 1):
        # Get first name and last name from database, fallback to splitting full name
        first_name = record.get('student_first_name', '')
        last_name = record.get('student_last_name', '')
        id_number = record.get('student_id_number', 'N/A')
        
        # If first_name or last_name is empty, try splitting the full name
        if not first_name or not last_name:
            full_name = record.get('student_name', 'Unknown')
            name_parts = full_name.strip().split(' ', 1)  # Split on first space
            
            if len(name_parts) == 2:
                first_name = name_parts[0] if not first_name else first_name
                last_name = name_parts[1] if not last_name else last_name
            elif len(name_parts) == 1:
                first_name = name_parts[0] if not first_name else first_name
        
        ws.cell(row=idx+4, column=1, value=idx)
        ws.cell(row=idx+4, column=2, value=id_number)
        ws.cell(row=idx+4, column=3, value=last_name)
        ws.cell(row=idx+4, column=4, value=first_name)
        
        status = record.get('status', 'Absent')
        status_cell = ws.cell(row=idx+4, column=5, value=status)
        
        # Color code: Green for Present, Red for Absent
        if status == 'Present':
            status_cell.fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
        else:
            status_cell.fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
        
        status_cell.alignment = Alignment(horizontal='center')
    
    # Adjust column widths
    ws.column_dimensions['A'].width = 8
    ws.column_dimensions['B'].width = 15
    ws.column_dimensions['C'].width = 20
    ws.column_dimensions['D'].width = 20
    ws.column_dimensions['E'].width = 15
    
    # Save to BytesIO
    excel_buffer = BytesIO()
    wb.save(excel_buffer)
    excel_buffer.seek(0)
    
    return excel_buffer.getvalue()

async def finalize_event_attendance(event_id: ObjectId):
    """Mark all enrolled students who didn't check in as Absent"""
    from backend.database.connection import user_collection, enrollment_collection
    
    # Get the event
    event = await event_collection.find_one({"_id": event_id})
    if not event:
        raise ValueError("Event not found")
    
    # Get all students enrolled in the event's department
    department_id = event.get("department_id")
    if not department_id:
        return {"message": "Event has no department", "absent_count": 0}
    
    # Get all enrolled students in this department
    enrolled_students = []
    async for enrollment in enrollment_collection.find({
        "department_id": department_id,
        "status": "approved"
    }):
        enrolled_students.append(str(enrollment["user_id"]))
    
    # Get students who already checked in (Present)
    present_students = []
    async for record in attendance_collection.find({
        "event_id": event_id,
        "status": "Present"
    }):
        present_students.append(record["student_id"])
    
    # Mark absent students
    absent_count = 0
    for student_id in enrolled_students:
        if student_id not in present_students:
            # Check if already marked as absent
            existing = await attendance_collection.find_one({
                "student_id": student_id,
                "event_id": event_id
            })
            
            if not existing:
                # Create absent attendance record
                attendance_dict = {
                    "student_id": student_id,
                    "event_id": event_id,
                    "timestamp": datetime.utcnow(),
                    "status": "Absent"
                }
                await attendance_collection.insert_one(attendance_dict)
                absent_count += 1
    
    return {
        "message": "Attendance finalized",
        "total_enrolled": len(enrolled_students),
        "present_count": len(present_students),
        "absent_count": absent_count
    }
