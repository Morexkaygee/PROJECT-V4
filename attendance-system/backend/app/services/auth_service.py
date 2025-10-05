from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User, Student, Lecturer
from app.core.security import verify_password, get_password_hash, create_access_token
from typing import Optional, Dict, Any


def authenticate_user(db: Session, identifier: str, password: str) -> Optional[User]:
    """Authenticate user with name/matric_no and password."""
    try:
        # Try matric_no for students first
        student = db.query(Student).filter(Student.matric_no == identifier).first()
        if student:
            user = db.query(User).filter(User.id == student.id).first()
            if user and verify_password(password, user.hashed_password):
                return user
        
        # Try name for lecturers
        user = db.query(User).filter(
            User.name == identifier,
            User.role == "lecturer"
        ).first()
        if user and verify_password(password, user.hashed_password):
            return user
            
        return None
    except Exception:
        return None


def create_user_token(user: User) -> str:
    """Create JWT token for authenticated user."""
    token_data = {
        "user_id": user.id,
        "role": user.role
    }
    return create_access_token(token_data)


def get_user_profile(db: Session, user_id: int) -> Optional[Dict[str, Any]]:
    """Get user profile with role-specific data."""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
            
        profile = {
            "id": user.id,
            "name": user.name,
            "role": user.role
        }
        
        if user.role == "student":
            student = db.query(Student).filter(Student.id == user_id).first()
            if student:
                profile["matric_no"] = student.matric_no
                profile["has_facial_encoding"] = bool(student.facial_encoding)
                profile["face_registered"] = student.face_registered
        elif user.role == "lecturer":
            lecturer = db.query(Lecturer).filter(Lecturer.id == user_id).first()
            if lecturer:
                profile["department"] = lecturer.department
                profile["title"] = lecturer.title
                profile["staff_id"] = lecturer.staff_id
                
        return profile
    except Exception:
        return None


def register_student(db: Session, name: str, password: str, matric_no: str) -> Dict[str, Any]:
    """Register new student."""
    try:
        # Check if matric_no already exists
        if db.query(Student).filter(Student.matric_no == matric_no).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Matriculation number already registered"
            )
        
        # Create user
        user = User(
            name=name,
            hashed_password=get_password_hash(password),
            role="student"
        )
        db.add(user)
        db.flush()
        
        # Create student profile
        student = Student(
            id=user.id,
            matric_no=matric_no
        )
        db.add(student)
        db.commit()
        
        return {"message": "Student registered successfully", "user_id": user.id}
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


def register_lecturer(db: Session, name: str, password: str) -> Dict[str, Any]:
    """Register new lecturer."""
    try:
        # Check if name already exists for lecturers
        if db.query(User).filter(User.name == name, User.role == "lecturer").first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Lecturer name already registered"
            )
        
        # Create user
        user = User(
            name=name,
            hashed_password=get_password_hash(password),
            role="lecturer"
        )
        db.add(user)
        db.flush()
        
        # Create lecturer profile
        lecturer = Lecturer(id=user.id)
        db.add(lecturer)
        db.commit()
        
        return {"message": "Lecturer registered successfully", "user_id": user.id}
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )