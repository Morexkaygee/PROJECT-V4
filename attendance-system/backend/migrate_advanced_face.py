#!/usr/bin/env python3
"""
Database migration script for advanced face recognition
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
        
        # Check if columns already exist
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'students' 
            AND column_name IN ('advanced_facial_encoding', 'face_registration_method')
        """))
        
        existing_columns = [row[0] for row in result.fetchall()]
        
        if 'advanced_facial_encoding' not in existing_columns:
            print("Adding advanced_facial_encoding column...")
            db.execute(text("""
                ALTER TABLE students 
                ADD COLUMN advanced_facial_encoding TEXT
            """))
            print("✓ advanced_facial_encoding column added")
        else:
            print("✓ advanced_facial_encoding column already exists")
        
        if 'face_registration_method' not in existing_columns:
            print("Adding face_registration_method column...")
            db.execute(text("""
                ALTER TABLE students 
                ADD COLUMN face_registration_method VARCHAR(50) DEFAULT 'basic'
            """))
            print("✓ face_registration_method column added")
        else:
            print("✓ face_registration_method column already exists")
        
        # Update existing records to have 'basic' method if they have facial_encoding
        print("Updating existing face registrations...")
        db.execute(text("""
            UPDATE students 
            SET face_registration_method = 'basic' 
            WHERE facial_encoding IS NOT NULL 
            AND face_registration_method IS NULL
        """))
        
        db.commit()
        print("✓ Database migration completed successfully!")
        
        # Show summary
        result = db.execute(text("""
            SELECT 
                COUNT(*) as total_students,
                COUNT(facial_encoding) as basic_registrations,
                COUNT(advanced_facial_encoding) as advanced_registrations
            FROM students
        """))
        
        stats = result.fetchone()
        print(f"\nMigration Summary:")
        print(f"- Total students: {stats[0]}")
        print(f"- Basic face registrations: {stats[1]}")
        print(f"- Advanced face registrations: {stats[2]}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Migration failed: {e}")
        return False
    finally:
        db.close()
    
    return True


def rollback_migration():
    """Rollback the migration (remove new columns)."""
    db = SessionLocal()
    
    try:
        print("Rolling back advanced face recognition migration...")
        
        # Remove new columns
        try:
            db.execute(text("ALTER TABLE students DROP COLUMN advanced_facial_encoding"))
            print("✓ Removed advanced_facial_encoding column")
        except Exception as e:
            print(f"⚠ Could not remove advanced_facial_encoding: {e}")
        
        try:
            db.execute(text("ALTER TABLE students DROP COLUMN face_registration_method"))
            print("✓ Removed face_registration_method column")
        except Exception as e:
            print(f"⚠ Could not remove face_registration_method: {e}")
        
        db.commit()
        print("✓ Migration rollback completed!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Rollback failed: {e}")
        return False
    finally:
        db.close()
    
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate database for advanced face recognition")
    parser.add_argument("--rollback", action="store_true", help="Rollback the migration")
    
    args = parser.parse_args()
    
    if args.rollback:
        success = rollback_migration()
    else:
        success = migrate_database()
    
    if success:
        print("\n🎉 Operation completed successfully!")
    else:
        print("\n💥 Operation failed!")
        sys.exit(1)