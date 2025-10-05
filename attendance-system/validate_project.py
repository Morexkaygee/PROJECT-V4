#!/usr/bin/env python3
"""
Project Validation Script
Checks if all files are properly connected and configured
"""
import os
import sys
import json
from pathlib import Path

def check_backend_structure():
    """Check backend file structure and imports."""
    print("Checking Backend Structure...")
    
    backend_path = Path("backend")
    required_files = [
        "app/main.py",
        "app/core/config.py",
        "app/core/database.py", 
        "app/core/security.py",
        "app/models/__init__.py",
        "app/models/user.py",
        "app/models/course.py",
        "app/models/attendance.py",
        "app/api/auth.py",
        "app/api/attendance.py",
        "app/services/auth_service.py",
        "app/services/attendance_service.py",
        "app/utils/face_recognition.py",
        "app/utils/gps_verification.py",
        "requirements.txt",
        ".env",
        "init_db.py",
        "start.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = backend_path / file_path
        if not full_path.exists():
            missing_files.append(str(full_path))
    
    if missing_files:
        print("Missing backend files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    else:
        print("All backend files present")
        return True

def check_frontend_structure():
    """Check frontend file structure."""
    print("Checking Frontend Structure...")
    
    frontend_path = Path("frontend")
    required_files = [
        "package.json",
        "next.config.js",
        "tsconfig.json",
        "tailwind.config.js",
        "src/pages/index.tsx",
        "src/pages/login.tsx",
        "src/pages/_app.tsx",
        "src/utils/api.ts",
        "src/utils/geolocation.ts",
        "src/components/AttendanceCamera.tsx"
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = frontend_path / file_path
        if not full_path.exists():
            missing_files.append(str(full_path))
    
    if missing_files:
        print("Missing frontend files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    else:
        print("All frontend files present")
        return True

def check_environment_config():
    """Check environment configuration."""
    print("Checking Environment Configuration...")
    
    env_file = Path("backend/.env")
    if not env_file.exists():
        print("Backend .env file missing")
        return False
    
    try:
        with open(env_file, 'r') as f:
            env_content = f.read()
        
        required_vars = [
            "DATABASE_URL",
            "SECRET_KEY", 
            "ALGORITHM",
            "ACCESS_TOKEN_EXPIRE_MINUTES",
            "FACE_RECOGNITION_TOLERANCE",
            "GPS_TOLERANCE_METERS",
            "ALLOWED_LOCATIONS"
        ]
        
        missing_vars = []
        for var in required_vars:
            if var not in env_content:
                missing_vars.append(var)
        
        if missing_vars:
            print("Missing environment variables:")
            for var in missing_vars:
                print(f"   - {var}")
            return False
        else:
            print("All environment variables present")
            return True
            
    except Exception as e:
        print(f"Error reading .env file: {e}")
        return False

def check_package_dependencies():
    """Check if package dependencies are properly defined."""
    print("Checking Package Dependencies...")
    
    # Check backend requirements
    backend_req = Path("backend/requirements.txt")
    if backend_req.exists():
        with open(backend_req, 'r') as f:
            backend_deps = f.read()
        
        required_backend_deps = [
            "fastapi", "uvicorn", "sqlalchemy", "alembic",
            "python-jose", "passlib", "face-recognition",
            "geopy", "python-dotenv", "pydantic"
        ]
        
        missing_backend = []
        for dep in required_backend_deps:
            if dep not in backend_deps.lower():
                missing_backend.append(dep)
        
        if missing_backend:
            print("Missing backend dependencies:")
            for dep in missing_backend:
                print(f"   - {dep}")
        else:
            print("Backend dependencies complete")
    
    # Check frontend package.json
    frontend_pkg = Path("frontend/package.json")
    if frontend_pkg.exists():
        try:
            with open(frontend_pkg, 'r') as f:
                pkg_data = json.load(f)
            
            deps = {**pkg_data.get('dependencies', {}), **pkg_data.get('devDependencies', {})}
            
            required_frontend_deps = [
                "next", "react", "react-dom", "typescript",
                "tailwindcss", "axios", "react-webcam"
            ]
            
            missing_frontend = []
            for dep in required_frontend_deps:
                if dep not in deps:
                    missing_frontend.append(dep)
            
            if missing_frontend:
                print("Missing frontend dependencies:")
                for dep in missing_frontend:
                    print(f"   - {dep}")
            else:
                print("Frontend dependencies complete")
                
        except json.JSONDecodeError:
            print("Invalid package.json format")
    
    return True

def check_api_connections():
    """Check if API endpoints are properly connected."""
    print("Checking API Connections...")
    
    # Check if frontend API client matches backend routes
    api_file = Path("frontend/src/utils/api.ts")
    if api_file.exists():
        with open(api_file, 'r') as f:
            api_content = f.read()
        
        # Check for required API endpoints
        required_endpoints = [
            "/auth/login",
            "/auth/register/student", 
            "/auth/profile",
            "/attendance/sessions",
            "/attendance/mark"
        ]
        
        missing_endpoints = []
        for endpoint in required_endpoints:
            if endpoint not in api_content:
                missing_endpoints.append(endpoint)
        
        if missing_endpoints:
            print("Missing API endpoints in frontend:")
            for endpoint in missing_endpoints:
                print(f"   - {endpoint}")
        else:
            print("API endpoints properly connected")
    
    return True

def main():
    """Run all validation checks."""
    print("Starting Project Validation...\n")
    
    checks = [
        check_backend_structure,
        check_frontend_structure,
        check_environment_config,
        check_package_dependencies,
        check_api_connections
    ]
    
    all_passed = True
    for check in checks:
        try:
            result = check()
            if not result:
                all_passed = False
        except Exception as e:
            print(f"Error in {check.__name__}: {e}")
            all_passed = False
        print()
    
    if all_passed:
        print("All validation checks passed!")
        print("\nNext Steps:")
        print("1. cd backend && python init_db.py")
        print("2. cd frontend && npm install")
        print("3. Run: python run.bat (or use individual start commands)")
        print("4. Access: http://localhost:3000")
    else:
        print("Some validation checks failed. Please fix the issues above.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)