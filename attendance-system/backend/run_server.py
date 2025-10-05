#!/usr/bin/env python3
"""
Simple server startup script
"""
import uvicorn
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.dirname(__file__))

if __name__ == "__main__":
    print("Starting Attendance Management System API...")
    print("Access at: http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    print("Press Ctrl+C to stop")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )