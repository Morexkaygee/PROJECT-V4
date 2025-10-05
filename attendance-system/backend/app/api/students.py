from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from pydantic import BaseModel
from typing import List, Optional
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User, Student
from app.models.course import Course, CourseStudent
from app.models.attendance import Attendance

router = APIRouter(prefix="/students", tags=["students"])


@router.get("/")
def get_all_students(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Search by name, email, or matric number"),
    department: Optional[str] = Query(None, description="Filter by department"),
    level: Optional[str] = Query(None, description="Filter by level")
):
    """Get all students with filtering and search (lecturer only)."""
    if current_user.role != "lecturer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only lecturers can view all students"
        )
    
    query = db.query(Student).join(User)
    
    # Apply search filter
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                User.name.ilike(search_term),
                Student.matric_no.ilike(search_term)
            )
        )
    
    # Apply department filter
    if department:
        query = query.filter(Student.department.ilike(f"%{department}%"))
    
    # Apply level filter
    if level:
        query = query.filter(Student.level == level)
    
    students = query.all()
    result = []
    
    for student in students:
        user = db.query(User).filter(User.id == student.id).first()
        if user:
            course_count = db.query(CourseStudent).filter(CourseStudent.student_id == student.id).count()
            attendance_count = db.query(Attendance).filter(Attendance.student_id == student.id).count()
            
            result.append({
                "id": student.id,
                "name": user.name,
                "matric_no": student.matric_no,
                "department": student.department,
                "level": student.level,
                "has_facial_encoding": bool(student.facial_encoding),
                "face_registered": student.face_registered,
                "course_count": course_count,
                "attendance_count": attendance_count,
                "created_at": user.created_at,
                "is_active": user.is_active
            })
    
    return result


@router.get("/profile")
def get_student_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current student's profile."""
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access this endpoint"
        )
    
    student = db.query(Student).filter(Student.id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )
    
    course_count = db.query(CourseStudent).filter(CourseStudent.student_id == student.id).count()
    attendance_count = db.query(Attendance).filter(Attendance.student_id == student.id).count()
    
    return {
        "id": student.id,
        "name": current_user.name,
        "matric_no": student.matric_no,
        "department": student.department,
        "level": student.level,
        "has_facial_encoding": bool(student.facial_encoding),
        "face_registered": student.face_registered,
        "course_count": course_count,
        "attendance_count": attendance_count
    }


@router.get("/course/{course_id}")
def get_students_by_course(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get students enrolled in a specific course (lecturer only)."""
    if current_user.role != "lecturer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only lecturers can view course students"
        )
    
    # Verify lecturer owns this course
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.lecturer_id == current_user.id
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found or access denied"
        )
    
    enrollments = db.query(CourseStudent).filter(CourseStudent.course_id == course_id).all()
    result = []
    
    for enrollment in enrollments:
        student = db.query(Student).filter(Student.id == enrollment.student_id).first()
        if student:
            user = db.query(User).filter(User.id == student.id).first()
            if user:
                attendance_count = db.query(Attendance).filter(
                    Attendance.student_id == student.id,
                    Attendance.course_id == course_id
                ).count()
                
                result.append({
                    "id": student.id,
                    "name": user.name,
                    "matric_no": student.matric_no,
                    "department": student.department,
                    "level": student.level,
                    "has_facial_encoding": bool(student.facial_encoding),
                    "face_registered": student.face_registered,
                    "attendance_count": attendance_count,
                    "enrolled_at": enrollment.enrolled_at if hasattr(enrollment, 'enrolled_at') else None
                })
    
    return result


@router.get("/{student_id}/details")
def get_student_details(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed student information (lecturer only)."""
    if current_user.role != "lecturer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only lecturers can view student details"
        )
    
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    user = db.query(User).filter(User.id == student.id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get enrolled courses
    enrollments = db.query(CourseStudent).filter(CourseStudent.student_id == student.id).all()
    enrolled_courses = []
    
    for enrollment in enrollments:
        course = db.query(Course).filter(Course.id == enrollment.course_id).first()
        if course:
            attendance_count = db.query(Attendance).filter(
                Attendance.student_id == student.id,
                Attendance.course_id == course.id
            ).count()
            
            enrolled_courses.append({
                "id": course.id,
                "name": course.name,
                "code": course.code,
                "attendance_count": attendance_count
            })
    
    total_attendance = db.query(Attendance).filter(Attendance.student_id == student.id).count()
    
    return {
        "id": student.id,
        "name": user.name,
        "matric_no": student.matric_no,
        "department": student.department,
        "level": student.level,
        "has_facial_encoding": bool(student.facial_encoding),
        "face_registered": student.face_registered,
        "enrolled_courses": enrolled_courses,
        "total_attendance_records": total_attendance,
        "created_at": user.created_at,
        "is_active": user.is_active
    }