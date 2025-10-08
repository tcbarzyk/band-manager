"""
Authentication tests for the Band Manager API.

These tests verify that the authentication system works correctly,
including JWT token validation, user dependency injection, and
access control for protected endpoints.
"""

import pytest
import os
from fastapi.testclient import TestClient
from fastapi import HTTPException
from unittest.mock import patch, Mock
import jwt
from datetime import datetime, timezone
import uuid

# Load environment variables from .env file for testing
from dotenv import load_dotenv
load_dotenv()

from auth import SupabaseAuth, get_current_user, get_current_user_optional
from fastapi.security import HTTPAuthorizationCredentials

# Get the actual JWT secret from environment for testing
ACTUAL_JWT_SECRET = os.getenv('SUPABASE_JWT_SECRET')

class TestSupabaseAuth:
    """Test the SupabaseAuth class"""
    
    def test_supabase_auth_initialization(self):
        """Test SupabaseAuth initializes correctly with environment variables"""
        # Since we load from .env, test with actual environment
        auth = SupabaseAuth()
        assert auth.jwt_secret is not None
        assert len(auth.jwt_secret) > 0
    
    @patch('auth.SUPABASE_URL', None)
    @patch('auth.SUPABASE_ANON_KEY', None)
    def test_supabase_auth_missing_env_vars(self):
        """Test SupabaseAuth fails with missing environment variables"""
        with pytest.raises(ValueError, match="SUPABASE_URL and SUPABASE_ANON_KEY must be set"):
            SupabaseAuth()
    
    def test_verify_jwt_token_valid(self):
        """Test JWT token verification with valid token"""
        auth = SupabaseAuth()
        
        # Create a valid test token using the actual JWT secret
        payload = {
            "sub": "12345678-1234-5678-1234-567812345678",
            "email": "test@example.com", 
            "role": "authenticated",
            "aud": "authenticated",
            "exp": 9999999999,  # Far future
            "iat": 1000000000
        }
        
        token = jwt.encode(payload, ACTUAL_JWT_SECRET, algorithm='HS256')
        
        result = auth.verify_jwt_token(token)
        assert result["sub"] == payload["sub"]
        assert result["email"] == payload["email"]
    
    def test_verify_jwt_token_expired(self):
        """Test JWT token verification with expired token"""
        auth = SupabaseAuth()
        
        # Create an expired token using the actual JWT secret
        payload = {
            "sub": "12345678-1234-5678-1234-567812345678",
            "email": "test@example.com",
            "exp": 1000000000,  # Past date
            "aud": "authenticated"
        }
        
        token = jwt.encode(payload, ACTUAL_JWT_SECRET, algorithm='HS256')
        
        with pytest.raises(HTTPException) as exc_info:
            auth.verify_jwt_token(token)
        
        assert exc_info.value.status_code == 401
        assert "expired" in exc_info.value.detail.lower()
    
    def test_verify_jwt_token_invalid(self):
        """Test JWT token verification with invalid token"""
        with patch.dict('os.environ', {
            'SUPABASE_URL': 'https://test.supabase.co',
            'SUPABASE_ANON_KEY': 'test-anon-key',
            'SUPABASE_JWT_SECRET': 'test-secret-key-that-is-long-enough-for-hs256'
        }):
            auth = SupabaseAuth()
            
            with pytest.raises(HTTPException) as exc_info:
                auth.verify_jwt_token("invalid-token")
            
            assert exc_info.value.status_code == 401
            assert "Invalid token" in exc_info.value.detail
    
    def test_get_user_from_token(self):
        """Test extracting user info from valid token"""
        auth = SupabaseAuth()
        
        payload = {
            "sub": "12345678-1234-5678-1234-567812345678",
            "email": "test@example.com",
            "role": "authenticated",
            "aud": "authenticated",
            "exp": 9999999999,
            "iat": 1000000000
        }
        
        token = jwt.encode(payload, ACTUAL_JWT_SECRET, algorithm='HS256')
        
        user_info = auth.get_user_from_token(token)
        assert user_info["user_id"] == payload["sub"]
        assert user_info["email"] == payload["email"]
        assert user_info["role"] == payload["role"]
    
    def test_get_user_from_token_missing_user_id(self):
        """Test extracting user info from token missing user_id"""
        auth = SupabaseAuth()
        
        payload = {
            # Missing "sub" field
            "email": "test@example.com",
            "role": "authenticated",
            "aud": "authenticated",
            "exp": 9999999999,
            "iat": 1000000000
        }
        
        token = jwt.encode(payload, ACTUAL_JWT_SECRET, algorithm='HS256')
        
        with pytest.raises(HTTPException) as exc_info:
            auth.get_user_from_token(token)
        
        assert exc_info.value.status_code == 401
        assert "missing user ID" in exc_info.value.detail


class TestAuthenticationEndpoints:
    """Test authentication-related API endpoints"""
    
    def test_get_current_user_profile_authenticated(self, authenticated_client_user_1, mock_user_1):
        """Test GET /auth/me with authenticated user"""
        response = authenticated_client_user_1.get("/auth/me")
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == mock_user_1["email"]
        assert "user_id" in data
        assert "display_name" in data
    
    def test_get_current_user_profile_unauthenticated(self, unauthenticated_client):
        """Test GET /auth/me without authentication"""
        response = unauthenticated_client.get("/auth/me")
        assert response.status_code == 403
    
    def test_update_current_user_profile(self, authenticated_client_user_1, mock_user_1):
        """Test PUT /auth/me to update profile"""
        # First create a profile
        profile_data = {
            "display_name": "Original Name",
            "email": mock_user_1["email"]
        }
        create_response = authenticated_client_user_1.post("/profiles", json=profile_data)
        assert create_response.status_code == 201
        
        # Then update it
        update_data = {"display_name": "Updated Name"}
        response = authenticated_client_user_1.put("/auth/me", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["display_name"] == "Updated Name"
    
    def test_update_current_user_profile_unauthenticated(self, unauthenticated_client):
        """Test PUT /auth/me without authentication"""
        update_data = {"display_name": "Updated Name"}
        
        response = unauthenticated_client.put("/auth/me", json=update_data)
        assert response.status_code == 403


class TestAccessControl:
    """Test access control for protected endpoints"""
    
    def test_protected_endpoint_without_auth(self, unauthenticated_client):
        """Test that protected endpoints reject unauthenticated requests"""
        
        # Test various protected endpoints
        protected_endpoints = [
            ("GET", "/my/bands"),
            ("POST", "/bands"),
            ("POST", "/profiles"),
        ]
        
        for method, endpoint in protected_endpoints:
            if method == "GET":
                response = unauthenticated_client.get(endpoint)
            elif method == "POST":
                response = unauthenticated_client.post(endpoint, json={})
            
            assert response.status_code == 403, f"Endpoint {method} {endpoint} should require authentication"
    
    def test_band_member_access_control(self, authenticated_client_user_1, authenticated_client_user_2):
        """Test that users can only access bands they're members of"""
        
        # User 1 creates a band
        band_data = {"name": "Test Band", "timezone": "America/New_York"}
        response = authenticated_client_user_1.post("/bands", json=band_data)
        assert response.status_code == 201
        band = response.json()
        band_id = band["id"]
        
        # User 1 can access the band
        response = authenticated_client_user_1.get(f"/bands/{band_id}")
        assert response.status_code == 200
        
        # User 2 cannot access the band (not a member)
        response = authenticated_client_user_2.get(f"/bands/{band_id}")
        assert response.status_code == 403
    
    def test_venue_access_control(self, authenticated_client_user_1, authenticated_client_user_2):
        """Test that users can only access venues in bands they're members of"""
        
        # User 1 creates a band
        band_data = {"name": "Test Band", "timezone": "America/New_York"}
        response = authenticated_client_user_1.post("/bands", json=band_data)
        band = response.json()
        band_id = band["id"]
        
        # User 1 creates a venue
        venue_data = {"name": "Test Venue", "address": "123 Test St"}
        response = authenticated_client_user_1.post(f"/bands/{band_id}/venues", json=venue_data)
        assert response.status_code == 201
        venue = response.json()
        venue_id = venue["id"]
        
        # User 1 can access the venue
        response = authenticated_client_user_1.get(f"/venues/{venue_id}")
        assert response.status_code == 200
        
        # User 2 cannot access the venue
        response = authenticated_client_user_2.get(f"/venues/{venue_id}")
        assert response.status_code == 403
    
    def test_event_access_control(self, authenticated_client_user_1, authenticated_client_user_2):
        """Test that users can only access events in bands they're members of"""
        from datetime import datetime, timezone
        
        # User 1 creates a band
        band_data = {"name": "Test Band", "timezone": "America/New_York"}
        response = authenticated_client_user_1.post("/bands", json=band_data)
        band = response.json()
        band_id = band["id"]
        
        # User 1 creates an event
        event_data = {
            "title": "Test Event",
            "type": "REHEARSAL",
            "starts_at_utc": "2025-10-15T19:00:00Z",
            "ends_at_utc": "2025-10-15T21:00:00Z"
        }
        response = authenticated_client_user_1.post(f"/bands/{band_id}/events", json=event_data)
        assert response.status_code == 201
        event = response.json()
        event_id = event["id"]
        
        # User 1 can access the event
        response = authenticated_client_user_1.get(f"/events/{event_id}")
        assert response.status_code == 200
        
        # User 2 cannot access the event
        response = authenticated_client_user_2.get(f"/events/{event_id}")
        assert response.status_code == 403


class TestProfileCreationWithAuth:
    """Test profile creation with authentication"""
    
    def test_create_profile_with_matching_email(self, authenticated_client_user_1, mock_user_1):
        """Test creating profile with email matching authenticated user"""
        profile_data = {
            "display_name": "Test User",
            "email": mock_user_1["email"]  # Must match authenticated user's email
        }
        
        response = authenticated_client_user_1.post("/profiles", json=profile_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["email"] == mock_user_1["email"]
        assert data["display_name"] == profile_data["display_name"]
    
    def test_create_profile_with_mismatched_email(self, authenticated_client_user_1):
        """Test creating profile with email not matching authenticated user"""
        profile_data = {
            "display_name": "Test User",
            "email": "different@example.com"  # Different from authenticated user's email
        }
        
        response = authenticated_client_user_1.post("/profiles", json=profile_data)
        assert response.status_code == 400
        assert "must match authenticated user's email" in response.json()["detail"]
    
    def test_create_duplicate_profile(self, authenticated_client_user_1, mock_user_1):
        """Test creating duplicate profile for same user"""
        profile_data = {
            "display_name": "Test User",
            "email": mock_user_1["email"]
        }
        
        # Create first profile
        response1 = authenticated_client_user_1.post("/profiles", json=profile_data)
        assert response1.status_code == 201
        
        # Try to create second profile for same user
        response2 = authenticated_client_user_1.post("/profiles", json=profile_data)
        assert response2.status_code == 400
        assert "already exists" in response2.json()["detail"]