import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone


class TestProfileEndpoints:
    """Test profile-related API endpoints with authentication"""
    
    def test_create_profile_authenticated(self, authenticated_client_user_1, mock_user_1):
        """Test POST /profiles endpoint with authentication"""
        profile_data = {
            "display_name": "Test User",
            "email": mock_user_1["email"]  # Must match authenticated user
        }
        
        response = authenticated_client_user_1.post(
            "/profiles",
            json=profile_data
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["display_name"] == profile_data["display_name"]
        assert data["email"] == profile_data["email"]
        assert "user_id" in data
        assert "created_at" in data
    
    def test_create_profile_unauthenticated(self, unauthenticated_client):
        """Test POST /profiles endpoint without authentication"""
        profile_data = {
            "display_name": "Test User",
            "email": "test@example.com"
        }
        
        response = unauthenticated_client.post("/profiles", json=profile_data)
        assert response.status_code == 403
    
    def test_create_profile_email_mismatch(self, authenticated_client_user_1):
        """Test creating profile with email not matching authenticated user"""
        profile_data = {
            "display_name": "Test User",
            "email": "different@example.com"
        }
        
        response = authenticated_client_user_1.post("/profiles", json=profile_data)
        assert response.status_code == 400
        assert "must match authenticated user's email" in response.json()["detail"]
    
    def test_get_profile(self, authenticated_client_user_1, mock_user_1):
        """Test GET /profiles/{user_id} endpoint"""
        # First create a profile
        profile_data = {
            "display_name": "Test User",
            "email": mock_user_1["email"]
        }
        create_response = authenticated_client_user_1.post("/profiles", json=profile_data)
        assert create_response.status_code == 201
        profile = create_response.json()
        user_id = profile["user_id"]
        
        # Test getting the profile (authenticated user can get any profile)
        response = authenticated_client_user_1.get(f"/profiles/{user_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["user_id"] == user_id
        assert data["display_name"] == profile_data["display_name"]
    
    def test_get_profile_unauthenticated(self, unauthenticated_client):
        """Test GET /profiles/{user_id} without authentication"""
        fake_user_id = "12345678-1234-5678-1234-567812345678"
        response = unauthenticated_client.get(f"/profiles/{fake_user_id}")
        assert response.status_code == 403


class TestBandEndpoints:
    """Test band-related API endpoints with authentication"""
    
    def test_create_band_authenticated(self, authenticated_client_user_1):
        """Test POST /bands endpoint with authentication"""
        band_data = {
            "name": "Test Band",
            "timezone": "America/New_York"
        }
        
        response = authenticated_client_user_1.post("/bands", json=band_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == band_data["name"]
        assert data["timezone"] == band_data["timezone"]
        assert "id" in data
        assert "join_code" in data
        assert "created_by" in data
    
    def test_create_band_unauthenticated(self, unauthenticated_client):
        """Test POST /bands endpoint without authentication"""
        band_data = {
            "name": "Test Band",
            "timezone": "America/New_York"
        }
        
        response = unauthenticated_client.post("/bands", json=band_data)
        assert response.status_code == 403
    
    def test_get_band_as_member(self, authenticated_client_user_1):
        """Test GET /bands/{band_id} as a band member"""
        # Create a band
        band_data = {"name": "Test Band", "timezone": "America/New_York"}
        create_response = authenticated_client_user_1.post("/bands", json=band_data)
        assert create_response.status_code == 201
        band = create_response.json()
        
        # Get the band (creator should be able to access)
        response = authenticated_client_user_1.get(f"/bands/{band['id']}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == band["id"]
        assert data["name"] == band["name"]
    
    def test_get_band_as_non_member(self, authenticated_client_user_1, authenticated_client_user_2):
        """Test GET /bands/{band_id} as a non-member"""
        # User 1 creates a band
        band_data = {"name": "Test Band", "timezone": "America/New_York"}
        create_response = authenticated_client_user_1.post("/bands", json=band_data)
        assert create_response.status_code == 201
        band = create_response.json()
        
        # User 2 tries to access the band (should be forbidden)
        response = authenticated_client_user_2.get(f"/bands/{band['id']}")
        assert response.status_code == 403
    
    def test_get_band_unauthenticated(self, unauthenticated_client):
        """Test GET /bands/{band_id} without authentication"""
        fake_band_id = "12345678-1234-5678-1234-567812345678"
        response = unauthenticated_client.get(f"/bands/{fake_band_id}")
        assert response.status_code == 403
    
    def test_get_my_bands(self, authenticated_client_user_1):
        """Test GET /my/bands endpoint"""
        # Create a couple of bands
        band_data_1 = {"name": "Band 1", "timezone": "America/New_York"}
        band_data_2 = {"name": "Band 2", "timezone": "America/Los_Angeles"}
        
        response1 = authenticated_client_user_1.post("/bands", json=band_data_1)
        response2 = authenticated_client_user_1.post("/bands", json=band_data_2)
        assert response1.status_code == 201
        assert response2.status_code == 201
        
        # Get user's bands
        response = authenticated_client_user_1.get("/my/bands")
        assert response.status_code == 200
        
        bands = response.json()
        assert len(bands) == 2
        band_names = [band["name"] for band in bands]
        assert "Band 1" in band_names
        assert "Band 2" in band_names
    
    def test_get_my_bands_unauthenticated(self, unauthenticated_client):
        """Test GET /my/bands without authentication"""
        response = unauthenticated_client.get("/my/bands")
        assert response.status_code == 403
    
    def test_join_band_with_valid_code(self, authenticated_client_user_1, authenticated_client_user_2):
        """Test POST /bands/join/{join_code} with valid join code"""
        # User 1 creates a band
        band_data = {"name": "Test Band", "timezone": "America/New_York"}
        create_response = authenticated_client_user_1.post("/bands", json=band_data)
        assert create_response.status_code == 201
        band = create_response.json()
        join_code = band["join_code"]
        
        # User 2 joins the band
        response = authenticated_client_user_2.post(f"/bands/join/{join_code}")
        assert response.status_code == 201
        
        membership = response.json()
        assert membership["band_id"] == band["id"]
        assert membership["role"] == "MEMBER"
    
    def test_join_band_unauthenticated(self, unauthenticated_client):
        """Test POST /bands/join/{join_code} without authentication"""
        response = unauthenticated_client.post("/bands/join/fake-code")
        assert response.status_code == 403
    
    def test_get_band_members_as_member(self, authenticated_client_user_1, authenticated_client_user_2):
        """Test GET /bands/{band_id}/members as a band member"""
        # User 1 creates band
        band_data = {"name": "Test Band", "timezone": "America/New_York"}
        create_response = authenticated_client_user_1.post("/bands", json=band_data)
        band = create_response.json()
        
        # User 2 joins the band
        join_response = authenticated_client_user_2.post(f"/bands/join/{band['join_code']}")
        assert join_response.status_code == 201
        
        # User 1 gets members list
        response = authenticated_client_user_1.get(f"/bands/{band['id']}/members")
        assert response.status_code == 200
        
        members = response.json()
        assert len(members) == 2  # Creator + joiner
    
    def test_get_band_members_as_non_member(self, authenticated_client_user_1, authenticated_client_user_2):
        """Test GET /bands/{band_id}/members as a non-member"""
        # User 1 creates band
        band_data = {"name": "Test Band", "timezone": "America/New_York"}
        create_response = authenticated_client_user_1.post("/bands", json=band_data)
        band = create_response.json()
        
        # User 2 tries to get members (should be forbidden)
        response = authenticated_client_user_2.get(f"/bands/{band['id']}/members")
        assert response.status_code == 403


class TestVenueEndpoints:
    """Test venue-related API endpoints with authentication"""
    
    def test_create_venue_as_member(self, authenticated_client_user_1):
        """Test POST /bands/{band_id}/venues as a band member"""
        # Create a band first
        band_data = {"name": "Test Band", "timezone": "America/New_York"}
        band_response = authenticated_client_user_1.post("/bands", json=band_data)
        band = band_response.json()
        
        # Create a venue
        venue_data = {
            "name": "Test Venue",
            "address": "123 Test Street",
            "notes": "Test venue notes"
        }
        
        response = authenticated_client_user_1.post(f"/bands/{band['id']}/venues", json=venue_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == venue_data["name"]
        assert data["address"] == venue_data["address"]
        assert data["band_id"] == band["id"]
    
    def test_create_venue_as_non_member(self, authenticated_client_user_1, authenticated_client_user_2):
        """Test POST /bands/{band_id}/venues as a non-member"""
        # User 1 creates a band
        band_data = {"name": "Test Band", "timezone": "America/New_York"}
        band_response = authenticated_client_user_1.post("/bands", json=band_data)
        band = band_response.json()
        
        # User 2 tries to create a venue (should be forbidden)
        venue_data = {"name": "Test Venue", "address": "123 Test Street"}
        response = authenticated_client_user_2.post(f"/bands/{band['id']}/venues", json=venue_data)
        assert response.status_code == 403
    
    def test_get_band_venues_as_member(self, authenticated_client_user_1):
        """Test GET /bands/{band_id}/venues as a band member"""
        # Create band and venue
        band_data = {"name": "Test Band", "timezone": "America/New_York"}
        band_response = authenticated_client_user_1.post("/bands", json=band_data)
        band = band_response.json()
        
        venue_data = {"name": "Test Venue", "address": "123 Test Street"}
        venue_response = authenticated_client_user_1.post(f"/bands/{band['id']}/venues", json=venue_data)
        assert venue_response.status_code == 201
        
        # Get venues
        response = authenticated_client_user_1.get(f"/bands/{band['id']}/venues")
        assert response.status_code == 200
        
        venues = response.json()
        assert len(venues) == 1
        assert venues[0]["name"] == venue_data["name"]
    
    def test_get_venue_by_id_as_member(self, authenticated_client_user_1):
        """Test GET /venues/{venue_id} as a band member"""
        # Create band and venue
        band_data = {"name": "Test Band", "timezone": "America/New_York"}
        band_response = authenticated_client_user_1.post("/bands", json=band_data)
        band = band_response.json()
        
        venue_data = {"name": "Test Venue", "address": "123 Test Street"}
        venue_response = authenticated_client_user_1.post(f"/bands/{band['id']}/venues", json=venue_data)
        venue = venue_response.json()
        
        # Get venue by ID
        response = authenticated_client_user_1.get(f"/venues/{venue['id']}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == venue["id"]
        assert data["name"] == venue["name"]


class TestEventEndpoints:
    """Test event-related API endpoints with authentication"""
    
    def test_create_event_as_member(self, authenticated_client_user_1):
        """Test POST /bands/{band_id}/events as a band member"""
        # Create a band first
        band_data = {"name": "Test Band", "timezone": "America/New_York"}
        band_response = authenticated_client_user_1.post("/bands", json=band_data)
        band = band_response.json()
        
        # Create an event
        event_data = {
            "title": "Test Rehearsal",
            "type": "REHEARSAL",
            "starts_at_utc": "2025-10-15T19:00:00Z",
            "ends_at_utc": "2025-10-15T21:00:00Z",
            "notes": "Test rehearsal notes"
        }
        
        response = authenticated_client_user_1.post(f"/bands/{band['id']}/events", json=event_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == event_data["title"]
        assert data["type"] == event_data["type"]
        assert data["band_id"] == band["id"]
    
    def test_create_event_as_non_member(self, authenticated_client_user_1, authenticated_client_user_2):
        """Test POST /bands/{band_id}/events as a non-member"""
        # User 1 creates a band
        band_data = {"name": "Test Band", "timezone": "America/New_York"}
        band_response = authenticated_client_user_1.post("/bands", json=band_data)
        band = band_response.json()
        
        # User 2 tries to create an event (should be forbidden)
        event_data = {
            "title": "Test Event",
            "type": "REHEARSAL",
            "starts_at_utc": "2025-10-15T19:00:00Z",
            "ends_at_utc": "2025-10-15T21:00:00Z"
        }
        response = authenticated_client_user_2.post(f"/bands/{band['id']}/events", json=event_data)
        assert response.status_code == 403
    
    def test_get_band_events_as_member(self, authenticated_client_user_1):
        """Test GET /bands/{band_id}/events as a band member"""
        # Create band and event
        band_data = {"name": "Test Band", "timezone": "America/New_York"}
        band_response = authenticated_client_user_1.post("/bands", json=band_data)
        band = band_response.json()
        
        event_data = {
            "title": "Test Event",
            "type": "REHEARSAL",
            "starts_at_utc": "2025-10-15T19:00:00Z",
            "ends_at_utc": "2025-10-15T21:00:00Z"
        }
        event_response = authenticated_client_user_1.post(f"/bands/{band['id']}/events", json=event_data)
        assert event_response.status_code == 201
        
        # Get events
        response = authenticated_client_user_1.get(f"/bands/{band['id']}/events")
        assert response.status_code == 200
        
        events = response.json()
        assert len(events) == 1
        assert events[0]["title"] == event_data["title"]
    
    def test_get_event_by_id_as_member(self, authenticated_client_user_1):
        """Test GET /events/{event_id} as a band member"""
        # Create band and event
        band_data = {"name": "Test Band", "timezone": "America/New_York"}
        band_response = authenticated_client_user_1.post("/bands", json=band_data)
        band = band_response.json()
        
        event_data = {
            "title": "Test Event",
            "type": "REHEARSAL",
            "starts_at_utc": "2025-10-15T19:00:00Z",
            "ends_at_utc": "2025-10-15T21:00:00Z"
        }
        event_response = authenticated_client_user_1.post(f"/bands/{band['id']}/events", json=event_data)
        event = event_response.json()
        
        # Get event by ID
        response = authenticated_client_user_1.get(f"/events/{event['id']}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == event["id"]
        assert data["title"] == event["title"]
    
    def test_update_event_as_member(self, authenticated_client_user_1):
        """Test PUT /events/{event_id} as a band member"""
        # Create band and event
        band_data = {"name": "Test Band", "timezone": "America/New_York"}
        band_response = authenticated_client_user_1.post("/bands", json=band_data)
        band = band_response.json()
        
        event_data = {
            "title": "Test Event",
            "type": "REHEARSAL",
            "starts_at_utc": "2025-10-15T19:00:00Z",
            "ends_at_utc": "2025-10-15T21:00:00Z"
        }
        event_response = authenticated_client_user_1.post(f"/bands/{band['id']}/events", json=event_data)
        event = event_response.json()
        
        # Update event
        update_data = {"title": "Updated Event Title"}
        response = authenticated_client_user_1.put(f"/events/{event['id']}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == "Updated Event Title"
    
    def test_delete_event_as_member(self, authenticated_client_user_1):
        """Test DELETE /events/{event_id} as a band member"""
        # Create band and event
        band_data = {"name": "Test Band", "timezone": "America/New_York"}
        band_response = authenticated_client_user_1.post("/bands", json=band_data)
        band = band_response.json()
        
        event_data = {
            "title": "Test Event",
            "type": "REHEARSAL",
            "starts_at_utc": "2025-10-15T19:00:00Z",
            "ends_at_utc": "2025-10-15T21:00:00Z"
        }
        event_response = authenticated_client_user_1.post(f"/bands/{band['id']}/events", json=event_data)
        event = event_response.json()
        
        # Delete event
        response = authenticated_client_user_1.delete(f"/events/{event['id']}")
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]
        
        # Verify event is deleted
        get_response = authenticated_client_user_1.get(f"/events/{event['id']}")
        assert get_response.status_code == 404


class TestPublicEndpoints:
    """Test public endpoints that don't require authentication"""
    
    def test_root_endpoint(self, unauthenticated_client):
        """Test GET / endpoint"""
        response = unauthenticated_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "status" in data
    
    def test_health_endpoint(self, unauthenticated_client):
        """Test GET /health endpoint"""
        response = unauthenticated_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"