#!/usr/bin/env python3
"""
Simple database viewer script
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.core.database import SessionLocal
from app.models.user import User, Student, Lecturer

def view_database():
    db = SessionLocal()
    try:
        print("=== USERS ===")
        users = db.query(User).all()
        for user in users:
            print(f"ID: {user.id}, Name: {user.name}, Role: {user.role}")
        
        print("\n=== STUDENTS ===")
        students = db.query(Student).all()
        for student in students:
            user = db.query(User).filter(User.id == student.id).first()
            print(f"ID: {student.id}, Name: {user.name}, Matric: {student.matric_no}, Face: {bool(student.facial_encoding)}")
        
        print("\n=== LECTURERS ===")
        lecturers = db.query(Lecturer).all()
        for lecturer in lecturers:
            user = db.query(User).filter(User.id == lecturer.id).first()
            print(f"ID: {lecturer.id}, Name: {user.name}")
            
    finally:
        db.close()

if __name__ == "__main__":
    view_database()