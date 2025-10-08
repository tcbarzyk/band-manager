"""
Repository layer for database operations using SQLAlchemy.
This layer abstracts database operations and provides a clean interface for the API.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import and_, or_
from typing import List, Optional
from uuid import UUID
import secrets

from models import Profile, Band, Membership, Venue, Event, BandRole, EventStatus
from schemas import (
    ProfileCreate, BandCreate, VenueCreate, EventCreate, EventUpdate
)

class BandRepository:
    """Repository for all band-related database operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    # Profile operations
    async def create_profile(self, profile_data: ProfileCreate, user_id: UUID) -> Profile:
        """Create a new user profile linked to Supabase auth user"""
        db_profile = Profile(
            user_id=user_id,
            display_name=profile_data.display_name,
            email=profile_data.email
        )
        self.db.add(db_profile)
        await self.db.commit()
        await self.db.refresh(db_profile)
        return db_profile

    async def get_profile(self, user_id: UUID) -> Optional[Profile]:
        """Get user profile by ID"""
        result = await self.db.execute(
            select(Profile).where(Profile.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_profile_by_email(self, email: str) -> Optional[Profile]:
        """Get user profile by email"""
        result = await self.db.execute(
            select(Profile).where(Profile.email == email)
        )
        return result.scalar_one_or_none()

    async def update_profile(self, user_id: UUID, update_data: dict) -> Optional[Profile]:
        """Update user profile"""
        profile = await self.get_profile(user_id)
        if not profile:
            return None
            
        for field, value in update_data.items():
            if hasattr(profile, field) and value is not None:
                setattr(profile, field, value)
        
        await self.db.commit()
        await self.db.refresh(profile)
        return profile

    async def ensure_profile_exists(self, user_id: UUID, email: str, display_name: str = None) -> Profile:
        """Ensure a profile exists for a Supabase user, create if not exists"""
        profile = await self.get_profile(user_id)
        
        if not profile:
            # Create profile using the display name or email prefix
            if not display_name:
                display_name = email.split('@')[0]
            
            profile_data = ProfileCreate(
                display_name=display_name,
                email=email
            )
            profile = await self.create_profile(profile_data, user_id)
        
        return profile

    async def update_profile(self, user_id: UUID, profile_data: dict) -> Optional[Profile]:
        """Update user profile"""
        profile = await self.get_profile(user_id)
        if not profile:
            return None
        
        for key, value in profile_data.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        
        await self.db.commit()
        await self.db.refresh(profile)
        return profile

    # Band operations
    async def create_band(self, band_data: BandCreate, created_by: UUID) -> Band:
        """Create a new band and add creator as leader"""
        # Generate unique join code
        join_code = secrets.token_urlsafe(8)
        
        # Create band
        db_band = Band(
            name=band_data.name,
            timezone=band_data.timezone,
            join_code=join_code,
            created_by=created_by
        )
        self.db.add(db_band)
        await self.db.flush()  # Flush to get the band ID
        
        # Add creator as leader
        membership = Membership(
            band_id=db_band.id,
            user_id=created_by,
            role=BandRole.LEADER
        )
        self.db.add(membership)
        
        await self.db.commit()
        await self.db.refresh(db_band)
        return db_band

    async def get_band(self, band_id: UUID) -> Optional[Band]:
        """Get band by ID"""
        result = await self.db.execute(
            select(Band).where(Band.id == band_id)
        )
        return result.scalar_one_or_none()

    async def get_band_by_join_code(self, join_code: str) -> Optional[Band]:
        """Get band by join code"""
        result = await self.db.execute(
            select(Band).where(Band.join_code == join_code)
        )
        return result.scalar_one_or_none()

    async def get_user_bands(self, user_id: UUID) -> List[Band]:
        """Get all bands for a user"""
        result = await self.db.execute(
            select(Band)
            .join(Membership)
            .where(Membership.user_id == user_id)
            .order_by(Band.created_at.desc())
        )
        return result.scalars().all()

    async def is_band_member(self, band_id: UUID, user_id: UUID) -> bool:
        """Check if user is a member of the band"""
        result = await self.db.execute(
            select(Membership).where(
                and_(Membership.band_id == band_id, Membership.user_id == user_id)
            )
        )
        return result.scalar_one_or_none() is not None

    async def get_user_band_role(self, band_id: UUID, user_id: UUID) -> Optional[BandRole]:
        """Get user's role in a specific band"""
        result = await self.db.execute(
            select(Membership.role).where(
                and_(Membership.band_id == band_id, Membership.user_id == user_id)
            )
        )
        role = result.scalar_one_or_none()
        return role

    async def update_band(self, band_id: UUID, band_data: dict) -> Optional[Band]:
        """Update band information"""
        band = await self.get_band(band_id)
        if not band:
            return None
        
        for key, value in band_data.items():
            if hasattr(band, key):
                setattr(band, key, value)
        
        await self.db.commit()
        await self.db.refresh(band)
        return band

    # Membership operations
    async def join_band(self, join_code: str, user_id: UUID) -> Optional[Membership]:
        """Join a band using join code"""
        band = await self.get_band_by_join_code(join_code)
        if not band:
            return None
        
        # Check if user is already a member
        existing = await self.db.execute(
            select(Membership).where(
                and_(Membership.band_id == band.id, Membership.user_id == user_id)
            )
        )
        if existing.scalar_one_or_none():
            return None  # Already a member
        
        membership = Membership(
            band_id=band.id,
            user_id=user_id,
            role=BandRole.MEMBER
        )
        self.db.add(membership)
        await self.db.commit()
        await self.db.refresh(membership)
        return membership

    async def get_band_members(self, band_id: UUID) -> List[Membership]:
        """Get all members of a band"""
        result = await self.db.execute(
            select(Membership)
            .options(selectinload(Membership.user))
            .where(Membership.band_id == band_id)
            .order_by(Membership.created_at)
        )
        return result.scalars().all()

    async def update_member_role(self, membership_id: UUID, role: BandRole) -> Optional[Membership]:
        """Update member role in band"""
        result = await self.db.execute(
            select(Membership).where(Membership.id == membership_id)
        )
        membership = result.scalar_one_or_none()
        if not membership:
            return None
        
        membership.role = role
        await self.db.commit()
        await self.db.refresh(membership)
        return membership

    async def leave_band(self, band_id: UUID, user_id: UUID) -> bool:
        """Remove user from band"""
        result = await self.db.execute(
            select(Membership).where(
                and_(Membership.band_id == band_id, Membership.user_id == user_id)
            )
        )
        membership = result.scalar_one_or_none()
        if not membership:
            return False
        
        await self.db.delete(membership)
        await self.db.commit()
        return True

    # Venue operations
    async def create_venue(self, venue_data: VenueCreate, band_id: UUID) -> Venue:
        """Create a new venue"""
        db_venue = Venue(
            band_id=band_id,
            name=venue_data.name,
            address=venue_data.address,
            notes=venue_data.notes
        )
        self.db.add(db_venue)
        await self.db.commit()
        await self.db.refresh(db_venue)
        return db_venue

    async def get_venue(self, venue_id: UUID) -> Optional[Venue]:
        """Get venue by ID"""
        result = await self.db.execute(
            select(Venue).where(Venue.id == venue_id)
        )
        return result.scalar_one_or_none()

    async def get_band_venues(self, band_id: UUID) -> List[Venue]:
        """Get all venues for a band"""
        result = await self.db.execute(
            select(Venue)
            .where(Venue.band_id == band_id)
            .order_by(Venue.name)
        )
        return result.scalars().all()

    async def update_venue(self, venue_id: UUID, venue_data: dict) -> Optional[Venue]:
        """Update venue information"""
        venue = await self.get_venue(venue_id)
        if not venue:
            return None
        
        for key, value in venue_data.items():
            if hasattr(venue, key):
                setattr(venue, key, value)
        
        await self.db.commit()
        await self.db.refresh(venue)
        return venue

    async def delete_venue(self, venue_id: UUID) -> bool:
        """Delete venue"""
        venue = await self.get_venue(venue_id)
        if not venue:
            return False
        
        await self.db.delete(venue)
        await self.db.commit()
        return True

    # Event operations
    async def create_event(self, event_data: EventCreate, band_id: UUID, created_by: UUID) -> Event:
        """Create a new event"""
        db_event = Event(
            band_id=band_id,
            type=event_data.type,
            title=event_data.title,
            starts_at_utc=event_data.starts_at_utc,
            ends_at_utc=event_data.ends_at_utc,
            venue_id=event_data.venue_id,
            notes=event_data.notes,
            created_by=created_by
        )
        self.db.add(db_event)
        await self.db.commit()
        await self.db.refresh(db_event)
        return db_event

    async def get_event(self, event_id: UUID) -> Optional[Event]:
        """Get event by ID with venue information"""
        result = await self.db.execute(
            select(Event)
            .options(selectinload(Event.venue))
            .where(Event.id == event_id)
        )
        return result.scalar_one_or_none()

    async def get_band_events(self, band_id: UUID) -> List[Event]:
        """Get all events for a band"""
        result = await self.db.execute(
            select(Event)
            .options(selectinload(Event.venue))
            .where(Event.band_id == band_id)
            .order_by(Event.starts_at_utc)
        )
        return result.scalars().all()

    async def update_event(self, event_id: UUID, event_data: EventUpdate) -> Optional[Event]:
        """Update event information"""
        event = await self.get_event(event_id)
        if not event:
            return None
        
        update_data = event_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(event, key):
                setattr(event, key, value)
        
        await self.db.commit()
        await self.db.refresh(event)
        return event

    async def delete_event(self, event_id: UUID) -> bool:
        """Delete event"""
        event = await self.get_event(event_id)
        if not event:
            return False
        
        await self.db.delete(event)
        await self.db.commit()
        return True

    # Utility methods
    async def check_user_in_band(self, user_id: UUID, band_id: UUID) -> bool:
        """Check if user is a member of the band"""
        result = await self.db.execute(
            select(Membership).where(
                and_(Membership.user_id == user_id, Membership.band_id == band_id)
            )
        )
        return result.scalar_one_or_none() is not None

    async def check_user_is_band_leader(self, user_id: UUID, band_id: UUID) -> bool:
        """Check if user is a leader of the band"""
        result = await self.db.execute(
            select(Membership).where(
                and_(
                    Membership.user_id == user_id,
                    Membership.band_id == band_id,
                    Membership.role == BandRole.LEADER
                )
            )
        )
        return result.scalar_one_or_none() is not None
