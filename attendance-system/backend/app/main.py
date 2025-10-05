from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, attendance, courses, students, face_registration
from app.core.config import settings

app = FastAPI(
    title="Attendance Management System",
    description="Face Recognition + GPS based Attendance System for Federal University of Technology, Akure",
    version="2.0.0"
)

# Configure CORS for ngrok and local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (ngrok URLs are dynamic)
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

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