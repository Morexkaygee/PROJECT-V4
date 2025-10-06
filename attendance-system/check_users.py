#!/usr/bin/env python3
"""
Check existing users in the database
"""

import sqlite3
from pathlib import Path

def check_users():
    """Check what users exist in the database"""
    db_path = Path("backend/attendance.db")
    
    if not db_path.exists():
        print("[ERROR] Database file not found!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Checking users in database...")
        print("=" * 50)
        
        # Check users table
        cursor.execute("SELECT id, name, email, role, is_active FROM users")
        users = cursor.fetchall()
        
        print(f"Total users: {len(users)}")
        print()
        
        if users:
            print("Users found:")
            for user in users:
                user_id, name, email, role, is_active = user
                status = "Active" if is_active else "Inactive"
                print(f"  ID: {user_id}, Name: {name}, Email: {email}, Role: {role}, Status: {status}")
                
                # If it's a student, get matric number
                if role == "student":
                    cursor.execute("SELECT matric_no FROM students WHERE id = ?", (user_id,))
                    student_data = cursor.fetchone()
                    if student_data:
                        print(f"    Matric No: {student_data[0]}")
        else:
            print("No users found in database!")
            print("You may need to create a test user or run the initialization script.")
        
        conn.close()
        
    except Exception as e:
        print(f"[ERROR] Database error: {e}")

def create_test_user():
    """Create a test student user"""
    db_path = Path("backend/attendance.db")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if test user already exists
        cursor.execute("SELECT id FROM users WHERE email = 'test@student.com'")
        if cursor.fetchone():
            print("Test user already exists!")
            return
        
        print("Creating test student user...")
        
        # Create user (password hash for 'test123')
        password_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhM8/LeHpmNitnqy36PG2."
        
        cursor.execute("""
            INSERT INTO users (name, email, password_hash, role, is_active)
            VALUES (?, ?, ?, ?, ?)
        """, ("Test Student", "test@student.com", password_hash, "student", 1))
        
        user_id = cursor.lastrowid
        
        # Create student profile
        cursor.execute("""
            INSERT INTO students (id, matric_no, department, level, face_registered)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, "TEST/2024/001", "Computer Science", "400", 0))
        
        conn.commit()
        conn.close()
        
        print("Test user created successfully!")
        print("Login credentials:")
        print("  Matric No: TEST/2024/001")
        print("  Password: test123")
        
    except Exception as e:
        print(f"[ERROR] Failed to create test user: {e}")

if __name__ == "__main__":
    check_users()
    
    print("\\n" + "=" * 50)
    response = input("Do you want to create a test student user? (y/n): ")
    if response.lower() == 'y':
        create_test_user()