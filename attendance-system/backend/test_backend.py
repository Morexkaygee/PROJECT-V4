#!/usr/bin/env python3
"""
Test script to check if backend is working
"""
import requests
import sys

def test_backend():
    """Test if backend is responding"""
    try:
        # Test basic health endpoint
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running and healthy!")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Backend responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend - server is not running")
        print("Start the backend with: python -m uvicorn app.main:app --reload")
        return False
    except requests.exceptions.Timeout:
        print("❌ Backend request timed out")
        return False
    except Exception as e:
        print(f"❌ Error testing backend: {e}")
        return False

def test_api_docs():
    """Test if API docs are accessible"""
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code == 200:
            print("✅ API docs are accessible at http://localhost:8000/docs")
            return True
        else:
            print(f"❌ API docs responded with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot access API docs: {e}")
        return False

if __name__ == "__main__":
    print("Testing Backend Server...")
    print("=" * 40)
    
    backend_ok = test_backend()
    if backend_ok:
        test_api_docs()
        print("\n✅ Backend is working correctly!")
        print("You can now use the frontend at http://localhost:3001")
    else:
        print("\n❌ Backend is not working!")
        print("Please start the backend server first:")
        print("1. cd attendance-system/backend")
        print("2. python -m uvicorn app.main:app --reload")