"""
FastAPI application for Band Manager with SQLAlchemy integration and Supabase Auth.
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from uuid import UUID
import uuid

from database import get_db, init_db, close_db
from repository import BandRepository
from auth import get_current_user, get_current_user_optional
from schemas import (
    ProfileCreate, ProfileResponse, ProfileUpdate,
    BandCreate, BandResponse,
    VenueCreate, VenueResponse,
    EventCreate, EventResponse, EventUpdate,
    MembershipResponse, UserInfo
)

app = FastAPI(
    title="Band Manager API",
    description="API for managing bands, events, and venues",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Application lifecycle events
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await init_db()
    print("Application started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up database connections on shutdown"""
    await close_db()
    print("Application shutdown complete")

# Dependency injection
async def get_repository(db: AsyncSession = Depends(get_db)):
    """Get repository instance with database session"""
    return BandRepository(db)

# Health check endpoint
@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Band Manager API is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {"status": "healthy", "service": "band-manager-api"}

# Authentication endpoints
@app.get("/auth/me", response_model=ProfileResponse)
async def get_current_user_profile(
    current_user: Dict[str, Any] = Depends(get_current_user),
    repo: BandRepository = Depends(get_repository)
):
    """Get current authenticated user's profile"""
    user_id = UUID(current_user["user_id"])
    
    # Ensure profile exists for this user
    profile = await repo.ensure_profile_exists(
        user_id=user_id,
        email=current_user["email"]
    )
    
    return profile

@app.put("/auth/me", response_model=ProfileResponse)
async def update_current_user_profile(
    profile_update: ProfileUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    repo: BandRepository = Depends(get_repository)
):
    """Update current authenticated user's profile"""
    user_id = UUID(current_user["user_id"])
    
    # Convert Pydantic model to dict, excluding None values
    update_data = profile_update.model_dump(exclude_none=True)
    
    profile = await repo.update_profile(user_id, update_data)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    return profile

# Profile endpoints (now authentication-protected)
@app.post("/profiles", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    profile_data: ProfileCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    repo: BandRepository = Depends(get_repository)
):
    """Create a new user profile (for current authenticated user)"""
    user_id = UUID(current_user["user_id"])
    
    try:
        # Check if profile already exists for this user
        existing = await repo.get_profile(user_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Profile already exists for this user"
            )
        
        # Check if email already exists
        existing_email = await repo.get_profile_by_email(profile_data.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Ensure the email matches the authenticated user's email
        if profile_data.email != current_user["email"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email must match authenticated user's email"
            )
        
        profile = await repo.create_profile(profile_data, user_id)
        return profile
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create profile: {str(e)}"
        )

@app.get("/profiles/{user_id}", response_model=ProfileResponse)
async def get_profile(
    user_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user),
    repo: BandRepository = Depends(get_repository)
):
    """Get user profile by ID (authentication required)"""
    profile = await repo.get_profile(user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    return profile

# Band endpoints
@app.post("/bands", response_model=BandResponse, status_code=status.HTTP_201_CREATED)
async def create_band(
    band_data: BandCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    repo: BandRepository = Depends(get_repository)
):
    """Create a new band"""
    user_id = UUID(current_user["user_id"])
    
    try:
        # Ensure user has a profile
        await repo.ensure_profile_exists(
            user_id=user_id,
            email=current_user["email"]
        )
        
        band = await repo.create_band(band_data, user_id)
        return band
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create band: {str(e)}"
        )

@app.get("/bands/{band_id}", response_model=BandResponse)
async def get_band(
    band_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user),
    repo: BandRepository = Depends(get_repository)
):
    """Get band by ID (must be a member)"""
    user_id = UUID(current_user["user_id"])
    
    band = await repo.get_band(band_id)
    if not band:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Band not found"
        )
    
    # Check if user is a member of this band
    is_member = await repo.is_band_member(band_id, user_id)
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You are not a member of this band"
        )
    
    return band

@app.get("/my/bands", response_model=List[BandResponse])
async def get_my_bands(
    current_user: Dict[str, Any] = Depends(get_current_user),
    repo: BandRepository = Depends(get_repository)
):
    """Get current user's bands"""
    user_id = UUID(current_user["user_id"])
    bands = await repo.get_user_bands(user_id)
    return bands

@app.get("/profiles/{user_id}/bands", response_model=List[BandResponse])
async def get_profile_bands(
    user_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user),
    repo: BandRepository = Depends(get_repository)
):
    """Get all bands for a profile/user"""
    bands = await repo.get_user_bands(user_id)
    return bands

@app.post("/bands/join/{join_code}", response_model=MembershipResponse)
async def join_band(
    join_code: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    repo: BandRepository = Depends(get_repository)
):
    """Join a band using join code"""
    user_id = UUID(current_user["user_id"])
    
    # Ensure user has a profile
    await repo.ensure_profile_exists(
        user_id=user_id,
        email=current_user["email"]
    )
    
    membership = await repo.join_band(join_code, user_id)
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid join code or already a member"
        )
    return membership

@app.get("/bands/{band_id}/members", response_model=List[MembershipResponse])
async def get_band_members(
    band_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user),
    repo: BandRepository = Depends(get_repository)
):
    """Get all members of a band (must be a member to view)"""
    user_id = UUID(current_user["user_id"])
    
    # Check if user is a member of this band
    is_member = await repo.is_band_member(band_id, user_id)
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You are not a member of this band"
        )
    
    members = await repo.get_band_members(band_id)
    return members

# Venue endpoints
@app.post("/bands/{band_id}/venues", response_model=VenueResponse, status_code=status.HTTP_201_CREATED)
async def create_venue(
    band_id: UUID,
    venue_data: VenueCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    repo: BandRepository = Depends(get_repository)
):
    """Create a new venue for a band (must be a member)"""
    user_id = UUID(current_user["user_id"])
    
    # Check if user is a member of this band
    is_member = await repo.is_band_member(band_id, user_id)
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You are not a member of this band"
        )
    
    try:
        venue = await repo.create_venue(venue_data, band_id)
        return venue
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create venue: {str(e)}"
        )

@app.get("/bands/{band_id}/venues", response_model=List[VenueResponse])
async def get_band_venues(
    band_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user),
    repo: BandRepository = Depends(get_repository)
):
    """Get all venues for a band (must be a member)"""
    user_id = UUID(current_user["user_id"])
    
    # Check if user is a member of this band
    is_member = await repo.is_band_member(band_id, user_id)
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You are not a member of this band"
        )
    
    venues = await repo.get_band_venues(band_id)
    return venues

@app.get("/venues/{venue_id}", response_model=VenueResponse)
async def get_venue(
    venue_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user),
    repo: BandRepository = Depends(get_repository)
):
    """Get venue by ID (must be a member of the band that owns it)"""
    user_id = UUID(current_user["user_id"])
    
    venue = await repo.get_venue(venue_id)
    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue not found"
        )
    
    # Check if user is a member of the band that owns this venue
    is_member = await repo.is_band_member(venue.band_id, user_id)
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You are not a member of the band that owns this venue"
        )
    
    return venue

@app.delete("/venues/{venue_id}")
async def delete_venue(
    venue_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user),
    repo: BandRepository = Depends(get_repository)
):
    """Delete a venue (must be a member of the band)"""
    user_id = UUID(current_user["user_id"])
    
    venue = await repo.get_venue(venue_id)
    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue not found"
        )
    
    # Check if user is a member of the band that owns this venue
    is_member = await repo.is_band_member(venue.band_id, user_id)
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You are not a member of the band that owns this venue"
        )
    
    success = await repo.delete_venue(venue_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue not found"
        )
    return {"message": "Venue deleted successfully"}

# Event endpoints
@app.post("/bands/{band_id}/events", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    band_id: UUID,
    event_data: EventCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    repo: BandRepository = Depends(get_repository)
):
    """Create a new event for a band (must be a member)"""
    user_id = UUID(current_user["user_id"])
    
    # Check if user is a member of this band
    is_member = await repo.is_band_member(band_id, user_id)
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You are not a member of this band"
        )
    
    try:
        event = await repo.create_event(event_data, band_id, user_id)
        return event
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create event: {str(e)}"
        )

@app.get("/bands/{band_id}/events", response_model=List[EventResponse])
async def get_band_events(
    band_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user),
    repo: BandRepository = Depends(get_repository)
):
    """Get all events for a band (must be a member)"""
    user_id = UUID(current_user["user_id"])
    
    # Check if user is a member of this band
    is_member = await repo.is_band_member(band_id, user_id)
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You are not a member of this band"
        )
    
    events = await repo.get_band_events(band_id)
    return events

@app.get("/events/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user),
    repo: BandRepository = Depends(get_repository)
):
    """Get event by ID (must be a member of the band)"""
    user_id = UUID(current_user["user_id"])
    
    event = await repo.get_event(event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Check if user is a member of the band that owns this event
    is_member = await repo.is_band_member(event.band_id, user_id)
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You are not a member of the band that owns this event"
        )
    
    return event

@app.put("/events/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: UUID,
    event_data: EventUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    repo: BandRepository = Depends(get_repository)
):
    """Update an event (must be a member of the band)"""
    user_id = UUID(current_user["user_id"])
    
    # Get the event to check band membership
    existing_event = await repo.get_event(event_id)
    if not existing_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Check if user is a member of the band that owns this event
    is_member = await repo.is_band_member(existing_event.band_id, user_id)
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You are not a member of the band that owns this event"
        )
    
    event = await repo.update_event(event_id, event_data)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    return event

@app.delete("/events/{event_id}")
async def delete_event(
    event_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user),
    repo: BandRepository = Depends(get_repository)
):
    """Delete an event (must be a member of the band)"""
    user_id = UUID(current_user["user_id"])
    
    # Get the event to check band membership
    existing_event = await repo.get_event(event_id)
    if not existing_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Check if user is a member of the band that owns this event
    is_member = await repo.is_band_member(existing_event.band_id, user_id)
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You are not a member of the band that owns this event"
        )
    
    success = await repo.delete_event(event_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    return {"message": "Event deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)