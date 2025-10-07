"""
Pydantic schemas for API request/response models.
These are separate from SQLAlchemy models for data validation and serialization.
"""

from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from models import BandRole, EventType, EventStatus

# Profile schemas
class ProfileBase(BaseModel):
    display_name: str
    email: EmailStr

class ProfileCreate(ProfileBase):
    @field_validator('display_name')
    @classmethod
    def validate_display_name(cls, v):
        if len(v) < 1 or len(v) > 100:
            raise ValueError('Display name must be between 1 and 100 characters')
        return v

class ProfileResponse(ProfileBase):
    user_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

# Band schemas
class BandBase(BaseModel):
    name: str
    timezone: str = "America/New_York"

class BandCreate(BandBase):
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if len(v) < 2 or len(v) > 64:
            raise ValueError('Band name must be between 2 and 64 characters')
        return v

class BandResponse(BandBase):
    id: UUID
    join_code: str
    created_by: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

# Membership schemas
class MembershipBase(BaseModel):
    role: BandRole

class MembershipCreate(MembershipBase):
    band_id: UUID
    user_id: UUID

class MembershipResponse(MembershipBase):
    id: UUID
    band_id: UUID
    user_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

# Venue schemas
class VenueBase(BaseModel):
    name: str
    address: Optional[str] = None
    notes: Optional[str] = None

class VenueCreate(VenueBase):
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if len(v) < 2 or len(v) > 120:
            raise ValueError('Venue name must be between 2 and 120 characters')
        return v

class VenueResponse(VenueBase):
    id: UUID
    band_id: UUID
    
    class Config:
        from_attributes = True

# Event schemas
class EventBase(BaseModel):
    title: str
    starts_at_utc: datetime
    ends_at_utc: datetime
    type: EventType
    venue_id: Optional[UUID] = None
    notes: Optional[str] = None

class EventCreate(EventBase):
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if len(v) < 2 or len(v) > 120:
            raise ValueError('Event title must be between 2 and 120 characters')
        return v
    
    @field_validator('ends_at_utc')
    @classmethod
    def validate_times(cls, v, values):
        if 'starts_at_utc' in values.data and v <= values.data['starts_at_utc']:
            raise ValueError('Event must end after it starts')
        return v

class EventUpdate(BaseModel):
    title: Optional[str] = None
    starts_at_utc: Optional[datetime] = None
    ends_at_utc: Optional[datetime] = None
    type: Optional[EventType] = None
    status: Optional[EventStatus] = None
    venue_id: Optional[UUID] = None
    notes: Optional[str] = None

class EventResponse(EventBase):
    id: UUID
    band_id: UUID
    status: EventStatus
    created_by: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

# Nested response models with relationships
class BandWithMembers(BandResponse):
    memberships: List[MembershipResponse] = []

class ProfileWithBands(ProfileResponse):
    memberships: List[MembershipResponse] = []

class EventWithVenue(EventResponse):
    venue: Optional[VenueResponse] = None