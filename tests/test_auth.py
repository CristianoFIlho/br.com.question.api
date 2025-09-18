"""
Tests for authentication endpoints
"""

import pytest
from fastapi.testclient import TestClient


class TestAuth:
    """Test authentication endpoints"""
    
    def test_register_user_success(self, client):
        """Test successful user registration"""
        response = client.post(
            "/api/v1/register",
            json={
                "name": "John Doe",
                "email": "john@example.com",
                "password": "password123",
                "role": "user"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "John Doe"
        assert data["email"] == "john@example.com"
        assert data["role"] == "user"
        assert "id" in data
        assert "created_at" in data
        assert "password" not in data  # Password should not be returned
    
    def test_register_user_duplicate_email(self, client, test_user):
        """Test registration with duplicate email"""
        response = client.post(
            "/api/v1/register",
            json={
                "name": "Another User",
                "email": test_user.email,  # Same email as test_user
                "password": "password123",
                "role": "user"
            }
        )
        
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]
    
    def test_login_success(self, client, test_user):
        """Test successful login"""
        response = client.post(
            "/api/v1/login",
            data={
                "username": test_user.email,
                "password": "testpassword"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        response = client.post(
            "/api/v1/login",
            data={
                "username": "nonexistent@example.com",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]
    
    def test_get_current_user(self, client, auth_headers, test_user):
        """Test getting current user information"""
        response = client.get(
            "/api/v1/me",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["name"] == test_user.name
        assert data["email"] == test_user.email
        assert data["role"] == test_user.role
    
    def test_get_current_user_unauthorized(self, client):
        """Test getting current user without authentication"""
        response = client.get("/api/v1/me")
        
        assert response.status_code == 401
    
    def test_update_current_user(self, client, auth_headers, test_user):
        """Test updating current user information"""
        response = client.put(
            "/api/v1/me",
            headers=auth_headers,
            json={
                "name": "Updated Name",
                "email": "updated@example.com"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["email"] == "updated@example.com"
        assert data["id"] == test_user.id
    
    def test_update_current_user_password(self, client, auth_headers, test_user):
        """Test updating current user password"""
        response = client.put(
            "/api/v1/me",
            headers=auth_headers,
            json={
                "password": "newpassword123"
            }
        )
        
        assert response.status_code == 200
        
        # Test login with new password
        login_response = client.post(
            "/api/v1/login",
            data={
                "username": test_user.email,
                "password": "newpassword123"
            }
        )
        
        assert login_response.status_code == 200
        assert "access_token" in login_response.json()
    
    def test_refresh_token(self, client, auth_headers):
        """Test token refresh"""
        response = client.post(
            "/api/v1/refresh",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0
