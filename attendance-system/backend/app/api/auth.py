from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.database import get_db
from app.core.security import verify_token, verify_password
from app.services.auth_service import authenticate_user, create_user_token, get_user_profile, register_student, register_lecturer
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Dependency to get current authenticated user."""
    payload = verify_token(credentials.credentials)
    user_id = payload.get("user_id")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


class StudentLoginRequest(BaseModel):
    matric_no: str
    password: str

class LecturerLoginRequest(BaseModel):
    name: str
    password: str

class RegisterStudentRequest(BaseModel):
    name: str
    password: str
    matric_no: str

class RegisterLecturerRequest(BaseModel):
    name: str
    password: str

class RegisterFaceRequest(BaseModel):
    face_image_data: str
    
class TestFaceQualityRequest(BaseModel):
    face_image_data: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


@router.post("/login/student", response_model=TokenResponse)
def login_student(request: StudentLoginRequest, db: Session = Depends(get_db)):
    """Authenticate student with matric number and password."""
    user = authenticate_user(db, request.matric_no, request.password)
    if not user or user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid matric number or password"
        )
    
    access_token = create_user_token(user)
    user_profile = get_user_profile(db, user.id)
    
    return TokenResponse(
        access_token=access_token,
        user=user_profile
    )

@router.post("/login/lecturer", response_model=TokenResponse)
def login_lecturer(request: LecturerLoginRequest, db: Session = Depends(get_db)):
    """Authenticate lecturer with name and password."""
    user = authenticate_user(db, request.name, request.password)
    if not user or user.role != "lecturer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid name or password"
        )
    
    access_token = create_user_token(user)
    user_profile = get_user_profile(db, user.id)
    
    return TokenResponse(
        access_token=access_token,
        user=user_profile
    )

@router.post("/register/student")
def register_student_endpoint(request: RegisterStudentRequest, db: Session = Depends(get_db)):
    """Register new student."""
    return register_student(db, request.name, request.password, request.matric_no)

@router.post("/register/lecturer")
def register_lecturer_endpoint(request: RegisterLecturerRequest, db: Session = Depends(get_db)):
    """Register new lecturer."""
    return register_lecturer(db, request.name, request.password)

@router.post("/register-face")
def register_face(
    request: RegisterFaceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Register face encoding for student with quality validation."""
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can register faces"
        )
    
    from app.utils.face_recognition import validate_and_encode_face
    from app.models.user import Student
    
    # Get student profile
    student = db.query(Student).filter(Student.id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )
    
    # Validate image and encode face with quality checks
    validation_result = validate_and_encode_face(request.face_image_data)
    
    if not validation_result["success"]:
        error_details = validation_result.get("error_details", {})
        
        if validation_result["error"] == "no_face_detected":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="❌ No Face Detected: Please ensure good lighting, face the camera directly, and remove any obstructions (glasses, masks, etc.). Try again with a clearer image."
            )
        elif validation_result["error"] == "multiple_faces":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"❌ Multiple Faces Detected: Found {error_details.get('face_count', 'multiple')} faces in the image. Please ensure only your face is visible in the camera."
            )
        elif validation_result["error"] == "poor_quality":
            quality_issues = error_details.get("quality_issues", [])
            issues_text = ", ".join(quality_issues) if quality_issues else "poor image quality"
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"❌ Poor Image Quality: {issues_text}. Please improve lighting, reduce blur, and ensure your face is clearly visible."
            )
        elif validation_result["error"] == "invalid_image":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="❌ Invalid Image: Cannot process the image. Please ensure you're using a valid image format and try again."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"❌ Face Registration Failed: {validation_result.get('message', 'Unknown error occurred')}"
            )
    
    # If student already has a face registered, verify it's the same person
    if student.facial_encoding:
        from app.utils.face_recognition import verify_face
        from app.core.config import settings
        
        is_same_person = verify_face(
            student.facial_encoding,
            request.face_image_data,
            tolerance=0.5  # Slightly more lenient for re-registration
        )
        
        if not is_same_person:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="❌ Face Mismatch: The new face image doesn't match your previously registered face. Please ensure you are the same person who originally registered."
            )
    
    # Save the high-quality encoding
    student.facial_encoding = validation_result["encoding"]
    student.face_registered = True
    db.commit()
    
    # Return success with quality metrics
    quality_score = validation_result.get("quality_score", 0)
    confidence = validation_result.get("confidence", 0)
    
    return {
        "message": "✅ Face registered successfully!",
        "quality_metrics": {
            "quality_score": round(quality_score, 2),
            "confidence": round(confidence, 2),
            "status": "excellent" if quality_score > 0.8 else "good" if quality_score > 0.6 else "acceptable"
        },
        "tips": [
            "Your face is now registered for attendance verification",
            "Ensure similar lighting conditions when marking attendance",
            "Face the camera directly during attendance marking"
        ]
    }

@router.get("/profile")
def get_current_user_profile(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get current user profile."""
    payload = verify_token(credentials.credentials)
    user_id = payload.get("user_id")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    profile = get_user_profile(db, user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return profile

@router.post("/test-face-quality")
def test_face_quality(
    request: TestFaceQualityRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Test face image quality before registration."""
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can test face quality"
        )
    
    from app.utils.face_recognition import validate_and_encode_face
    
    # Validate image quality without saving
    validation_result = validate_and_encode_face(request.face_image_data, test_only=True)
    
    if validation_result["success"]:
        quality_score = validation_result.get("quality_score", 0)
        confidence = validation_result.get("confidence", 0)
        
        return {
            "success": True,
            "message": "✅ Face quality is good for registration",
            "quality_metrics": {
                "quality_score": round(quality_score, 2),
                "confidence": round(confidence, 2),
                "status": "excellent" if quality_score > 0.8 else "good" if quality_score > 0.6 else "acceptable",
                "recommendation": "Ready for registration" if quality_score > 0.6 else "Consider improving lighting or image clarity"
            }
        }
    else:
        return {
            "success": False,
            "message": validation_result.get("message", "Face quality test failed"),
            "error": validation_result.get("error"),
            "suggestions": [
                "Ensure good lighting",
                "Face the camera directly",
                "Remove glasses or masks if possible",
                "Keep your face steady and centered"
            ]
        }