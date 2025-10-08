"""
Unit tests for the BandRepository class.

These tests verify that database operations work correctly
in isolation, using an in-memory SQLite database.
"""

import pytest
from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from repository import BandRepository
from schemas import ProfileCreate, BandCreate, VenueCreate, EventCreate, EventUpdate
from models import BandRole, EventType, EventStatus
from tests.factories import (
    ProfileFactory, BandFactory, VenueFactory, EventFactory, MembershipFactory,
    TEST_USER_ID_1, TEST_USER_ID_2
)

class TestProfileRepository:
    """Test profile-related repository operations"""
    
    @pytest.mark.asyncio
    async def test_create_profile(self, test_repo: BandRepository):
        """Test creating a new profile"""
        profile_data = ProfileFactory()
        user_id = TEST_USER_ID_1
        
        profile = await test_repo.create_profile(profile_data, user_id)
        
        assert profile.user_id == user_id
        assert profile.display_name == profile_data.display_name
        assert profile.email == profile_data.email
        assert profile.created_at is not None
    
    @pytest.mark.asyncio
    async def test_get_profile(self, test_repo: BandRepository):
        """Test retrieving a profile by ID"""
        # Create a profile first
        profile_data = ProfileFactory()
        user_id = TEST_USER_ID_1
        created_profile = await test_repo.create_profile(profile_data, user_id)
        
        # Retrieve the profile
        retrieved_profile = await test_repo.get_profile(user_id)
        
        assert retrieved_profile is not None
        assert retrieved_profile.user_id == created_profile.user_id
        assert retrieved_profile.display_name == created_profile.display_name
        assert retrieved_profile.email == created_profile.email
    
    @pytest.mark.asyncio
    async def test_get_profile_by_email(self, test_repo: BandRepository):
        """Test retrieving a profile by email"""
        profile_data = ProfileFactory()
        user_id = TEST_USER_ID_1
        created_profile = await test_repo.create_profile(profile_data, user_id)
        
        retrieved_profile = await test_repo.get_profile_by_email(profile_data.email)
        
        assert retrieved_profile is not None
        assert retrieved_profile.email == created_profile.email
        assert retrieved_profile.user_id == created_profile.user_id
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_profile(self, test_repo: BandRepository):
        """Test retrieving a profile that doesn't exist"""
        nonexistent_id = uuid4()
        
        profile = await test_repo.get_profile(nonexistent_id)
        
        assert profile is None
    
    @pytest.mark.asyncio
    async def test_update_profile(self, test_repo: BandRepository):
        """Test updating a profile"""
        # Create a profile first
        profile_data = ProfileFactory()
        user_id = TEST_USER_ID_1
        created_profile = await test_repo.create_profile(profile_data, user_id)
        
        # Update the profile
        update_data = {"display_name": "Updated Name"}
        updated_profile = await test_repo.update_profile(user_id, update_data)
        
        assert updated_profile is not None
        assert updated_profile.display_name == "Updated Name"
        assert updated_profile.email == profile_data.email  # Should remain unchanged
    
    @pytest.mark.asyncio
    async def test_ensure_profile_exists_new_user(self, test_repo: BandRepository):
        """Test ensure_profile_exists creates new profile for new user"""
        user_id = TEST_USER_ID_1
        email = "test@example.com"
        display_name = "Test User"
        
        profile = await test_repo.ensure_profile_exists(user_id, email, display_name)
        
        assert profile.user_id == user_id
        assert profile.email == email
        assert profile.display_name == display_name
    
    @pytest.mark.asyncio
    async def test_ensure_profile_exists_existing_user(self, test_repo: BandRepository):
        """Test ensure_profile_exists returns existing profile"""
        # Create a profile first
        profile_data = ProfileFactory()
        user_id = TEST_USER_ID_1
        created_profile = await test_repo.create_profile(profile_data, user_id)
        
        # Call ensure_profile_exists - should return existing profile
        profile = await test_repo.ensure_profile_exists(user_id, profile_data.email, "Different Name")
        
        assert profile.user_id == created_profile.user_id
        assert profile.email == created_profile.email
        assert profile.display_name == created_profile.display_name  # Should not change
    
    @pytest.mark.asyncio
    async def test_ensure_profile_exists_auto_display_name(self, test_repo: BandRepository):
        """Test ensure_profile_exists auto-generates display name from email"""
        user_id = TEST_USER_ID_1
        email = "testuser@example.com"
        
        profile = await test_repo.ensure_profile_exists(user_id, email)
        
        assert profile.user_id == user_id
        assert profile.email == email
        assert profile.display_name == "testuser"  # Should be email prefix

class TestBandRepository:
    """Test band-related repository operations"""
    
    @pytest.mark.asyncio
    async def test_create_band(self, test_repo: BandRepository):
        """Test creating a new band"""
        # Create a user first
        profile_data = ProfileFactory()
        user_id = TEST_USER_ID_1
        await test_repo.create_profile(profile_data, user_id)
        
        # Create a band
        band_data = BandFactory()
        band = await test_repo.create_band(band_data, user_id)
        
        assert band.name == band_data.name
        assert band.timezone == band_data.timezone
        assert band.created_by == user_id
        assert band.join_code is not None
        assert len(band.join_code) > 0
        assert band.created_at is not None
    
    @pytest.mark.asyncio
    async def test_create_band_creates_leader_membership(self, test_repo: BandRepository):
        """Test that creating a band automatically creates a leader membership"""
        # Create a user first
        profile_data = ProfileFactory()
        user_id = TEST_USER_ID_1
        await test_repo.create_profile(profile_data, user_id)
        
        # Create a band
        band_data = BandFactory()
        band = await test_repo.create_band(band_data, user_id)
        
        # Check that the user is a leader of the band
        is_leader = await test_repo.check_user_is_band_leader(user_id, band.id)
        assert is_leader is True
        
        # Check band members
        members = await test_repo.get_band_members(band.id)
        assert len(members) == 1
        assert members[0].user_id == user_id
        assert members[0].role == BandRole.LEADER
    
    @pytest.mark.asyncio
    async def test_get_band(self, test_repo: BandRepository):
        """Test retrieving a band by ID"""
        # Create user and band
        profile_data = ProfileFactory()
        user_id = TEST_USER_ID_1
        await test_repo.create_profile(profile_data, user_id)
        
        band_data = BandFactory()
        created_band = await test_repo.create_band(band_data, user_id)
        
        # Retrieve the band
        retrieved_band = await test_repo.get_band(created_band.id)
        
        assert retrieved_band is not None
        assert retrieved_band.id == created_band.id
        assert retrieved_band.name == created_band.name
    
    @pytest.mark.asyncio
    async def test_get_user_bands(self, test_repo: BandRepository):
        """Test retrieving all bands for a user"""
        # Create user
        profile_data = ProfileFactory()
        user_id = TEST_USER_ID_1
        await test_repo.create_profile(profile_data, user_id)
        
        # Create multiple bands
        band1_data = BandFactory(name="Band 1")
        band2_data = BandFactory(name="Band 2")
        
        band1 = await test_repo.create_band(band1_data, user_id)
        band2 = await test_repo.create_band(band2_data, user_id)
        
        # Get user's bands
        user_bands = await test_repo.get_user_bands(user_id)
        
        assert len(user_bands) == 2
        band_names = [band.name for band in user_bands]
        assert "Band 1" in band_names
        assert "Band 2" in band_names
    
    @pytest.mark.asyncio
    async def test_join_band(self, test_repo: BandRepository):
        """Test joining a band using join code"""
        # Create two users
        profile1_data = ProfileFactory(display_name="Leader", email="leader@example.com")
        profile2_data = ProfileFactory(display_name="Member", email="member@example.com")
        user1_id = TEST_USER_ID_1
        user2_id = TEST_USER_ID_2
        
        await test_repo.create_profile(profile1_data, user1_id)
        await test_repo.create_profile(profile2_data, user2_id)
        
        # User 1 creates a band
        band_data = BandFactory()
        band = await test_repo.create_band(band_data, user1_id)
        
        # User 2 joins the band
        membership = await test_repo.join_band(band.join_code, user2_id)
        
        assert membership is not None
        assert membership.band_id == band.id
        assert membership.user_id == user2_id
        assert membership.role == BandRole.MEMBER
        
        # Verify user is now in the band
        is_member = await test_repo.check_user_in_band(user2_id, band.id)
        assert is_member is True
        
        # Check total band members
        members = await test_repo.get_band_members(band.id)
        assert len(members) == 2

    @pytest.mark.asyncio
    async def test_is_band_member(self, test_session: AsyncSession):
        """Test checking if user is a band member"""
        test_repo = BandRepository(test_session)
        
        # Create test band and user using repository methods
        user_id = "12345678-1234-5678-1234-567812345678"  # Valid UUID
        profile_data = ProfileFactory(user_id=user_id)
        await test_repo.create_profile(profile_data, user_id)
        
        band_data = BandFactory()
        band = await test_repo.create_band(band_data, user_id)
        
        # User should already be a member (band creator becomes leader)
        is_member = await test_repo.is_band_member(band.id, user_id)
        assert is_member is True
        
        # Test with non-existent user
        is_member = await test_repo.is_band_member(band.id, "87654321-4321-8765-4321-876543218765")
        assert is_member is False

    @pytest.mark.asyncio
    async def test_get_user_band_role(self, test_session: AsyncSession):
        """Test getting user's role in a band"""
        test_repo = BandRepository(test_session)
        
        # Create test band and users using repository methods
        admin_user_id = "12345678-1234-5678-1234-567812345678"  # Valid UUID
        member_user_id = "87654321-4321-8765-4321-876543218765"  # Valid UUID
        
        # Create admin user and band (admin becomes leader)
        admin_profile_data = ProfileFactory(user_id=admin_user_id)
        await test_repo.create_profile(admin_profile_data, admin_user_id)
        
        band_data = BandFactory()
        band = await test_repo.create_band(band_data, admin_user_id)
        
        # Create member user and add them to the band
        member_profile_data = ProfileFactory(user_id=member_user_id)
        await test_repo.create_profile(member_profile_data, member_user_id)
        await test_repo.join_band(band.join_code, member_user_id)
        
        # Check admin role (should be LEADER, not ADMIN)
        role = await test_repo.get_user_band_role(band.id, admin_user_id)
        assert role == BandRole.LEADER
        
        # Check member role
        role = await test_repo.get_user_band_role(band.id, member_user_id)
        assert role == BandRole.MEMBER
        
        # Check non-member user (should return None)
        non_member_id = "11111111-1111-1111-1111-111111111111"  # Valid UUID
        role = await test_repo.get_user_band_role(band.id, non_member_id)
        assert role is None

class TestVenueRepository:
    """Test venue-related repository operations"""
    
    @pytest.mark.asyncio
    async def test_create_venue(self, test_repo: BandRepository):
        """Test creating a new venue"""
        # Create user and band
        profile_data = ProfileFactory()
        user_id = TEST_USER_ID_1
        await test_repo.create_profile(profile_data, user_id)
        
        band_data = BandFactory()
        band = await test_repo.create_band(band_data, user_id)
        
        # Create venue
        venue_data = VenueFactory()
        venue = await test_repo.create_venue(venue_data, band.id)
        
        assert venue.name == venue_data.name
        assert venue.address == venue_data.address
        assert venue.notes == venue_data.notes
        assert venue.band_id == band.id
    
    @pytest.mark.asyncio
    async def test_get_band_venues(self, test_repo: BandRepository):
        """Test retrieving all venues for a band"""
        # Create user and band
        profile_data = ProfileFactory()
        user_id = TEST_USER_ID_1
        await test_repo.create_profile(profile_data, user_id)
        
        band_data = BandFactory()
        band = await test_repo.create_band(band_data, user_id)
        
        # Create multiple venues
        venue1_data = VenueFactory(name="Venue 1")
        venue2_data = VenueFactory(name="Venue 2")
        
        await test_repo.create_venue(venue1_data, band.id)
        await test_repo.create_venue(venue2_data, band.id)
        
        # Get band venues
        venues = await test_repo.get_band_venues(band.id)
        
        assert len(venues) == 2
        venue_names = [venue.name for venue in venues]
        assert "Venue 1" in venue_names
        assert "Venue 2" in venue_names

class TestEventRepository:
    """Test event-related repository operations"""
    
    @pytest.mark.asyncio
    async def test_create_event(self, test_repo: BandRepository):
        """Test creating a new event"""
        # Create user and band
        profile_data = ProfileFactory()
        user_id = TEST_USER_ID_1
        await test_repo.create_profile(profile_data, user_id)
        
        band_data = BandFactory()
        band = await test_repo.create_band(band_data, user_id)
        
        # Create event
        event_data = EventFactory()
        event = await test_repo.create_event(event_data, band.id, user_id)
        
        assert event.title == event_data.title
        assert event.type == event_data.type
        assert event.band_id == band.id
        assert event.created_by == user_id
        assert event.status == EventStatus.PLANNED  # Default status
    
    @pytest.mark.asyncio
    async def test_create_event_with_venue(self, test_repo: BandRepository):
        """Test creating an event with a venue"""
        # Create user and band
        profile_data = ProfileFactory()
        user_id = TEST_USER_ID_1
        await test_repo.create_profile(profile_data, user_id)
        
        band_data = BandFactory()
        band = await test_repo.create_band(band_data, user_id)
        
        # Create venue
        venue_data = VenueFactory()
        venue = await test_repo.create_venue(venue_data, band.id)
        
        # Create event with venue
        event_data = EventFactory(venue_id=venue.id)
        event = await test_repo.create_event(event_data, band.id, user_id)
        
        assert event.venue_id == venue.id
    
    @pytest.mark.asyncio
    async def test_get_band_events(self, test_repo: BandRepository):
        """Test retrieving all events for a band"""
        # Create user and band
        profile_data = ProfileFactory()
        user_id = TEST_USER_ID_1
        await test_repo.create_profile(profile_data, user_id)
        
        band_data = BandFactory()
        band = await test_repo.create_band(band_data, user_id)
        
        # Create multiple events
        event1_data = EventFactory(title="Rehearsal 1")
        event2_data = EventFactory(title="Gig 1", type=EventType.GIG)
        
        await test_repo.create_event(event1_data, band.id, user_id)
        await test_repo.create_event(event2_data, band.id, user_id)
        
        # Get band events
        events = await test_repo.get_band_events(band.id)
        
        assert len(events) == 2
        event_titles = [event.title for event in events]
        assert "Rehearsal 1" in event_titles
        assert "Gig 1" in event_titles
    
    @pytest.mark.asyncio
    async def test_update_event(self, test_repo: BandRepository):
        """Test updating an event"""
        # Create user and band
        profile_data = ProfileFactory()
        user_id = TEST_USER_ID_1
        await test_repo.create_profile(profile_data, user_id)
        
        band_data = BandFactory()
        band = await test_repo.create_band(band_data, user_id)
        
        # Create event
        event_data = EventFactory()
        event = await test_repo.create_event(event_data, band.id, user_id)
        
        # Update event
        update_data = EventUpdate(
            title="Updated Event Title",
            status=EventStatus.CONFIRMED
        )
        updated_event = await test_repo.update_event(event.id, update_data)
        
        assert updated_event is not None
        assert updated_event.title == "Updated Event Title"
        assert updated_event.status == EventStatus.CONFIRMED
        # Original fields should remain unchanged
        assert updated_event.type == event_data.type
    
    @pytest.mark.asyncio
    async def test_delete_event(self, test_repo: BandRepository):
        """Test deleting an event"""
        # Create user and band
        profile_data = ProfileFactory()
        user_id = TEST_USER_ID_1
        await test_repo.create_profile(profile_data, user_id)
        
        band_data = BandFactory()
        band = await test_repo.create_band(band_data, user_id)
        
        # Create event
        event_data = EventFactory()
        event = await test_repo.create_event(event_data, band.id, user_id)
        
        # Delete event
        success = await test_repo.delete_event(event.id)
        assert success is True
        
        # Verify event is deleted
        deleted_event = await test_repo.get_event(event.id)
        assert deleted_event is None