@echo off
echo Starting Attendance System for Mobile Access...
echo.

REM Get IP address
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
    set IP=%%a
    goto :found
)
:found
set IP=%IP: =%

echo Your IP Address: %IP%
echo.
echo Access from your phone:
echo Frontend: http://%IP%:3000
echo API: http://%IP%:8000
echo.
echo IMPORTANT: Make sure both devices are on the same WiFi network!
echo.

REM Start backend in new window
start "Backend Server" cmd /k "cd /d backend && python start.py"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend
cd frontend
echo Starting frontend server...
npm run dev -- --host 0.0.0.0

pause