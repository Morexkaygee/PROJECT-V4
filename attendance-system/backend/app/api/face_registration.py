"""
Advanced Face Registration API
Handles face registration using multiple state-of-the-art models
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User, Student
from app.utils.face_recognition import validate_and_encode_face_advanced, validate_and_encode_face
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/face", tags=["face-registration"])


class FaceRegistrationRequest(BaseModel):
    face_image_data: str
    use_advanced: bool = True


class FaceTestRequest(BaseModel):
    face_image_data: str


@router.post("/register")
def register_face(
    request: FaceRegistrationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Register student's face using advanced multi-model approach."""
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can register faces"
        )
    
    student = db.query(Student).filter(Student.id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )
    
    try:
        if request.use_advanced:
            # Use advanced multi-model face registration
            result = validate_and_encode_face_advanced(request.face_image_data)
            
            if not result["success"]:
                return {
                    "success": False,
                    "error": result["error"],
                    "message": result["message"],
                    "error_details": result.get("error_details", {})
                }
            
            # Store advanced encoding
            student.advanced_facial_encoding = result.get("advanced_encoding")
            student.face_registration_method = "advanced"
            
            # Also store legacy encoding for backward compatibility
            if "encoding" in result:
                student.facial_encoding = result["encoding"]
            
            success_message = f"Face registered successfully using {len(result.get('models_used', []))} models"
            models_info = {
                "models_used": result.get("models_used", []),
                "quality_score": result.get("quality_score", 0.0),
                "confidence": result.get("confidence", 0.0)
            }
        else:
            # Use basic face registration
            result = validate_and_encode_face(request.face_image_data)
            
            if not result["success"]:
                return {
                    "success": False,
                    "error": result["error"],
                    "message": result["message"],
                    "error_details": result.get("error_details", {})
                }
            
            student.facial_encoding = result["encoding"]
            student.face_registration_method = "basic"
            
            success_message = "Face registered successfully using basic method"
            models_info = {
                "quality_score": result.get("quality_score", 0.0),
                "confidence": result.get("confidence", 0.0)
            }
        
        student.face_registered = True
        db.commit()
        
        return {
            "success": True,
            "message": success_message,
            "registration_method": student.face_registration_method,
            **models_info
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Face registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Face registration failed due to server error"
        )


@router.post("/test")
def test_face_quality(
    request: FaceTestRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Test face image quality without registering."""
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can test face quality"
        )
    
    try:
        # Test with advanced method
        advanced_result = validate_and_encode_face_advanced(request.face_image_data, test_only=True)
        
        # Test with basic method for comparison
        basic_result = validate_and_encode_face(request.face_image_data, test_only=True)
        
        return {
            "advanced_analysis": {
                "success": advanced_result["success"],
                "quality_score": advanced_result.get("quality_score", 0.0),
                "confidence": advanced_result.get("confidence", 0.0),
                "models_used": advanced_result.get("models_used", []),
                "error": advanced_result.get("error"),
                "message": advanced_result.get("message")
            },
            "basic_analysis": {
                "success": basic_result["success"],
                "quality_score": basic_result.get("quality_score", 0.0),
                "confidence": basic_result.get("confidence", 0.0),
                "error": basic_result.get("error"),
                "message": basic_result.get("message")
            },
            "recommendation": "advanced" if advanced_result["success"] else "basic" if basic_result["success"] else "retake"
        }
        
    except Exception as e:
        logger.error(f"Face quality test error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Face quality test failed"
        )


@router.get("/status")
def get_face_registration_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current face registration status."""
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can check face registration status"
        )
    
    student = db.query(Student).filter(Student.id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )
    
    return {
        "face_registered": student.face_registered,
        "registration_method": student.face_registration_method or "none",
        "has_basic_encoding": bool(student.facial_encoding),
        "has_advanced_encoding": bool(student.advanced_facial_encoding),
        "can_upgrade": student.face_registered and student.face_registration_method == "basic"
    }


@router.post("/upgrade")
def upgrade_to_advanced_registration(
    request: FaceRegistrationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upgrade existing basic face registration to advanced multi-model registration."""
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can upgrade face registration"
        )
    
    student = db.query(Student).filter(Student.id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )
    
    if not student.face_registered:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No existing face registration found. Use /register endpoint instead."
        )
    
    if student.face_registration_method == "advanced":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Face registration is already using advanced method"
        )
    
    try:
        # Perform advanced face registration
        result = validate_and_encode_face_advanced(request.face_image_data)
        
        if not result["success"]:
            return {
                "success": False,
                "error": result["error"],
                "message": result["message"],
                "error_details": result.get("error_details", {})
            }
        
        # Update to advanced encoding
        student.advanced_facial_encoding = result.get("advanced_encoding")
        student.face_registration_method = "advanced"
        
        # Keep legacy encoding for backward compatibility
        if "encoding" in result:
            student.facial_encoding = result["encoding"]
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Face registration upgraded to advanced method using {len(result.get('models_used', []))} models",
            "models_used": result.get("models_used", []),
            "quality_score": result.get("quality_score", 0.0),
            "confidence": result.get("confidence", 0.0)
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Face registration upgrade error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Face registration upgrade failed"
        )


@router.delete("/unregister")
def unregister_face(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove face registration."""
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can unregister faces"
        )
    
    student = db.query(Student).filter(Student.id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )
    
    if not student.face_registered:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No face registration found"
        )
    
    try:
        student.facial_encoding = None
        student.advanced_facial_encoding = None
        student.face_registered = False
        student.face_registration_method = None
        
        db.commit()
        
        return {
            "success": True,
            "message": "Face registration removed successfully"
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Face unregistration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Face unregistration failed"
        )