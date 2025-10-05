#!/usr/bin/env python3
"""
Simple Evaluation Metrics for Attendance Management System
"""
import sys
import os
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

# Add the app directory to the path
sys.path.append(os.path.dirname(__file__))

from app.core.database import SessionLocal
from app.models.user import User, Student, Lecturer
from app.models.course import Course, CourseStudent
from app.models.attendance import AttendanceSession, Attendance


def run_evaluation():
    """Run simple evaluation metrics."""
    db = SessionLocal()
    
    try:
        print("ATTENDANCE SYSTEM EVALUATION REPORT")
        print("=" * 50)
        
        # Basic Statistics
        print("\nSYSTEM OVERVIEW")
        print("-" * 30)
        total_users = db.query(User).count()
        total_students = db.query(Student).count()
        total_lecturers = db.query(Lecturer).count()
        total_courses = db.query(Course).count()
        total_sessions = db.query(AttendanceSession).count()
        total_attendance = db.query(Attendance).count()
        
        print(f"Total Users: {total_users}")
        print(f"Students: {total_students}")
        print(f"Lecturers: {total_lecturers}")
        print(f"Courses: {total_courses}")
        print(f"Sessions: {total_sessions}")
        print(f"Attendance Records: {total_attendance}")
        
        # Face Recognition Metrics
        print("\nFACE RECOGNITION METRICS")
        print("-" * 30)
        
        students_with_face = db.query(Student).filter(Student.face_registered == True).count()
        basic_registrations = db.query(Student).filter(Student.facial_encoding.isnot(None)).count()
        advanced_registrations = db.query(Student).filter(Student.advanced_facial_encoding.isnot(None)).count()
        
        face_registration_rate = (students_with_face / total_students * 100) if total_students > 0 else 0
        
        print(f"Face Registration Rate: {face_registration_rate:.1f}%")
        print(f"Students with Face Registered: {students_with_face}/{total_students}")
        print(f"Basic Face Registrations: {basic_registrations}")
        print(f"Advanced Face Registrations: {advanced_registrations}")
        print(f"Unregistered Students: {total_students - students_with_face}")
        
        # Attendance Verification
        print("\nATTENDANCE VERIFICATION")
        print("-" * 30)
        
        face_verified = db.query(Attendance).filter(
            Attendance.verification_method == 'face_gps_verified'
        ).count()
        
        gps_verified = db.query(Attendance).filter(
            Attendance.student_lat.isnot(None),
            Attendance.student_lng.isnot(None)
        ).count()
        
        verification_success_rate = (face_verified / total_attendance * 100) if total_attendance > 0 else 0
        gps_verification_rate = (gps_verified / total_attendance * 100) if total_attendance > 0 else 0
        
        print(f"Face Verification Success Rate: {verification_success_rate:.1f}%")
        print(f"GPS Verification Rate: {gps_verification_rate:.1f}%")
        print(f"Successfully Verified Attendances: {face_verified}/{total_attendance}")
        
        # Session Statistics
        print("\nSESSION STATISTICS")
        print("-" * 30)
        
        active_sessions = db.query(AttendanceSession).filter(AttendanceSession.is_active == True).count()
        
        # Average attendance per session
        if total_sessions > 0:
            avg_attendance_per_session = total_attendance / total_sessions
        else:
            avg_attendance_per_session = 0
        
        print(f"Active Sessions: {active_sessions}")
        print(f"Average Attendance per Session: {avg_attendance_per_session:.1f}")
        
        # Course Enrollment
        print("\nCOURSE METRICS")
        print("-" * 30)
        
        total_enrollments = db.query(CourseStudent).count()
        avg_enrollment_per_course = (total_enrollments / total_courses) if total_courses > 0 else 0
        
        print(f"Total Course Enrollments: {total_enrollments}")
        print(f"Average Students per Course: {avg_enrollment_per_course:.1f}")
        
        # System Health Score
        print("\nSYSTEM HEALTH SCORE")
        print("-" * 30)
        
        # Calculate overall health score (0-100)
        health_factors = []
        
        # Face registration coverage (25% weight)
        health_factors.append(min(face_registration_rate, 100) * 0.25)
        
        # Verification success rate (35% weight)
        health_factors.append(verification_success_rate * 0.35)
        
        # GPS verification rate (25% weight)
        health_factors.append(gps_verification_rate * 0.25)
        
        # System usage (15% weight) - based on attendance records
        usage_score = min((total_attendance / max(total_students, 1)) * 20, 100)
        health_factors.append(usage_score * 0.15)
        
        overall_health = sum(health_factors)
        
        print(f"Overall System Health: {overall_health:.1f}/100")
        
        if overall_health >= 80:
            print("Status: EXCELLENT")
        elif overall_health >= 60:
            print("Status: GOOD")
        elif overall_health >= 40:
            print("Status: FAIR")
        else:
            print("Status: NEEDS IMPROVEMENT")
        
        # Recommendations
        print("\nRECOMMENDATIONS")
        print("-" * 30)
        
        if face_registration_rate < 80:
            print("• Encourage more students to register their faces")
        
        if verification_success_rate < 90:
            print("• Improve face recognition accuracy")
        
        if active_sessions == 0:
            print("• Create active attendance sessions")
        
        if total_attendance < total_students:
            print("• Increase system usage and engagement")
        
        if advanced_registrations < basic_registrations:
            print("• Promote advanced face recognition features")
        
        # Performance Summary
        print("\nPERFORMANCE SUMMARY")
        print("-" * 30)
        print(f"System Adoption: {(total_attendance / max(total_students, 1) * 100):.1f}%")
        print(f"Technology Adoption: {face_registration_rate:.1f}%")
        print(f"Security Level: {verification_success_rate:.1f}%")
        print(f"Data Quality: {gps_verification_rate:.1f}%")
        
        # Save summary to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"evaluation_summary_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            f.write(f"Attendance System Evaluation - {datetime.now()}\n")
            f.write("=" * 50 + "\n")
            f.write(f"Total Users: {total_users}\n")
            f.write(f"Face Registration Rate: {face_registration_rate:.1f}%\n")
            f.write(f"Verification Success Rate: {verification_success_rate:.1f}%\n")
            f.write(f"Overall Health Score: {overall_health:.1f}/100\n")
        
        print(f"\nSummary saved to: {filename}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    run_evaluation()