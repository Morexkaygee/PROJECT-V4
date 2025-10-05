#!/usr/bin/env python3
"""
Delete student account from database
"""
import sys
import os
from sqlalchemy.orm import Session

# Add the app directory to the path
sys.path.append(os.path.dirname(__file__))

from app.core.database import SessionLocal
from app.models.user import User, Student

def delete_student(matric_no):
    """Delete student by matric number."""
    db = SessionLocal()
    try:
        # Find student by matric number
        student = db.query(Student).filter(Student.matric_no == matric_no).first()
        
        if not student:
            print(f"Student with matric number {matric_no} not found")
            return False
        
        # Get user record
        user = db.query(User).filter(User.id == student.id).first()
        
        if user:
            print(f"Found student: {user.name} ({student.matric_no})")
            
            # Delete student profile first (foreign key constraint)
            db.delete(student)
            
            # Delete user record
            db.delete(user)
            
            db.commit()
            print(f"Successfully deleted student {matric_no}")
            return True
        else:
            print(f"User record not found for student {matric_no}")
            return False
            
    except Exception as e:
        db.rollback()
        print(f"Error deleting student: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = delete_student("IFT/19/0644")
    if success:
        print("Student account deleted successfully!")
    else:
        print("Failed to delete student account!")