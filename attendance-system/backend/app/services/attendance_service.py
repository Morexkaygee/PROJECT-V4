from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.attendance import AttendanceSession, Attendance
from app.models.user import Student
from app.utils.face_recognition import verify_face, verify_face_advanced
from app.utils.gps_verification import verify_location
from app.core.config import settings
from typing import Dict, Any, List
from datetime import datetime
import time


def create_attendance_session(
    db: Session,
    title: str,
    course_id: int,
    start_time: datetime,
    end_time: datetime,
    location_lat: float,
    location_lng: float,
    location_radius: float = 100.0
) -> AttendanceSession:
    """Create new attendance session."""
    try:
        session = AttendanceSession(
            title=title,
            course_id=course_id,
            start_time=start_time,
            end_time=end_time,
            location_lat=location_lat,
            location_lng=location_lng,
            location_radius=location_radius
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create attendance session"
        )


def mark_attendance_with_verification(
    db: Session,
    session_id: int,
    student_id: int,
    face_image_data: str,
    student_lat: float,
    student_lng: float
) -> Dict[str, Any]:
    """Mark attendance with face and GPS verification."""
    start_time = time.time()
    try:
        # Get session and check time window
        current_time = datetime.utcnow()
        session = db.query(AttendanceSession).filter(
            AttendanceSession.id == session_id,
            AttendanceSession.is_active == True,
            AttendanceSession.start_time <= current_time,
            AttendanceSession.end_time >= current_time
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Active session not found"
            )
        
        # Get student
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
        
        # Check if already marked
        existing_attendance = db.query(Attendance).filter(
            Attendance.session_id == session_id,
            Attendance.student_id == student_id
        ).first()
        
        if existing_attendance:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Attendance already marked for this session"
            )
        
        # Handle face recognition - STRICT VERIFICATION REQUIRED
        face_verified = False
        face_error = None
        verification_details = {}
        
        if not face_image_data:
            face_error = "❌ Face Image Missing: No face image was captured. Please ensure your camera is working and try again."
        elif not student.facial_encoding and not student.advanced_facial_encoding:
            # Student must register face first - NO attendance without registered face
            face_error = "❌ Face Not Registered: You must register your face before marking attendance. Please go to 'Register Face' in your profile first."
        else:
            # Use advanced verification if available, fallback to basic
            if student.advanced_facial_encoding and student.face_registration_method == "advanced":
                try:
                    # Use advanced multi-model verification
                    verification_result = verify_face_advanced(
                        student.advanced_facial_encoding,
                        face_image_data,
                        settings.face_recognition_tolerance
                    )
                    
                    face_verified = verification_result.get('match', False)
                    verification_details = {
                        'method': 'advanced',
                        'confidence': verification_result.get('confidence', 0.0),
                        'models_used': verification_result.get('model_results', {}),
                        'quality_score': verification_result.get('quality_score', 0.0)
                    }
                    
                    if not face_verified:
                        confidence = verification_result.get('confidence', 0.0)
                        face_error = f"❌ Advanced Face Verification Failed: Confidence {confidence:.2f} below threshold {settings.face_recognition_tolerance}. The captured face does not match your registered face with sufficient certainty."
                        
                except Exception as e:
                    # Fallback to basic verification if advanced fails
                    if student.facial_encoding:
                        face_verified = verify_face(
                            student.facial_encoding,
                            face_image_data,
                            settings.face_recognition_tolerance
                        )
                        verification_details = {'method': 'basic_fallback'}
                        if not face_verified:
                            face_error = "❌ Face Verification Failed: Could not verify face using advanced method, basic fallback also failed."
                    else:
                        face_error = "❌ Face Verification Error: Advanced verification failed and no basic encoding available."
            else:
                # Use basic verification
                from app.utils.face_recognition import encode_face_from_base64
                
                # First check if we can detect a face in the current image
                current_encoding = encode_face_from_base64(face_image_data)
                if not current_encoding:
                    face_error = "❌ No Face Detected: Cannot detect a face in the captured image. Please ensure good lighting, face the camera directly, and try again."
                else:
                    # Now verify against stored encoding
                    face_verified = verify_face(
                        student.facial_encoding,
                        face_image_data,
                        settings.face_recognition_tolerance
                    )
                    verification_details = {'method': 'basic'}
                    if not face_verified:
                        face_error = "❌ Face Mismatch: The captured face does not match your registered face. Please ensure you are the registered student and face the camera clearly."
        
        # Verify GPS location
        gps_verification = verify_location(
            student_lat,
            student_lng,
            session.location_lat,
            session.location_lng,
            session.location_radius
        )
        
        # CRITICAL: Both face AND location verification must pass - NO EXCEPTIONS
        verification_errors = []
        
        # Check face verification with detailed error
        if not face_verified:
            verification_errors.append(face_error or "❌ Face Verification Failed: Unknown face verification error")
        
        # Check location verification with detailed error
        if not gps_verification["is_valid"]:
            distance = gps_verification.get('distance_meters')
            if distance is not None:
                if distance > session.location_radius:
                    verification_errors.append(
                        f"📍 Location Too Far: You are {distance:.1f}m away from the session location. "
                        f"You must be within {session.location_radius}m to mark attendance. "
                        f"Please move closer to the classroom/session location."
                    )
                else:
                    verification_errors.append(
                        f"📍 Location Error: GPS verification failed despite being {distance:.1f}m away. "
                        f"Please check your location settings and try again."
                    )
            else:
                verification_errors.append(
                    "📍 Location Invalid: Cannot determine your location. "
                    "Please enable location services, ensure GPS is working, and try again."
                )
        
        # Provide comprehensive feedback based on what failed
        if verification_errors:
            if len(verification_errors) == 1:
                # Single failure - provide specific guidance
                error_message = verification_errors[0]
                if "Face" in error_message:
                    error_message += "\n\n💡 Face Verification Tips:\n• Ensure good lighting\n• Face the camera directly\n• Remove glasses/masks if possible\n• Keep your face steady"
                elif "Location" in error_message:
                    error_message += "\n\n💡 Location Tips:\n• Enable location services\n• Move closer to the session location\n• Ensure GPS signal is strong\n• Try refreshing your location"
            else:
                # Multiple failures - provide combined guidance
                error_message = "Multiple verification failures:\n\n" + "\n\n".join(verification_errors)
                error_message += "\n\n💡 Please fix all issues above and try again."
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )
        
        # Final safety check
        if face_verified is not True or gps_verification["is_valid"] is not True:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="❌ Verification Error: Both face and location verification must pass. Please try again."
            )
        
        # Mark attendance ONLY after all verifications pass
        attendance = Attendance(
            session_id=session_id,
            student_id=student_id,
            present=True,
            verification_method="face_gps_verified",
            student_lat=student_lat,
            student_lng=student_lng,
            face_confidence_score=verification_details.get('confidence', 0.0),
            gps_accuracy_meters=gps_verification.get('distance_meters', 0.0),
            processing_time_ms=int((time.time() - start_time) * 1000) if 'start_time' in locals() else 0,
            verification_status='accepted'
        )
        
        db.add(attendance)
        db.commit()
        
        # Log successful verification for audit
        print(f"ATTENDANCE MARKED: Student {student_id} verified for session {session_id} - "
              f"Face: {face_verified}, Location: {gps_verification['is_valid']}, "
              f"Distance: {gps_verification.get('distance_meters', 'N/A')}m")
        
        return {
            "message": "Attendance marked successfully",
            "verification": {
                "face_verified": face_verified,
                "location_verified": gps_verification["is_valid"],
                "distance_meters": gps_verification["distance_meters"],
                "face_verification_details": verification_details
            }
        }
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark attendance"
        )


def validate_attendance_integrity(db: Session, attendance_id: int) -> bool:
    """Validate that an attendance record meets all verification requirements."""
    try:
        attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
        if not attendance:
            return False
        
        # Check that verification method indicates proper verification
        if attendance.verification_method != "face_gps_verified":
            return False
        
        # Check that location data exists
        if attendance.student_lat is None or attendance.student_lng is None:
            return False
        
        # Get session and verify location is within range
        session = db.query(AttendanceSession).filter(AttendanceSession.id == attendance.session_id).first()
        if not session:
            return False
        
        location_check = verify_location(
            attendance.student_lat,
            attendance.student_lng,
            session.location_lat,
            session.location_lng,
            session.location_radius
        )
        
        return location_check["is_valid"]
    except Exception:
        return False


def get_session_attendance(db: Session, session_id: int) -> List[Dict[str, Any]]:
    """Get attendance records for a session."""
    try:
        attendances = db.query(Attendance).filter(
            Attendance.session_id == session_id
        ).all()
        
        result = []
        for attendance in attendances:
            student = db.query(Student).filter(Student.id == attendance.student_id).first()
            if student:
                # Validate attendance integrity
                is_valid = validate_attendance_integrity(db, attendance.id)
                
                result.append({
                    "student_id": student.id,
                    "student_name": student.user.name,
                    "matric_no": student.matric_no,
                    "marked_at": attendance.marked_at,
                    "present": attendance.present,
                    "verification_method": attendance.verification_method,
                    "verified": is_valid
                })
        
        return result
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve attendance records"
        )