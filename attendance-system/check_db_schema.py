#!/usr/bin/env python3
"""
Check database schema
"""

import sqlite3
from pathlib import Path

def check_schema():
    """Check database table schemas"""
    db_path = Path("backend/attendance.db")
    
    if not db_path.exists():
        print("[ERROR] Database file not found!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get users table schema
        cursor.execute("PRAGMA table_info(users)")
        users_columns = cursor.fetchall()
        
        print("Users table schema:")
        print("-" * 40)
        for col in users_columns:
            print(f"  {col[1]} ({col[2]}) - {col}")
        
        print("\\nStudents table schema:")
        print("-" * 40)
        cursor.execute("PRAGMA table_info(students)")
        students_columns = cursor.fetchall()
        
        for col in students_columns:
            print(f"  {col[1]} ({col[2]}) - {col}")
        
        # Check a sample user record
        print("\\nSample user record:")
        print("-" * 40)
        cursor.execute("SELECT * FROM users WHERE role = 'student' LIMIT 1")
        sample_user = cursor.fetchone()
        if sample_user:
            print(f"Sample: {sample_user}")
        
        conn.close()
        
    except Exception as e:
        print(f"[ERROR] Database error: {e}")

if __name__ == "__main__":
    check_schema()