#!/usr/bin/env python3
"""
Evaluation Metrics for Attendance Management System
Analyzes system performance, accuracy, and usage statistics
"""
import sys
import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, text
import json

# Add the app directory to the path
sys.path.append(os.path.dirname(__file__))

from app.core.database import SessionLocal
from app.models.user import User, Student, Lecturer
from app.models.course import Course, CourseStudent
from app.models.attendance import AttendanceSession, Attendance


class AttendanceSystemEvaluator:
    def __init__(self):
        self.db = SessionLocal()
        self.metrics = {}
    
    def calculate_system_metrics(self):
        """Calculate comprehensive system metrics."""
        print("Calculating Attendance Management System Metrics...")
        print("=" * 60)
        
        # Basic system statistics
        self.metrics['system_stats'] = self._get_system_stats()
        
        # Face recognition metrics
        self.metrics['face_recognition'] = self._get_face_recognition_metrics()
        
        # Attendance accuracy metrics
        self.metrics['attendance_accuracy'] = self._get_attendance_accuracy()
        
        # Usage patterns
        self.metrics['usage_patterns'] = self._get_usage_patterns()
        
        # Performance metrics
        self.metrics['performance'] = self._get_performance_metrics()
        
        # Security metrics
        self.metrics['security'] = self._get_security_metrics()
        
        return self.metrics
    
    def _get_system_stats(self):
        """Get basic system statistics."""
        stats = {}
        
        # User statistics
        stats['total_users'] = self.db.query(User).count()
        stats['total_students'] = self.db.query(Student).count()
        stats['total_lecturers'] = self.db.query(Lecturer).count()
        
        # Course statistics
        stats['total_courses'] = self.db.query(Course).count()
        stats['total_enrollments'] = self.db.query(CourseStudent).count()
        
        # Session statistics
        stats['total_sessions'] = self.db.query(AttendanceSession).count()
        stats['active_sessions'] = self.db.query(AttendanceSession).filter(
            AttendanceSession.is_active == True
        ).count()
        
        # Attendance statistics
        stats['total_attendance_records'] = self.db.query(Attendance).count()
        
        return stats
    
    def _get_face_recognition_metrics(self):
        """Analyze face recognition system performance."""
        metrics = {}
        
        # Face registration statistics
        students_with_face = self.db.query(Student).filter(
            Student.face_registered == True
        ).count()
        
        basic_registrations = self.db.query(Student).filter(
            Student.facial_encoding.isnot(None),
            Student.face_registration_method == 'basic'
        ).count()
        
        advanced_registrations = self.db.query(Student).filter(
            Student.advanced_facial_encoding.isnot(None),
            Student.face_registration_method == 'advanced'
        ).count()
        
        total_students = self.db.query(Student).count()
        
        metrics['face_registration_rate'] = (students_with_face / total_students * 100) if total_students > 0 else 0
        metrics['basic_registrations'] = basic_registrations
        metrics['advanced_registrations'] = advanced_registrations
        metrics['unregistered_students'] = total_students - students_with_face
        
        # Face verification success rate
        face_verified_attendance = self.db.query(Attendance).filter(
            Attendance.verification_method == 'face_gps_verified'
        ).count()
        
        total_attendance = self.db.query(Attendance).count()
        
        metrics['face_verification_success_rate'] = (
            face_verified_attendance / total_attendance * 100
        ) if total_attendance > 0 else 0
        
        return metrics
    
    def _get_attendance_accuracy(self):
        """Calculate attendance accuracy metrics."""
        metrics = {}
        
        # Verification method distribution
        verification_methods = self.db.query(
            Attendance.verification_method,
            func.count(Attendance.id).label('count')
        ).group_by(Attendance.verification_method).all()
        
        metrics['verification_methods'] = {
            method: count for method, count in verification_methods
        }
        
        # GPS accuracy (within radius)
        gps_verified = self.db.query(Attendance).filter(
            Attendance.student_lat.isnot(None),
            Attendance.student_lng.isnot(None)
        ).count()
        
        total_attendance = self.db.query(Attendance).count()
        
        metrics['gps_verification_rate'] = (
            gps_verified / total_attendance * 100
        ) if total_attendance > 0 else 0
        
        return metrics
    
    def _get_usage_patterns(self):
        """Analyze system usage patterns."""
        metrics = {}
        
        # Daily attendance patterns
        daily_attendance = self.db.query(
            func.date(Attendance.marked_at).label('date'),
            func.count(Attendance.id).label('count')
        ).group_by(func.date(Attendance.marked_at)).order_by('date').all()
        
        metrics['daily_attendance'] = [
            {'date': str(date), 'count': count} for date, count in daily_attendance
        ]
        
        # Peak usage hours
        hourly_usage = self.db.query(
            func.extract('hour', Attendance.marked_at).label('hour'),
            func.count(Attendance.id).label('count')
        ).group_by(func.extract('hour', Attendance.marked_at)).all()
        
        metrics['hourly_usage'] = {
            int(hour): count for hour, count in hourly_usage
        }
        
        # Course popularity
        course_attendance = self.db.query(
            Course.name,
            func.count(Attendance.id).label('attendance_count')
        ).join(AttendanceSession).join(Attendance).group_by(Course.name).all()
        
        metrics['course_popularity'] = [
            {'course': name, 'attendance_count': count}
            for name, count in course_attendance
        ]
        
        return metrics
    
    def _get_performance_metrics(self):
        """Calculate system performance metrics."""
        metrics = {}
        
        # Average session duration
        sessions_with_duration = self.db.query(AttendanceSession).filter(
            AttendanceSession.start_time.isnot(None),
            AttendanceSession.end_time.isnot(None)
        ).all()
        
        if sessions_with_duration:
            durations = [
                (session.end_time - session.start_time).total_seconds() / 3600
                for session in sessions_with_duration
            ]
            metrics['avg_session_duration_hours'] = sum(durations) / len(durations)
        else:
            metrics['avg_session_duration_hours'] = 0
        
        # Attendance per session
        attendance_per_session = self.db.query(
            AttendanceSession.id,
            func.count(Attendance.id).label('attendance_count')
        ).outerjoin(Attendance).group_by(AttendanceSession.id).all()
        
        if attendance_per_session:
            counts = [count for _, count in attendance_per_session]
            metrics['avg_attendance_per_session'] = sum(counts) / len(counts)
            metrics['max_attendance_per_session'] = max(counts)
        else:
            metrics['avg_attendance_per_session'] = 0
            metrics['max_attendance_per_session'] = 0
        
        return metrics
    
    def _get_security_metrics(self):
        """Calculate security-related metrics."""
        metrics = {}
        
        # Face verification attempts vs successes
        total_attempts = self.db.query(Attendance).count()
        successful_verifications = self.db.query(Attendance).filter(
            Attendance.verification_method == 'face_gps_verified'
        ).count()
        
        metrics['verification_success_rate'] = (
            successful_verifications / total_attempts * 100
        ) if total_attempts > 0 else 0
        
        # Location verification accuracy
        location_verified = self.db.query(Attendance).filter(
            Attendance.student_lat.isnot(None),
            Attendance.student_lng.isnot(None)
        ).count()
        
        metrics['location_verification_rate'] = (
            location_verified / total_attempts * 100
        ) if total_attempts > 0 else 0
        
        # Duplicate attendance attempts (security concern)
        duplicate_attempts = self.db.execute(text("""
            SELECT session_id, student_id, COUNT(*) as attempt_count
            FROM attendance
            GROUP BY session_id, student_id
            HAVING COUNT(*) > 1
        """)).fetchall()
        
        metrics['duplicate_attempts'] = len(duplicate_attempts)
        
        return metrics
    
    def generate_report(self):
        """Generate comprehensive evaluation report."""
        metrics = self.calculate_system_metrics()
        
        print("\n📊 ATTENDANCE SYSTEM EVALUATION REPORT")
        print("=" * 60)
        
        # System Overview
        print("\n🏢 SYSTEM OVERVIEW")
        print("-" * 30)
        stats = metrics['system_stats']
        print(f"Total Users: {stats['total_users']}")
        print(f"Students: {stats['total_students']}")
        print(f"Lecturers: {stats['total_lecturers']}")
        print(f"Courses: {stats['total_courses']}")
        print(f"Enrollments: {stats['total_enrollments']}")
        print(f"Sessions Created: {stats['total_sessions']}")
        print(f"Active Sessions: {stats['active_sessions']}")
        print(f"Attendance Records: {stats['total_attendance_records']}")
        
        # Face Recognition Performance
        print("\n👤 FACE RECOGNITION PERFORMANCE")
        print("-" * 30)
        face_metrics = metrics['face_recognition']
        print(f"Face Registration Rate: {face_metrics['face_registration_rate']:.1f}%")
        print(f"Basic Registrations: {face_metrics['basic_registrations']}")
        print(f"Advanced Registrations: {face_metrics['advanced_registrations']}")
        print(f"Unregistered Students: {face_metrics['unregistered_students']}")
        print(f"Face Verification Success: {face_metrics['face_verification_success_rate']:.1f}%")
        
        # Attendance Accuracy
        print("\n✅ ATTENDANCE ACCURACY")
        print("-" * 30)
        accuracy = metrics['attendance_accuracy']
        print(f"GPS Verification Rate: {accuracy['gps_verification_rate']:.1f}%")
        print("Verification Methods:")
        for method, count in accuracy['verification_methods'].items():
            print(f"  {method}: {count}")
        
        # Performance Metrics
        print("\n⚡ PERFORMANCE METRICS")
        print("-" * 30)
        perf = metrics['performance']
        print(f"Avg Session Duration: {perf['avg_session_duration_hours']:.1f} hours")
        print(f"Avg Attendance per Session: {perf['avg_attendance_per_session']:.1f}")
        print(f"Max Attendance per Session: {perf['max_attendance_per_session']}")
        
        # Security Metrics
        print("\n🔒 SECURITY METRICS")
        print("-" * 30)
        security = metrics['security']
        print(f"Overall Verification Success: {security['verification_success_rate']:.1f}%")
        print(f"Location Verification Rate: {security['location_verification_rate']:.1f}%")
        print(f"Duplicate Attempts Detected: {security['duplicate_attempts']}")
        
        # Usage Patterns
        print("\n📈 USAGE PATTERNS")
        print("-" * 30)
        usage = metrics['usage_patterns']
        
        if usage['course_popularity']:
            print("Most Popular Courses:")
            for course in sorted(usage['course_popularity'], 
                               key=lambda x: x['attendance_count'], reverse=True)[:5]:
                print(f"  {course['course']}: {course['attendance_count']} attendances")
        
        if usage['hourly_usage']:
            peak_hour = max(usage['hourly_usage'], key=usage['hourly_usage'].get)
            print(f"Peak Usage Hour: {peak_hour}:00 ({usage['hourly_usage'][peak_hour]} records)")
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS")
        print("-" * 30)
        self._generate_recommendations(metrics)
        
        # Save detailed report
        self._save_detailed_report(metrics)
        
        return metrics
    
    def _generate_recommendations(self, metrics):
        """Generate actionable recommendations based on metrics."""
        face_metrics = metrics['face_recognition']
        security = metrics['security']
        
        if face_metrics['face_registration_rate'] < 80:
            print("• Increase face registration rate - currently only {:.1f}%".format(
                face_metrics['face_registration_rate']))
        
        if face_metrics['advanced_registrations'] < face_metrics['basic_registrations']:
            print("• Encourage students to upgrade to advanced face recognition")
        
        if security['verification_success_rate'] < 90:
            print("• Improve verification success rate - currently {:.1f}%".format(
                security['verification_success_rate']))
        
        if security['duplicate_attempts'] > 0:
            print(f"• Investigate {security['duplicate_attempts']} duplicate attendance attempts")
        
        if metrics['system_stats']['active_sessions'] == 0:
            print("• No active sessions - encourage lecturers to create sessions")
    
    def _save_detailed_report(self, metrics):
        """Save detailed metrics to JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"evaluation_report_{timestamp}.json"
        
        # Convert datetime objects to strings for JSON serialization
        json_metrics = json.loads(json.dumps(metrics, default=str))
        
        with open(filename, 'w') as f:
            json.dump(json_metrics, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {filename}")
    
    def __del__(self):
        if hasattr(self, 'db'):
            self.db.close()


def main():
    """Run evaluation metrics."""
    try:
        evaluator = AttendanceSystemEvaluator()
        evaluator.generate_report()
    except Exception as e:
        print(f"Error running evaluation: {e}")


if __name__ == "__main__":
    main()