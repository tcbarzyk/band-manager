"""
Integration tests for FastAPI endpoints.

These tests verify that the HTTP API works correctly
by making actual HTTP requests to the application.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
import json
from uuid import uuid4
from datetime import datetime, timezone

from tests.factories import (
    ProfileFactory, BandFactory, VenueFactory, EventFactory,
    TEST_USER_ID_1, TEST_USER_ID_2
)

class TestProfileEndpoints:
    """Test profile-related API endpoints"""
    
    def test_create_profile(self, test_client: TestClient):
        """Test POST /profiles endpoint"""
        profile_data = ProfileFactory()
        
        response = test_client.post(
            "/profiles",
            json=profile_data.dict()
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["display_name"] == profile_data.display_name
        assert data["email"] == profile_data.email
        assert "user_id" in data
        assert "created_at" in data
    
    def test_create_profile_duplicate_email(self, test_client: TestClient):
        """Test creating profile with duplicate email"""
        profile_data = ProfileFactory(email="duplicate@example.com")
        
        # Create first profile
        response1 = test_client.post("/profiles", json=profile_data.dict())
        assert response1.status_code == 201
        
        # Try to create second profile with same email
        response2 = test_client.post("/profiles", json=profile_data.dict())
        assert response2.status_code == 400
        assert "Email already registered" in response2.json()["detail"]
    
    def test_get_profile(self, test_client: TestClient):
        """Test GET /profiles/{user_id} endpoint"""
        # Create a profile first
        profile_data = ProfileFactory()
        create_response = test_client.post("/profiles", json=profile_data.dict())
        created_profile = create_response.json()
        
        # Get the profile
        response = test_client.get(f"/profiles/{created_profile['user_id']}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == created_profile["user_id"]
        assert data["display_name"] == profile_data.display_name
        assert data["email"] == profile_data.email
    
    def test_get_nonexistent_profile(self, test_client: TestClient):
        """Test getting a profile that doesn't exist"""
        nonexistent_id = str(uuid4())
        
        response = test_client.get(f"/profiles/{nonexistent_id}")
        
        assert response.status_code == 404
        assert "Profile not found" in response.json()["detail"]

class TestBandEndpoints:
    """Test band-related API endpoints"""
    
    def test_create_band(self, test_client: TestClient):
        """Test POST /bands endpoint"""
        band_data = BandFactory()
        
        response = test_client.post("/bands", json=band_data.dict())
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == band_data.name
        assert data["timezone"] == band_data.timezone
        assert "id" in data
        assert "join_code" in data
        assert "created_by" in data
        assert "created_at" in data
    
    def test_get_band(self, test_client: TestClient):
        """Test GET /bands/{band_id} endpoint"""
        # Create a band first
        band_data = BandFactory()
        create_response = test_client.post("/bands", json=band_data.dict())
        created_band = create_response.json()
        
        # Get the band
        response = test_client.get(f"/bands/{created_band['id']}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_band["id"]
        assert data["name"] == band_data.name
    
    def test_get_nonexistent_band(self, test_client: TestClient):
        """Test getting a band that doesn't exist"""
        nonexistent_id = str(uuid4())
        
        response = test_client.get(f"/bands/{nonexistent_id}")
        
        assert response.status_code == 404
        assert "Band not found" in response.json()["detail"]
    
    def test_join_band(self, test_client: TestClient):
        """Test POST /bands/join/{join_code} endpoint"""
        # Create a band first
        band_data = BandFactory()
        create_response = test_client.post("/bands", json=band_data.dict())
        created_band = create_response.json()
        join_code = created_band["join_code"]
        
        # Join the band
        response = test_client.post(f"/bands/join/{join_code}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["band_id"] == created_band["id"]
        assert data["role"] == "member"
        assert "user_id" in data
        assert "created_at" in data
    
    def test_join_band_invalid_code(self, test_client: TestClient):
        """Test joining with invalid join code"""
        invalid_code = "invalid_code"
        
        response = test_client.post(f"/bands/join/{invalid_code}")
        
        assert response.status_code == 400
        assert "Invalid join code" in response.json()["detail"]
    
    def test_get_band_members(self, test_client: TestClient):
        """Test GET /bands/{band_id}/members endpoint"""
        # Create a band
        band_data = BandFactory()
        create_response = test_client.post("/bands", json=band_data.dict())
        created_band = create_response.json()
        
        # Get band members
        response = test_client.get(f"/bands/{created_band['id']}/members")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1  # Creator should be a member
        assert data[0]["role"] == "leader"
        assert data[0]["band_id"] == created_band["id"]

class TestVenueEndpoints:
    """Test venue-related API endpoints"""
    
    def test_create_venue(self, test_client: TestClient):
        """Test POST /bands/{band_id}/venues endpoint"""
        # Create a band first
        band_data = BandFactory()
        band_response = test_client.post("/bands", json=band_data.dict())
        created_band = band_response.json()
        
        # Create venue
        venue_data = VenueFactory()
        response = test_client.post(
            f"/bands/{created_band['id']}/venues",
            json=venue_data.dict()
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == venue_data.name
        assert data["address"] == venue_data.address
        assert data["notes"] == venue_data.notes
        assert data["band_id"] == created_band["id"]
    
    def test_get_band_venues(self, test_client: TestClient):
        """Test GET /bands/{band_id}/venues endpoint"""
        # Create a band
        band_data = BandFactory()
        band_response = test_client.post("/bands", json=band_data.dict())
        created_band = band_response.json()
        
        # Create venues
        venue1_data = VenueFactory(name="Venue 1")
        venue2_data = VenueFactory(name="Venue 2")
        
        test_client.post(f"/bands/{created_band['id']}/venues", json=venue1_data.dict())
        test_client.post(f"/bands/{created_band['id']}/venues", json=venue2_data.dict())
        
        # Get venues
        response = test_client.get(f"/bands/{created_band['id']}/venues")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        venue_names = [venue["name"] for venue in data]
        assert "Venue 1" in venue_names
        assert "Venue 2" in venue_names
    
    def test_get_venue(self, test_client: TestClient):
        """Test GET /venues/{venue_id} endpoint"""
        # Create band and venue
        band_data = BandFactory()
        band_response = test_client.post("/bands", json=band_data.dict())
        created_band = band_response.json()
        
        venue_data = VenueFactory()
        venue_response = test_client.post(
            f"/bands/{created_band['id']}/venues",
            json=venue_data.dict()
        )
        created_venue = venue_response.json()
        
        # Get the venue
        response = test_client.get(f"/venues/{created_venue['id']}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_venue["id"]
        assert data["name"] == venue_data.name
    
    def test_delete_venue(self, test_client: TestClient):
        """Test DELETE /venues/{venue_id} endpoint"""
        # Create band and venue
        band_data = BandFactory()
        band_response = test_client.post("/bands", json=band_data.dict())
        created_band = band_response.json()
        
        venue_data = VenueFactory()
        venue_response = test_client.post(
            f"/bands/{created_band['id']}/venues",
            json=venue_data.dict()
        )
        created_venue = venue_response.json()
        
        # Delete the venue
        response = test_client.delete(f"/venues/{created_venue['id']}")
        
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]
        
        # Verify venue is deleted
        get_response = test_client.get(f"/venues/{created_venue['id']}")
        assert get_response.status_code == 404

class TestEventEndpoints:
    """Test event-related API endpoints"""
    
    def test_create_event(self, test_client: TestClient):
        """Test POST /bands/{band_id}/events endpoint"""
        # Create a band first
        band_data = BandFactory()
        band_response = test_client.post("/bands", json=band_data.dict())
        created_band = band_response.json()
        
        # Create event
        event_data = EventFactory()
        event_dict = event_data.dict()
        # Convert datetime to ISO string for JSON serialization
        event_dict["starts_at_utc"] = event_data.starts_at_utc.isoformat()
        event_dict["ends_at_utc"] = event_data.ends_at_utc.isoformat()
        
        response = test_client.post(
            f"/bands/{created_band['id']}/events",
            json=event_dict
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == event_data.title
        assert data["type"] == event_data.type.value
        assert data["band_id"] == created_band["id"]
        assert data["status"] == "planned"  # Default status
    
    def test_get_band_events(self, test_client: TestClient):
        """Test GET /bands/{band_id}/events endpoint"""
        # Create a band
        band_data = BandFactory()
        band_response = test_client.post("/bands", json=band_data.dict())
        created_band = band_response.json()
        
        # Create events
        event1_data = EventFactory(title="Rehearsal 1")
        event2_data = EventFactory(title="Gig 1")
        
        for event_data in [event1_data, event2_data]:
            event_dict = event_data.dict()
            event_dict["starts_at_utc"] = event_data.starts_at_utc.isoformat()
            event_dict["ends_at_utc"] = event_data.ends_at_utc.isoformat()
            test_client.post(f"/bands/{created_band['id']}/events", json=event_dict)
        
        # Get events
        response = test_client.get(f"/bands/{created_band['id']}/events")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        event_titles = [event["title"] for event in data]
        assert "Rehearsal 1" in event_titles
        assert "Gig 1" in event_titles
    
    def test_get_event(self, test_client: TestClient):
        """Test GET /events/{event_id} endpoint"""
        # Create band and event
        band_data = BandFactory()
        band_response = test_client.post("/bands", json=band_data.dict())
        created_band = band_response.json()
        
        event_data = EventFactory()
        event_dict = event_data.dict()
        event_dict["starts_at_utc"] = event_data.starts_at_utc.isoformat()
        event_dict["ends_at_utc"] = event_data.ends_at_utc.isoformat()
        
        event_response = test_client.post(
            f"/bands/{created_band['id']}/events",
            json=event_dict
        )
        created_event = event_response.json()
        
        # Get the event
        response = test_client.get(f"/events/{created_event['id']}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_event["id"]
        assert data["title"] == event_data.title
    
    def test_update_event(self, test_client: TestClient):
        """Test PUT /events/{event_id} endpoint"""
        # Create band and event
        band_data = BandFactory()
        band_response = test_client.post("/bands", json=band_data.dict())
        created_band = band_response.json()
        
        event_data = EventFactory()
        event_dict = event_data.dict()
        event_dict["starts_at_utc"] = event_data.starts_at_utc.isoformat()
        event_dict["ends_at_utc"] = event_data.ends_at_utc.isoformat()
        
        event_response = test_client.post(
            f"/bands/{created_band['id']}/events",
            json=event_dict
        )
        created_event = event_response.json()
        
        # Update the event
        update_data = {
            "title": "Updated Event Title",
            "status": "confirmed"
        }
        response = test_client.put(f"/events/{created_event['id']}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Event Title"
        assert data["status"] == "confirmed"
    
    def test_delete_event(self, test_client: TestClient):
        """Test DELETE /events/{event_id} endpoint"""
        # Create band and event
        band_data = BandFactory()
        band_response = test_client.post("/bands", json=band_data.dict())
        created_band = band_response.json()
        
        event_data = EventFactory()
        event_dict = event_data.dict()
        event_dict["starts_at_utc"] = event_data.starts_at_utc.isoformat()
        event_dict["ends_at_utc"] = event_data.ends_at_utc.isoformat()
        
        event_response = test_client.post(
            f"/bands/{created_band['id']}/events",
            json=event_dict
        )
        created_event = event_response.json()
        
        # Delete the event
        response = test_client.delete(f"/events/{created_event['id']}")
        
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]
        
        # Verify event is deleted
        get_response = test_client.get(f"/events/{created_event['id']}")
        assert get_response.status_code == 404

class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_root_endpoint(self, test_client: TestClient):
        """Test GET / endpoint"""
        response = test_client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "Band Manager API" in data["message"]
        assert data["status"] == "healthy"
    
    def test_health_endpoint(self, test_client: TestClient):
        """Test GET /health endpoint"""
        response = test_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "band-manager-api"