#!/usr/bin/env python3
"""
Check student face registration status
"""
import sys
import os
from sqlalchemy.orm import Session

# Add the app directory to the path
sys.path.append(os.path.dirname(__file__))

from app.core.database import SessionLocal
from app.models.user import User, Student

def check_students():
    """Check all students and their face registration status."""
    db = SessionLocal()
    try:
        students = db.query(Student).all()
        print("Student Face Registration Status:")
        print("=" * 50)
        
        for student in students:
            user = db.query(User).filter(User.id == student.id).first()
            print(f"Student: {user.name} ({student.matric_no})")
            print(f"  Face Registered: {student.face_registered}")
            print(f"  Has Basic Encoding: {bool(student.facial_encoding)}")
            print(f"  Has Advanced Encoding: {bool(student.advanced_facial_encoding)}")
            print(f"  Registration Method: {student.face_registration_method}")
            print("-" * 30)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_students()