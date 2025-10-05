#!/usr/bin/env python3
"""
Simple test for advanced face recognition system
"""
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.dirname(__file__))

def test_system():
    """Test the system components."""
    print("Testing Advanced Face Recognition System")
    print("=" * 50)
    
    # Test basic imports
    try:
        import face_recognition
        print("PASS: face_recognition library")
    except ImportError:
        print("FAIL: face_recognition library")
    
    try:
        from deepface import DeepFace
        print("PASS: DeepFace library")
    except ImportError:
        print("FAIL: DeepFace library")
    
    try:
        import mediapipe
        print("PASS: MediaPipe library")
    except ImportError:
        print("FAIL: MediaPipe library")
    
    # Test advanced system
    try:
        from app.utils.advanced_face_recognition import advanced_face_recognition
        models_count = len(advanced_face_recognition.models)
        print(f"PASS: Advanced system loaded ({models_count} models)")
    except Exception as e:
        print(f"FAIL: Advanced system - {e}")
    
    # Test API
    try:
        from app.api.face_registration import router
        print("PASS: Face registration API")
    except Exception as e:
        print(f"FAIL: Face registration API - {e}")
    
    # Test database migration
    try:
        from app.core.database import SessionLocal
        from sqlalchemy import text
        
        db = SessionLocal()
        result = db.execute(text("PRAGMA table_info(students)"))
        columns = [row[1] for row in result.fetchall()]
        db.close()
        
        if 'advanced_facial_encoding' in columns:
            print("PASS: Database migration")
        else:
            print("FAIL: Database migration")
            
    except Exception as e:
        print(f"FAIL: Database test - {e}")
    
    print("\n" + "=" * 50)
    print("System Status: Ready for testing")
    print("Frontend: http://localhost:3001")
    print("Backend API: Start with 'python start.py'")

if __name__ == "__main__":
    test_system()