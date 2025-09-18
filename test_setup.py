#!/usr/bin/env python3
"""
Test setup script to verify all components are working
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and return success status"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            return True
        else:
            print(f"❌ {description} - Failed")
            print(f"   Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - Exception: {e}")
        return False

def check_file_exists(file_path, description):
    """Check if a file exists"""
    if Path(file_path).exists():
        print(f"✅ {description} - Found")
        return True
    else:
        print(f"❌ {description} - Not found")
        return False

def main():
    """Main test function"""
    print("🚀 Testing Salesforce Quiz API Setup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("app").exists():
        print("❌ Not in the correct directory. Please run from project root.")
        return False
    
    # Check essential files
    essential_files = [
        ("app/main.py", "Main application file"),
        ("app/routers/auth.py", "Authentication router"),
        ("app/routers/quiz.py", "Quiz router"),
        ("app/models/database.py", "Database models"),
        ("app/models/schemas.py", "Pydantic schemas"),
        ("app/services/quiz_service.py", "Quiz service"),
        ("app/core/config.py", "Configuration"),
        ("app/core/security.py", "Security utilities"),
        ("requirements.txt", "Dependencies"),
        ("env.example", "Environment example"),
        (".gitignore", "Git ignore file"),
        ("alembic.ini", "Alembic configuration"),
        ("migrate.py", "Migration script"),
        ("pytest.ini", "Pytest configuration"),
        ("tests/conftest.py", "Test configuration"),
        ("tests/test_auth.py", "Authentication tests"),
        ("tests/test_quiz.py", "Quiz tests"),
        ("tests/test_services.py", "Service tests")
    ]
    
    print("📁 Checking essential files...")
    all_files_exist = True
    for file_path, description in essential_files:
        if not check_file_exists(file_path, description):
            all_files_exist = False
    
    if not all_files_exist:
        print("❌ Some essential files are missing!")
        return False
    
    # Test Python imports
    print("\n🐍 Testing Python imports...")
    try:
        sys.path.append(os.getcwd())
        from app.main import app
        from app.routers import auth, quiz
        from app.models.database import Base
        from app.models.schemas import User, QuizSet, Question
        from app.services.quiz_service import QuizService
        from app.core.config import settings
        from app.core.security import get_password_hash
        print("✅ All imports successful")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Test database migration
    print("\n🗄️ Testing database migration...")
    if run_command("python3 migrate.py", "Database migration"):
        print("✅ Database setup successful")
    else:
        print("❌ Database setup failed")
        return False
    
    # Test running the application
    print("\n🌐 Testing application startup...")
    try:
        from fastapi.testclient import TestClient
        client = TestClient(app)
        response = client.get("/")
        if response.status_code == 200:
            print("✅ Application starts successfully")
        else:
            print(f"❌ Application startup failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Application startup error: {e}")
        return False
    
    # Test authentication endpoints
    print("\n🔐 Testing authentication endpoints...")
    try:
        # Test register endpoint
        response = client.post(
            "/api/v1/register",
            json={
                "name": "Test User",
                "email": "test@example.com",
                "password": "testpassword",
                "role": "user"
            }
        )
        if response.status_code == 201:
            print("✅ User registration endpoint working")
        else:
            print(f"❌ User registration failed: {response.status_code}")
            return False
        
        # Test login endpoint
        response = client.post(
            "/api/v1/login",
            data={
                "username": "test@example.com",
                "password": "testpassword"
            }
        )
        if response.status_code == 200:
            print("✅ User login endpoint working")
        else:
            print(f"❌ User login failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Authentication test error: {e}")
        return False
    
    # Test quiz endpoints
    print("\n📝 Testing quiz endpoints...")
    try:
        # Get auth token
        response = client.post(
            "/api/v1/login",
            data={
                "username": "test@example.com",
                "password": "testpassword"
            }
        )
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test quiz sets endpoint
        response = client.get("/api/v1/quiz-sets")
        if response.status_code == 200:
            print("✅ Quiz sets endpoint working")
        else:
            print(f"❌ Quiz sets endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Quiz endpoint test error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! The API is ready to use.")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔴 ReDoc: http://localhost:8000/redoc")
    print("🏃‍♂️ To start the server: uvicorn app.main:app --reload")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
