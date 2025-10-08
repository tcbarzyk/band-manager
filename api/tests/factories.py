"""
Factory classes for creating test data.

These factories provide consistent, realistic test data
and make it easy to create objects with specific attributes.
"""

import factory
from datetime import datetime, timezone, timedelta
import uuid

# Since we're using Pydantic schemas, we'll create factory classes for them
from schemas import ProfileCreate, BandCreate, VenueCreate, EventCreate
from models import EventType, BandRole, EventStatus, Membership

class ProfileFactory(factory.Factory):
    """Factory for creating Profile test data"""
    
    class Meta:
        model = ProfileCreate
    
    display_name = factory.Sequence(lambda n: f"Test User {n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.display_name.lower().replace(' ', '.')}@example.com")

class BandFactory(factory.Factory):
    """Factory for creating Band test data"""
    
    class Meta:
        model = BandCreate
    
    name = factory.Sequence(lambda n: f"Test Band {n}")
    timezone = "America/New_York"

class VenueFactory(factory.Factory):
    """Factory for creating Venue test data"""
    
    class Meta:
        model = VenueCreate
    
    name = factory.Sequence(lambda n: f"Test Venue {n}")
    address = factory.Faker("address")
    notes = factory.Faker("text", max_nb_chars=200)

class EventFactory(factory.Factory):
    """Factory for creating Event test data"""
    
    class Meta:
        model = EventCreate
    
    title = factory.Sequence(lambda n: f"Test Event {n}")
    starts_at_utc = factory.LazyFunction(
        lambda: datetime.now(timezone.utc) + timedelta(days=1)
    )
    ends_at_utc = factory.LazyAttribute(
        lambda obj: obj.starts_at_utc + timedelta(hours=2)
    )
    type = EventType.REHEARSAL
    notes = factory.Faker("text", max_nb_chars=200)

class RehearsalFactory(EventFactory):
    """Factory specifically for rehearsal events"""
    type = EventType.REHEARSAL
    title = factory.Sequence(lambda n: f"Band Rehearsal {n}")

class GigFactory(EventFactory):
    """Factory specifically for gig events"""
    type = EventType.GIG
    title = factory.Sequence(lambda n: f"Live Performance {n}")

class MembershipFactory(factory.Factory):
    """Factory for creating Membership test data"""
    
    class Meta:
        model = Membership
    
    role = BandRole.MEMBER

# Utility functions for creating test UUIDs
def generate_test_uuid(seed: str = None) -> uuid.UUID:
    """Generate a deterministic UUID for testing"""
    if seed:
        # Create a deterministic UUID based on seed
        import hashlib
        hash_value = hashlib.md5(seed.encode()).hexdigest()
        return uuid.UUID(hash_value)
    return uuid.uuid4()

# Predefined test UUIDs for consistency
TEST_USER_ID_1 = uuid.UUID("11111111-1111-1111-1111-111111111111")
TEST_USER_ID_2 = uuid.UUID("22222222-2222-2222-2222-222222222222")
TEST_BAND_ID = uuid.UUID("33333333-3333-3333-3333-333333333333")
TEST_VENUE_ID = uuid.UUID("44444444-4444-4444-4444-444444444444")
TEST_EVENT_ID = uuid.UUID("55555555-5555-5555-5555-555555555555")