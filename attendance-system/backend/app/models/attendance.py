from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class AttendanceSession(Base):
    __tablename__ = "attendance_sessions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    location_lat = Column(Float)
    location_lng = Column(Float)
    location_radius = Column(Float, default=100.0)
    
    course = relationship("Course")
    attendances = relationship("Attendance", back_populates="session")


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("attendance_sessions.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    marked_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    present = Column(Boolean, default=True, nullable=False)
    verification_method = Column(String(50), nullable=False)  # 'face_gps', 'manual'
    student_lat = Column(Float)
    student_lng = Column(Float)
    
    # Performance Metrics
    face_confidence_score = Column(Float)  # Face recognition confidence
    gps_accuracy_meters = Column(Float)    # GPS accuracy (CEP)
    processing_time_ms = Column(Integer)   # End-to-end latency in milliseconds
    verification_status = Column(String(20))  # 'accepted', 'rejected_face', 'rejected_gps'
    
    session = relationship("AttendanceSession", back_populates="attendances")
    student = relationship("Student")