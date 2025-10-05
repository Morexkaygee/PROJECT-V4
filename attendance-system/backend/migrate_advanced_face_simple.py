#!/usr/bin/env python3
"""
Simple database migration script for advanced face recognition
Adds new columns to support multiple face recognition models
"""
import sys
import os
from sqlalchemy import text

# Add the app directory to the path
sys.path.append(os.path.dirname(__file__))

from app.core.database import engine, SessionLocal


def migrate_database():
    """Add new columns for advanced face recognition."""
    db = SessionLocal()
    
    try:
        print("Starting database migration for advanced face recognition...")
        
        # For SQLite, we need to check columns differently
        result = db.execute(text("PRAGMA table_info(students)"))
        existing_columns = [row[1] for row in result.fetchall()]
        
        if 'advanced_facial_encoding' not in existing_columns:
            print("Adding advanced_facial_encoding column...")
            db.execute(text("ALTER TABLE students ADD COLUMN advanced_facial_encoding TEXT"))
            print("advanced_facial_encoding column added")
        else:
            print("advanced_facial_encoding column already exists")
        
        if 'face_registration_method' not in existing_columns:
            print("Adding face_registration_method column...")
            db.execute(text("ALTER TABLE students ADD COLUMN face_registration_method VARCHAR(50) DEFAULT 'basic'"))
            print("face_registration_method column added")
        else:
            print("face_registration_method column already exists")
        
        # Update existing records to have 'basic' method if they have facial_encoding
        print("Updating existing face registrations...")
        db.execute(text("""
            UPDATE students 
            SET face_registration_method = 'basic' 
            WHERE facial_encoding IS NOT NULL 
            AND face_registration_method IS NULL
        """))
        
        db.commit()
        print("Database migration completed successfully!")
        
        # Show summary
        result = db.execute(text("""
            SELECT 
                COUNT(*) as total_students,
                COUNT(facial_encoding) as basic_registrations,
                COUNT(advanced_facial_encoding) as advanced_registrations
            FROM students
        """))
        
        stats = result.fetchone()
        print(f"Migration Summary:")
        print(f"- Total students: {stats[0]}")
        print(f"- Basic face registrations: {stats[1]}")
        print(f"- Advanced face registrations: {stats[2]}")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"Migration failed: {e}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = migrate_database()
    
    if success:
        print("Operation completed successfully!")
    else:
        print("Operation failed!")
        sys.exit(1)