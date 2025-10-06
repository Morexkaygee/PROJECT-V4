from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import hashlib
from datetime import datetime
import json

app = FastAPI(title="Attendance System", version="1.0.0")

# CORS - Secure configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ],  # Specific origins only
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Accept",
        "Accept-Language", 
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "Origin"
    ],
)

# Simple database setup
def init_db():
    conn = sqlite3.connect('simple_attendance.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            matric_no TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            lecturer_id INTEGER,
            location_lat REAL,
            location_lng REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (lecturer_id) REFERENCES users (id)
        )
    ''')
    
    # Attendance table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            student_id INTEGER,
            marked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions (id),
            FOREIGN KEY (student_id) REFERENCES users (id)
        )
    ''')
    
    # Create default users if they don't exist
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        # Default lecturer
        cursor.execute('''
            INSERT INTO users (name, password, role) 
            VALUES (?, ?, ?)
        ''', ("Dr. Sample Lecturer", hashlib.md5("lecturer123".encode()).hexdigest(), "lecturer"))
        
        # Default student
        cursor.execute('''
            INSERT INTO users (name, password, role, matric_no) 
            VALUES (?, ?, ?, ?)
        ''', ("Sample Student", hashlib.md5("student123".encode()).hexdigest(), "student", "CSC/2020/001"))
    
    conn.commit()
    conn.close()

# Models
class LoginRequest(BaseModel):
    username: str
    password: str

class SessionCreate(BaseModel):
    title: str
    location_lat: float
    location_lng: float

# Initialize database
init_db()

@app.get("/")
def root():
    return {"message": "Attendance System API", "status": "running"}

@app.post("/auth/login")
def login(request: LoginRequest):
    conn = sqlite3.connect('simple_attendance.db')
    cursor = conn.cursor()
    
    password_hash = hashlib.md5(request.password.encode()).hexdigest()
    
    cursor.execute('''
        SELECT id, name, role, matric_no FROM users 
        WHERE (name = ? OR matric_no = ?) AND password = ?
    ''', (request.username, request.username, password_hash))
    
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {
        "access_token": f"token_{user[0]}",
        "user": {
            "id": user[0],
            "name": user[1],
            "role": user[2],
            "matric_no": user[3]
        }
    }

@app.get("/auth/profile")
def get_profile():
    # Simple mock profile for testing
    return {
        "id": 1,
        "name": "Sample Student",
        "role": "student",
        "matric_no": "CSC/2020/001"
    }

@app.post("/attendance/sessions")
def create_session(session: SessionCreate):
    conn = sqlite3.connect('simple_attendance.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO sessions (title, lecturer_id, location_lat, location_lng)
        VALUES (?, ?, ?, ?)
    ''', (session.title, 1, session.location_lat, session.location_lng))
    
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return {"id": session_id, "message": "Session created successfully"}

@app.get("/attendance/sessions")
def get_sessions():
    conn = sqlite3.connect('simple_attendance.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT s.id, s.title, s.location_lat, s.location_lng, s.created_at,
               u.name as lecturer_name
        FROM sessions s
        LEFT JOIN users u ON s.lecturer_id = u.id
        ORDER BY s.created_at DESC
    ''')
    
    sessions = []
    for row in cursor.fetchall():
        sessions.append({
            "id": row[0],
            "title": row[1],
            "location": {"lat": row[2], "lng": row[3]},
            "created_at": row[4],
            "lecturer_name": row[5]
        })
    
    conn.close()
    return sessions

@app.post("/attendance/mark")
def mark_attendance():
    # Simple mock attendance marking
    return {"message": "Attendance marked successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)