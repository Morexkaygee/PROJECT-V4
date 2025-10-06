#!/usr/bin/env python3
"""
Troubleshooting script for student dashboard data loading issues
"""

import requests
import json
import sqlite3
import os
from pathlib import Path

def check_backend_server():
    """Check if backend server is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend server is running")
            return True
        else:
            print(f"❌ Backend server responded with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend server is not running or not accessible")
        return False
    except Exception as e:
        print(f"❌ Error checking backend server: {e}")
        return False

def check_database():
    """Check database connection and tables"""
    db_path = Path("backend/attendance.db")
    if not db_path.exists():
        print("❌ Database file not found")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if required tables exist
        tables = ['users', 'students', 'courses', 'course_students']
        for table in tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if not cursor.fetchone():
                print(f"❌ Table '{table}' not found in database")
                return False
        
        print("✅ Database and tables exist")
        
        # Check if there are any students
        cursor.execute("SELECT COUNT(*) FROM students")
        student_count = cursor.fetchone()[0]
        print(f"📊 Students in database: {student_count}")
        
        # Check if there are any courses
        cursor.execute("SELECT COUNT(*) FROM courses")
        course_count = cursor.fetchone()[0]
        print(f"📊 Courses in database: {course_count}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_api_endpoints():
    """Test critical API endpoints"""
    base_url = "http://localhost:8000"
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Root API endpoint working")
        else:
            print(f"❌ Root API endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root API endpoint error: {e}")
    
    # Test courses endpoint (should work without auth)
    try:
        response = requests.get(f"{base_url}/courses/", timeout=5)
        if response.status_code == 200:
            print("✅ Courses API endpoint working")
            courses = response.json()
            print(f"📊 Available courses: {len(courses)}")
        else:
            print(f"❌ Courses API endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Courses API endpoint error: {e}")

def check_frontend_config():
    """Check frontend configuration"""
    api_file = Path("frontend/src/utils/api.ts")
    if not api_file.exists():
        print("❌ Frontend API configuration file not found")
        return False
    
    try:
        with open(api_file, 'r') as f:
            content = f.read()
            if "localhost:8000" in content or "8000" in content:
                print("✅ Frontend API configuration looks correct")
                return True
            else:
                print("❌ Frontend API configuration may be incorrect")
                return False
    except Exception as e:
        print(f"❌ Error reading frontend config: {e}")
        return False

def create_test_data():
    """Create test data if database is empty"""
    try:
        db_path = Path("backend/attendance.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if we have any students
        cursor.execute("SELECT COUNT(*) FROM students")
        student_count = cursor.fetchone()[0]
        
        if student_count == 0:
            print("🔧 Creating test student data...")
            
            # Create a test student user
            cursor.execute("""
                INSERT OR IGNORE INTO users (name, email, password_hash, role, is_active)
                VALUES ('Test Student', 'student@test.com', '$2b$12$test_hash', 'student', 1)
            """)
            
            user_id = cursor.lastrowid
            if user_id:
                cursor.execute("""
                    INSERT OR IGNORE INTO students (id, matric_no, department, level, face_registered)
                    VALUES (?, 'TEST/001', 'Computer Science', '400', 0)
                """, (user_id,))
                
                print("✅ Test student created")
        
        # Check if we have any courses
        cursor.execute("SELECT COUNT(*) FROM courses")
        course_count = cursor.fetchone()[0]
        
        if course_count == 0:
            print("🔧 Creating test course data...")
            
            # Create a test lecturer first
            cursor.execute("""
                INSERT OR IGNORE INTO users (name, email, password_hash, role, is_active)
                VALUES ('Test Lecturer', 'lecturer@test.com', '$2b$12$test_hash', 'lecturer', 1)
            """)
            
            lecturer_id = cursor.lastrowid
            if lecturer_id:
                cursor.execute("""
                    INSERT OR IGNORE INTO lecturers (id, staff_id, department)
                    VALUES (?, 'STAFF/001', 'Computer Science')
                """, (lecturer_id,))
                
                cursor.execute("""
                    INSERT OR IGNORE INTO courses (name, code, lecturer_id)
                    VALUES ('Test Course', 'CSC101', ?)
                """, (lecturer_id,))
                
                print("✅ Test course created")
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        return False

def main():
    """Main troubleshooting function"""
    print("🔍 Troubleshooting Student Dashboard Issues...")
    print("=" * 50)
    
    # Change to project directory
    os.chdir(Path(__file__).parent)
    
    # Check backend server
    server_running = check_backend_server()
    
    # Check database
    db_ok = check_database()
    
    # Check frontend config
    frontend_ok = check_frontend_config()
    
    if server_running:
        # Test API endpoints
        test_api_endpoints()
    
    # Create test data if needed
    if db_ok and not server_running:
        create_test_data()
    
    print("\n" + "=" * 50)
    print("🔧 RECOMMENDATIONS:")
    
    if not server_running:
        print("1. Start the backend server:")
        print("   cd backend")
        print("   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        print()
    
    if not db_ok:
        print("2. Initialize the database:")
        print("   cd backend")
        print("   python init_db.py")
        print()
    
    if not frontend_ok:
        print("3. Check frontend API configuration in frontend/src/utils/api.ts")
        print()
    
    print("4. Clear browser cache and localStorage:")
    print("   - Open browser developer tools (F12)")
    print("   - Go to Application/Storage tab")
    print("   - Clear localStorage and sessionStorage")
    print()
    
    print("5. Check browser console for JavaScript errors")
    print()
    
    print("6. Try logging in again with fresh credentials")

if __name__ == "__main__":
    main()