@echo off
echo Starting Attendance Management System...
echo.

REM Start Backend
echo Starting Backend Server...
cd "attendance-system\backend"
start "Backend Server" cmd /k "python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

REM Wait for backend to start
timeout /t 5 /nobreak > nul

REM Start Frontend
echo Starting Frontend...
cd "..\frontend"
start "Frontend Server" cmd /k "npm run dev"

echo.
echo Servers are starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3001
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to close this window...
pause > nul