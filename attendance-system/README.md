# Attendance Management System

A modern attendance management system using **Face Recognition + GPS Verification** for secure and accurate attendance tracking.

## Features

- **Dual Verification**: Face recognition + GPS location verification
- **Role-based Access**: Admin, Lecturer, and Student interfaces
- **Real-time Attendance**: Live attendance marking during sessions
- **Secure Authentication**: JWT-based authentication with proper security
- **Location Tracking**: GPS-based session location verification
- **Modern UI**: Clean, responsive interface built with Next.js and Tailwind CSS

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **PostgreSQL**: Robust database with proper relationships
- **SQLAlchemy**: ORM with Alembic migrations
- **Face Recognition**: Python face_recognition library
- **GPS Verification**: Geopy for location calculations
- **JWT Authentication**: Secure token-based auth

### Frontend
- **Next.js 15**: React framework with TypeScript
- **Tailwind CSS**: Utility-first CSS framework
- **React Hook Form**: Form handling with validation
- **Axios**: HTTP client with interceptors
- **React Webcam**: Camera integration for face capture

## Setup Instructions

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd attendance-system/backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup environment variables**:
   ```bash
   copy .env.example .env
   # Edit .env with your database URL and secret key
   ```

5. **Run database migrations**:
   ```bash
   alembic upgrade head
   ```

6. **Start the server**:
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd attendance-system/frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start development server**:
   ```bash
   npm run dev
   ```

## Security Features

- ✅ **No hardcoded credentials**
- ✅ **Updated dependencies** (no vulnerabilities)
- ✅ **Proper error handling** throughout
- ✅ **Input validation** and sanitization
- ✅ **CORS configuration** with specific origins
- ✅ **JWT token security** with proper expiration
- ✅ **SQL injection prevention** with parameterized queries
- ✅ **Role-based access control**

## API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register/student` - Student registration
- `GET /auth/profile` - Get user profile

### Attendance
- `POST /attendance/sessions` - Create attendance session (Lecturer)
- `POST /attendance/mark` - Mark attendance with face+GPS (Student)
- `GET /attendance/sessions/{id}/attendance` - Get session attendance (Lecturer)

## Usage Flow

1. **Lecturer** creates an attendance session with location coordinates
2. **Student** opens the attendance marking interface
3. System captures student's face via webcam
4. System gets student's GPS location
5. Both face recognition and GPS location are verified
6. Attendance is marked only if both verifications pass

## Project Structure

```
attendance-system/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Configuration & security
│   │   ├── models/       # Database models
│   │   ├── services/     # Business logic
│   │   └── utils/        # Utilities (face recognition, GPS)
│   ├── alembic/          # Database migrations
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── components/   # React components
    │   ├── pages/        # Next.js pages
    │   ├── utils/        # API client & utilities
    │   └── types/        # TypeScript types
    └── package.json
```

## License

This project is developed as a final year project for the Department of Electrical and Electronics Engineering, Federal University of Technology, Akure.