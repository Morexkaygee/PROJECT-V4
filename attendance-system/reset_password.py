#!/usr/bin/env python3
"""
Reset password for a student account
"""

import sqlite3
import bcrypt
from pathlib import Path

def reset_student_password(matric_no, new_password):
    """Reset password for a student"""
    db_path = Path("backend/attendance.db")
    
    if not db_path.exists():
        print("[ERROR] Database file not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Find the student
        cursor.execute("""
            SELECT u.id, u.name, s.matric_no 
            FROM users u 
            JOIN students s ON u.id = s.id 
            WHERE s.matric_no = ? AND u.role = 'student'
        """, (matric_no,))
        
        user = cursor.fetchone()
        if not user:
            print(f"[ERROR] Student with matric number {matric_no} not found!")
            return False
        
        user_id, name, matric = user
        print(f"Found student: {name} ({matric})")
        
        # Hash the new password
        password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Update the password
        cursor.execute("UPDATE users SET hashed_password = ? WHERE id = ?", (password_hash, user_id))
        
        conn.commit()
        conn.close()
        
        print(f"[SUCCESS] Password updated for {name}")
        print(f"New login credentials:")
        print(f"  Matric No: {matric}")
        print(f"  Password: {new_password}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to reset password: {e}")
        return False

def main():
    print("Student Password Reset Tool")
    print("=" * 40)
    
    # Your matric number
    matric_no = "IFT/19/0644"
    new_password = "newpass123"
    
    print(f"Resetting password for matric number: {matric_no}")
    print(f"New password will be: {new_password}")
    
    if reset_student_password(matric_no, new_password):
        print("\\n[SUCCESS] You can now login with your account!")
        print("\\nTest the login:")
        print("1. Go to the student login page")
        print(f"2. Enter matric number: {matric_no}")
        print(f"3. Enter password: {new_password}")
    else:
        print("\\n[FAILED] Could not reset password")

if __name__ == "__main__":
    main()