#!/usr/bin/env python3
import subprocess
import sys
import os
from pathlib import Path


def create_self_signed_cert():
    """Create self-signed certificate for HTTPS."""
    cert_dir = Path("certs")
    cert_dir.mkdir(exist_ok=True)
    
    cert_file = cert_dir / "cert.pem"
    key_file = cert_dir / "key.pem"
    
    if cert_file.exists() and key_file.exists():
        return str(cert_file), str(key_file)
    
    try:
        # Create self-signed certificate
        subprocess.run([
            "openssl", "req", "-x509", "-newkey", "rsa:4096",
            "-keyout", str(key_file), "-out", str(cert_file),
            "-days", "365", "-nodes", "-subj", "/CN=localhost"
        ], check=True, capture_output=True)
        return str(cert_file), str(key_file)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("OpenSSL not found. Install OpenSSL or use HTTP mode.")
        return None, None


def start_server():
    """Start the FastAPI server with proper error handling."""
    try:
        # Check if uvicorn is available
        result = subprocess.run(
            [sys.executable, "-c", "import uvicorn"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print("Error: uvicorn not found. Please install requirements:")
            print("pip install -r requirements.txt")
            sys.exit(1)
        
        # Try to create HTTPS certificates
        cert_file, key_file = create_self_signed_cert()
        
        # Start the server
        print("Starting Attendance Management System API...")
        
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--reload",
            "--host", "0.0.0.0",
            "--port", "8000"
        ]
        
        if cert_file and key_file:
            cmd.extend(["--ssl-certfile", cert_file, "--ssl-keyfile", key_file])
            print("HTTPS enabled - Camera access will work on mobile!")
            print("Access via: https://YOUR_IP:8000")
        else:
            print("Running HTTP mode - Camera may not work on mobile browsers")
            print("Access via: http://YOUR_IP:8000")
        
        subprocess.run(cmd, check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"Error starting server: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    start_server()