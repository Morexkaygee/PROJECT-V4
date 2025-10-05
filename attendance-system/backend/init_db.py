#!/usr/bin/env python3
"""
Database initialization script
Creates tables and optionally adds sample data
"""
import sys
import os
from sqlalchemy.orm import Session

# Add the app directory to the path
sys.path.append(os.path.dirname(__file__))

from app.core.database import engine, SessionLocal, Base
from app.models import *
from app.core.security import get_password_hash


def create_tables():
    """Create all database tables."""
    try:
        # Import all models to ensure they're registered
        from app.models.user import User, Student, Lecturer
        from app.models.course import Course, CourseStudent
        from app.models.attendance import AttendanceSession, Attendance
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
        return True
    except Exception as e:
        print(f"Error creating tables: {e}")
        return False


def create_sample_data():
    """Create sample lecturer and student for testing."""
    db = SessionLocal()
    try:
        # Check if sample data already exists
        existing_lecturer = db.query(User).filter(User.name == "Dr. Sample Lecturer").first()
        if existing_lecturer:
            print("Sample data already exists")
            return
        
        # Create sample lecturer
        lecturer_user = User(
            name="Dr. Sample Lecturer",
            hashed_password=get_password_hash("lecturer123"),
            role="lecturer"
        )
        db.add(lecturer_user)
        db.flush()
        
        lecturer_profile = Lecturer(
            id=lecturer_user.id,
            department="Computer Science",
            title="Dr.",
            staff_id="FUTA/CSC/001"
        )
        db.add(lecturer_profile)
        
        # Create sample student
        student_user = User(
            name="Sample Student",
            hashed_password=get_password_hash("student123"),
            role="student"
        )
        db.add(student_user)
        db.flush()
        
        student_profile = Student(
            id=student_user.id,
            matric_no="CSC/2020/001"
        )
        db.add(student_profile)
        
        db.commit()
        print("Sample data created:")
        print("- Lecturer: Dr. Sample Lecturer / lecturer123")
        print("- Student: CSC/2020/001 / student123")
        
    except Exception as e:
        db.rollback()
        print(f"Error creating sample data: {e}")
    finally:
        db.close()


def main():
    """Main initialization function."""
    print("Initializing Attendance Management System Database...")
    
    if create_tables():
        create_sample_data()
        print("Database initialization completed!")
        print("\nNext steps:")
        print("1. Update your .env file with proper DATABASE_URL and SECRET_KEY")
        print("2. Run: python start.py")
        print("3. Access API docs at: http://localhost:8000/docs")
    else:
        print("Database initialization failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()