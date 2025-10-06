#!/usr/bin/env python3
"""
Quick server status checker
"""

import requests
import sys

def check_server():
    """Check if the backend server is running"""
    try:
        print("Checking backend server at http://localhost:8000...")
        
        # Test health endpoint
        response = requests.get("http://localhost:8000/health", timeout=5)
        
        if response.status_code == 200:
            print("[OK] Backend server is running!")
            print(f"Response: {response.json()}")
            
            # Test API root
            root_response = requests.get("http://localhost:8000/", timeout=5)
            if root_response.status_code == 200:
                print("[OK] API root endpoint working!")
                print(f"API Info: {root_response.json()}")
            
            return True
        else:
            print(f"[ERROR] Server responded with status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("[ERROR] Cannot connect to backend server!")
        print("The server is not running or not accessible at http://localhost:8000")
        print("\nTo start the server:")
        print("1. Open a terminal/command prompt")
        print("2. Navigate to the backend directory:")
        print("   cd backend")
        print("3. Run the server:")
        print("   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        return False
        
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False

if __name__ == "__main__":
    if check_server():
        print("\n[SUCCESS] Server is working correctly!")
        sys.exit(0)
    else:
        print("\n[FAILED] Server is not working!")
        sys.exit(1)