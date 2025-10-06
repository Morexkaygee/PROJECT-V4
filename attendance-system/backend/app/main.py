from fastapi import FastAPI
from app.api import auth, attendance, courses, students, face_registration
from app.core.config import settings
from app.core.cors import configure_cors

app = FastAPI(
    title="Attendance Management System",
    description="Face Recognition + GPS based Attendance System for Federal University of Technology, Akure",
    version="2.0.0"
)

# Configure CORS using centralized configuration
configure_cors(app)

# Include routers
app.include_router(auth.router)
app.include_router(attendance.router)
app.include_router(courses.router)
app.include_router(students.router)
app.include_router(face_registration.router)


@app.get("/")
def root():
    return {"message": "Attendance Management System API", "version": "2.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}