from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from app.core.database import get_db
from app.core.config import settings
from app.api.auth import get_current_user
from app.models.user import User
from app.models.attendance import AttendanceSession, Attendance
from app.services.attendance_service import (
    create_attendance_session,
    mark_attendance_with_verification,
    get_session_attendance
)

router = APIRouter(prefix="/attendance", tags=["attendance"])


class CreateSessionRequest(BaseModel):
    title: str
    course_id: int
    start_time: str  # ISO format datetime string
    end_time: str    # ISO format datetime string
    location_lat: float
    location_lng: float
    location_radius: float = 100.0


class MarkAttendanceRequest(BaseModel):
    session_id: int
    face_image_data: str
    student_lat: float
    student_lng: float


class TestFaceRequest(BaseModel):
    face_image_data: str


@router.post("/sessions")
def create_session(
    request: CreateSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new attendance session (lecturer only)."""
    if current_user.role != "lecturer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only lecturers can create attendance sessions"
        )
    
    from datetime import datetime
    
    try:
        start_time = datetime.fromisoformat(request.start_time.replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(request.end_time.replace('Z', '+00:00'))
        
        if end_time <= start_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End time must be after start time"
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid datetime format"
        )
    
    session = create_attendance_session(
        db=db,
        title=request.title,
        course_id=request.course_id,
        start_time=start_time,
        end_time=end_time,
        location_lat=request.location_lat,
        location_lng=request.location_lng,
        location_radius=request.location_radius
    )
    
    return {
        "message": "Attendance session created successfully",
        "session_id": session.id
    }


@router.post("/mark")
def mark_attendance(
    request: MarkAttendanceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark attendance with face and GPS verification (student only)."""
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can mark attendance"
        )
    
    return mark_attendance_with_verification(
        db=db,
        session_id=request.session_id,
        student_id=current_user.id,
        face_image_data=request.face_image_data,
        student_lat=request.student_lat,
        student_lng=request.student_lng
    )


@router.get("/sessions/active")
def get_active_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get active attendance sessions for students."""
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can view active sessions"
        )
    
    from app.models.course import CourseStudent, Course
    
    # Get courses student is enrolled in
    enrollments = db.query(CourseStudent).filter(CourseStudent.student_id == current_user.id).all()
    course_ids = [e.course_id for e in enrollments]
    
    if not course_ids:
        return []
    
    # Get active sessions for enrolled courses
    sessions = db.query(AttendanceSession).filter(
        AttendanceSession.course_id.in_(course_ids),
        AttendanceSession.is_active == True
    ).all()
    
    result = []
    for session in sessions:
        course = db.query(Course).filter(Course.id == session.course_id).first()
        result.append({
            "id": session.id,
            "title": session.title,
            "course_id": session.course_id,
            "course_name": course.name if course else "Unknown",
            "course_code": course.code if course else "Unknown",
            "created_at": session.created_at,
            "is_active": session.is_active
        })
    
    return result

@router.get("/sessions/lecturer")
def get_lecturer_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get attendance sessions created by current lecturer."""
    if current_user.role != "lecturer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only lecturers can view their sessions"
        )
    
    from app.models.course import Course
    
    # Get lecturer's courses
    courses = db.query(Course).filter(Course.lecturer_id == current_user.id).all()
    course_ids = [c.id for c in courses]
    
    if not course_ids:
        return []
    
    # Get sessions for lecturer's courses
    sessions = db.query(AttendanceSession).filter(
        AttendanceSession.course_id.in_(course_ids)
    ).order_by(AttendanceSession.created_at.desc()).all()
    
    result = []
    for session in sessions:
        course = db.query(Course).filter(Course.id == session.course_id).first()
        attendance_count = db.query(Attendance).filter(Attendance.session_id == session.id).count()
        
        result.append({
            "id": session.id,
            "title": session.title,
            "course_id": session.course_id,
            "course_name": course.name if course else "Unknown",
            "course_code": course.code if course else "Unknown",
            "created_at": session.created_at,
            "is_active": session.is_active,
            "attendance_count": attendance_count
        })
    
    return result

@router.get("/sessions/{session_id}/attendance")
def get_attendance_records(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get attendance records for a session (lecturer only)."""
    if current_user.role != "lecturer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only lecturers can view attendance records"
        )
    
    return get_session_attendance(db, session_id)

@router.get("/student/history")
def get_student_attendance_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get attendance history for current student."""
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can view their attendance history"
        )
    
    from app.models.course import Course
    
    # Get student's attendance records
    records = db.query(Attendance).filter(Attendance.student_id == current_user.id).order_by(Attendance.marked_at.desc()).all()
    
    result = []
    for record in records:
        session = db.query(AttendanceSession).filter(AttendanceSession.id == record.session_id).first()
        if session:
            course = db.query(Course).filter(Course.id == session.course_id).first()
            result.append({
                "id": record.id,
                "session_title": session.title,
                "course_name": course.name if course else "Unknown",
                "course_code": course.code if course else "Unknown",
                "marked_at": record.marked_at,
                "status": "present"
            })
    
    return result


@router.post("/test-face")
def test_face_recognition(
    request: MarkAttendanceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Test face recognition without marking attendance."""
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can test face recognition"
        )
    
    from app.models.user import Student
    from app.utils.face_recognition import encode_face_from_base64, verify_face, verify_face_advanced
    
    student = db.query(Student).filter(Student.id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )
    
    # Test face encoding
    new_encoding = encode_face_from_base64(request.face_image_data)
    if not new_encoding:
        return {
            "face_detected": False,
            "message": "No face detected in image",
            "has_registered_face": bool(student.facial_encoding or student.advanced_facial_encoding),
            "registration_method": student.face_registration_method or "none"
        }
    
    # Test face verification based on registration method
    face_match = False
    verification_details = {}
    
    if student.advanced_facial_encoding and student.face_registration_method == "advanced":
        try:
            # Test advanced verification
            verification_result = verify_face_advanced(
                student.advanced_facial_encoding,
                request.face_image_data,
                settings.face_recognition_tolerance
            )
            face_match = verification_result.get('match', False)
            verification_details = {
                'method': 'advanced',
                'confidence': verification_result.get('confidence', 0.0),
                'models_used': list(verification_result.get('model_results', {}).keys()),
                'quality_score': verification_result.get('quality_score', 0.0)
            }
        except Exception as e:
            # Fallback to basic if advanced fails
            if student.facial_encoding:
                face_match = verify_face(
                    student.facial_encoding,
                    request.face_image_data,
                    settings.face_recognition_tolerance
                )
                verification_details = {'method': 'basic_fallback', 'error': str(e)}
    elif student.facial_encoding:
        # Test basic verification
        face_match = verify_face(
            student.facial_encoding,
            request.face_image_data,
            settings.face_recognition_tolerance
        )
        verification_details = {'method': 'basic'}
    
    return {
        "face_detected": True,
        "has_registered_face": bool(student.facial_encoding or student.advanced_facial_encoding),
        "registration_method": student.face_registration_method or "basic",
        "face_match": face_match,
        "verification_details": verification_details,
        "message": "Face recognition test completed",
        "tolerance": settings.face_recognition_tolerance,
        "can_upgrade": student.face_registered and student.face_registration_method == "basic"
    }