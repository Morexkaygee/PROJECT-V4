from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(20), unique=True, nullable=False, index=True)
    lecturer_id = Column(Integer, ForeignKey("lecturers.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    lecturer = relationship("Lecturer", back_populates="courses")
    students = relationship("Student", secondary="course_students", back_populates="courses")


class CourseStudent(Base):
    __tablename__ = "course_students"

    course_id = Column(Integer, ForeignKey("courses.id"), primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), primary_key=True)


class CoursePermission(Base):
    __tablename__ = "course_permissions"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    lecturer_id = Column(Integer, ForeignKey("lecturers.id"), nullable=False)
    granted_at = Column(DateTime, default=datetime.utcnow)
    
    course = relationship("Course")
    lecturer = relationship("Lecturer")