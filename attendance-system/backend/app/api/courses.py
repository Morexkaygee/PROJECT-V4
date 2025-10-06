from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.course import Course, CourseStudent
from app.models.user import Student, Lecturer
from app.models.attendance import AttendanceSession

router = APIRouter(prefix="/courses", tags=["courses"])

class CreateCourseRequest(BaseModel):
    name: str
    code: str
    description: str = ""

@router.get("/")
def get_all_courses(db: Session = Depends(get_db)):
    """Get all available courses."""
    courses = db.query(Course).all()
    result = []
    
    for course in courses:
        lecturer = db.query(Lecturer).filter(Lecturer.id == course.lecturer_id).first()
        lecturer_user = db.query(User).filter(User.id == lecturer.id).first() if lecturer else None
        
        student_count = db.query(CourseStudent).filter(CourseStudent.course_id == course.id).count()
        
        result.append({
            "id": course.id,
            "name": course.name,
            "code": course.code,
            "description": getattr(course, 'description', ''),
            "lecturer_name": lecturer_user.name if lecturer_user else "Unknown",
            "student_count": student_count,
            "created_at": course.created_at if hasattr(course, 'created_at') else None
        })
    
    return result

@router.post("/")
def create_course(
    request: CreateCourseRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new course (lecturer only)."""
    if current_user.role != "lecturer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only lecturers can create courses"
        )
    
    # Check if course code already exists
    existing_course = db.query(Course).filter(Course.code == request.code).first()
    if existing_course:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course code already exists"
        )
    
    course = Course(
        name=request.name,
        code=request.code,
        lecturer_id=current_user.id
    )
    
    db.add(course)
    db.commit()
    db.refresh(course)
    
    return {"message": "Course created successfully", "course_id": course.id}

@router.get("/student")
def get_student_courses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get courses enrolled by current student."""
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access this endpoint"
        )
    
    enrollments = db.query(CourseStudent).filter(CourseStudent.student_id == current_user.id).all()
    result = []
    
    for enrollment in enrollments:
        course = db.query(Course).filter(Course.id == enrollment.course_id).first()
        if course:
            lecturer = db.query(Lecturer).filter(Lecturer.id == course.lecturer_id).first()
            lecturer_user = db.query(User).filter(User.id == lecturer.id).first() if lecturer else None
            
            result.append({
                "id": course.id,
                "name": course.name,
                "code": course.code,
                "lecturer_name": lecturer_user.name if lecturer_user else "Unknown"
            })
    
    return result

@router.get("/lecturer")
def get_lecturer_courses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get courses accessible by current lecturer (owned + permitted)."""
    if current_user.role != "lecturer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only lecturers can access this endpoint"
        )
    
    from app.models.course import CoursePermission
    
    # Get owned courses
    owned_courses = db.query(Course).filter(Course.lecturer_id == current_user.id).all()
    
    # Get courses with permissions
    permissions = db.query(CoursePermission).filter(
        CoursePermission.lecturer_id == current_user.id
    ).all()
    
    permitted_course_ids = [p.course_id for p in permissions]
    permitted_courses = db.query(Course).filter(Course.id.in_(permitted_course_ids)).all() if permitted_course_ids else []
    
    # Combine and deduplicate
    all_courses = list({course.id: course for course in owned_courses + permitted_courses}.values())
    
    result = []
    for course in all_courses:
        student_count = db.query(CourseStudent).filter(CourseStudent.course_id == course.id).count()
        is_owner = course.lecturer_id == current_user.id
        
        result.append({
            "id": course.id,
            "name": course.name,
            "code": course.code,
            "student_count": student_count,
            "is_owner": is_owner,
            "created_at": course.created_at if hasattr(course, 'created_at') else None
        })
    
    return result

@router.post("/{course_id}/enroll")
def enroll_in_course(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enroll current student in course."""
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can enroll in courses"
        )
    
    # Check if course exists
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Check if already enrolled
    existing_enrollment = db.query(CourseStudent).filter(
        CourseStudent.course_id == course_id,
        CourseStudent.student_id == current_user.id
    ).first()
    
    if existing_enrollment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already enrolled in this course"
        )
    
    # Create enrollment
    enrollment = CourseStudent(
        course_id=course_id,
        student_id=current_user.id
    )
    
    db.add(enrollment)
    db.commit()
    
    return {"message": "Successfully enrolled in course"}

def has_course_access(db: Session, course_id: int, lecturer_id: int) -> bool:
    """Check if lecturer has access to course (owns it or has permission)."""
    from app.models.course import CoursePermission
    
    # Check if lecturer owns the course
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.lecturer_id == lecturer_id
    ).first()
    
    if course:
        return True
    
    # Check if lecturer has permission
    permission = db.query(CoursePermission).filter(
        CoursePermission.course_id == course_id,
        CoursePermission.lecturer_id == lecturer_id
    ).first()
    
    return bool(permission)


@router.get("/{course_id}/students")
def get_course_students(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get students enrolled in course (lecturer only)."""
    if current_user.role != "lecturer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only lecturers can view course students"
        )
    
    # Check if lecturer has access to this course
    if not has_course_access(db, course_id, current_user.id):
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
                # Simplified attendance count to avoid join issues
                attendance_count = 0  # TODO: Fix attendance count query
                
                result.append({
                    "id": student.id,
                    "name": user.name,
                    "matric_no": student.matric_no,
                    "has_facial_encoding": bool(student.facial_encoding),
                    "attendance_count": attendance_count
                })
    
    return result


class GrantPermissionRequest(BaseModel):
    lecturer_name: str


@router.post("/{course_id}/permissions")
def grant_course_permission(
    course_id: int,
    request: GrantPermissionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Grant course access to another lecturer (course owner only)."""
    if current_user.role != "lecturer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only lecturers can grant permissions"
        )
    
    # Check if current user owns the course
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.lecturer_id == current_user.id
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found or you don't own this course"
        )
    
    # Find the lecturer to grant permission to
    target_user = db.query(User).filter(
        User.name == request.lecturer_name,
        User.role == "lecturer"
    ).first()
    
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lecturer not found"
        )
    
    # Check if permission already exists
    from app.models.course import CoursePermission
    existing_permission = db.query(CoursePermission).filter(
        CoursePermission.course_id == course_id,
        CoursePermission.lecturer_id == target_user.id
    ).first()
    
    if existing_permission:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Permission already granted"
        )
    
    # Grant permission
    permission = CoursePermission(
        course_id=course_id,
        lecturer_id=target_user.id
    )
    
    db.add(permission)
    db.commit()
    
    return {"message": f"Permission granted to {request.lecturer_name}"}


@router.get("/{course_id}/permissions")
def get_course_permissions(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get lecturers with access to course (course owner only)."""
    if current_user.role != "lecturer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only lecturers can view permissions"
        )
    
    # Check if current user owns the course
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.lecturer_id == current_user.id
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found or you don't own this course"
        )
    
    from app.models.course import CoursePermission
    permissions = db.query(CoursePermission).filter(
        CoursePermission.course_id == course_id
    ).all()
    
    result = []
    for permission in permissions:
        lecturer_user = db.query(User).filter(User.id == permission.lecturer_id).first()
        if lecturer_user:
            result.append({
                "id": permission.id,
                "lecturer_name": lecturer_user.name,
                "granted_at": permission.granted_at
            })
    
    return result