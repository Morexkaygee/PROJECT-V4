from sqlalchemy import Column, Integer, String, ForeignKey, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)

    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # 'student' or 'lecturer'
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    matric_no = Column(String(50), unique=True, nullable=False, index=True)
    facial_encoding = Column(Text)  # Legacy dlib encoding
    advanced_facial_encoding = Column(Text)  # JSON with multiple model embeddings
    face_registered = Column(Boolean, default=False)
    face_registration_method = Column(String(50), default="basic")  # "basic" or "advanced"
    department = Column(String(255))
    level = Column(String(10))
    user = relationship("User", backref="student_profile")
    courses = relationship("Course", secondary="course_students", back_populates="students")


class Lecturer(Base):
    __tablename__ = "lecturers"

    id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    staff_id = Column(String(50), unique=True, nullable=True)
    department = Column(String(255))
    title = Column(String(50))  # Dr., Prof., Mr., Mrs., etc.
    user = relationship("User", backref="lecturer_profile")
    courses = relationship("Course", back_populates="lecturer")