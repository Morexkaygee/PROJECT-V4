#!/usr/bin/env python3
"""
Create sample data for testing
"""
import sys
import os
from sqlalchemy.orm import Session

# Add the app directory to the path
sys.path.append(os.path.dirname(__file__))

from app.core.database import SessionLocal
from app.models.user import User, Lecturer
from app.models.course import Course
from app.core.security import get_password_hash

def create_sample_data():
    """Create sample lecturer and course data."""
    db = SessionLocal()
    try:
        # Create sample lecturer
        existing_lecturer = db.query(User).filter(User.email == "lecturer@futa.edu.ng").first()
        if not existing_lecturer:
            lecturer_user = User(
                name="Dr. John Smith",
                email="lecturer@futa.edu.ng",
                hashed_password=get_password_hash("lecturer123"),
                role="lecturer"
            )
            db.add(lecturer_user)
            db.flush()
            
            lecturer_profile = Lecturer(id=lecturer_user.id)
            db.add(lecturer_profile)
            db.flush()
            
            # Create sample course
            course = Course(
                name="Computer Science 301",
                code="CSC301",
                lecturer_id=lecturer_user.id
            )
            db.add(course)
            
            db.commit()
            print("Sample lecturer and course created:")
            print("Lecturer: lecturer@futa.edu.ng / lecturer123")
            print("Course: CSC301 - Computer Science 301")
        else:
            print("Sample data already exists")
            
    except Exception as e:
        db.rollback()
        print(f"Error creating sample data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data()