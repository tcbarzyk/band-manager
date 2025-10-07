"""
FastAPI application for Band Manager with SQLAlchemy integration.
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
import uuid

from database import get_db, init_db, close_db
from repository import BandRepository
from schemas import (
    ProfileCreate, ProfileResponse,
    BandCreate, BandResponse,
    VenueCreate, VenueResponse,
    EventCreate, EventResponse, EventUpdate,
    MembershipResponse
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

# Profile endpoints
@app.post("/profiles", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    profile_data: ProfileCreate,
    repo: BandRepository = Depends(get_repository)
):
    """Create a new user profile"""
    # In a real app, you'd get user_id from authentication token
    user_id = uuid.uuid4()  # Mock user ID for demo
    
    try:
        # Check if email already exists
        existing = await repo.get_profile_by_email(profile_data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        profile = await repo.create_profile(profile_data, user_id)
        return profile
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create profile: {str(e)}"
        )

@app.get("/profiles/{user_id}", response_model=ProfileResponse)
async def get_profile(
    user_id: UUID,
    repo: BandRepository = Depends(get_repository)
):
    """Get user profile by ID"""
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
    repo: BandRepository = Depends(get_repository)
):
    """Create a new band"""
    # In a real app, you'd get user_id from authentication token
    created_by = uuid.uuid4()  # Mock user ID for demo
    
    try:
        band = await repo.create_band(band_data, created_by)
        return band
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create band: {str(e)}"
        )

@app.get("/bands/{band_id}", response_model=BandResponse)
async def get_band(
    band_id: UUID,
    repo: BandRepository = Depends(get_repository)
):
    """Get band by ID"""
    band = await repo.get_band(band_id)
    if not band:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Band not found"
        )
    return band

@app.get("/profiles/{user_id}/bands", response_model=List[BandResponse])
async def get_profile_bands(
    user_id: UUID,
    repo: BandRepository = Depends(get_repository)
):
    """Get all bands for a profile/user"""
    bands = await repo.get_user_bands(user_id)
    return bands

@app.post("/bands/join/{join_code}", response_model=MembershipResponse)
async def join_band(
    join_code: str,
    repo: BandRepository = Depends(get_repository)
):
    """Join a band using join code"""
    # In a real app, you'd get user_id from authentication token
    user_id = uuid.uuid4()  # Mock user ID for demo
    
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
    repo: BandRepository = Depends(get_repository)
):
    """Get all members of a band"""
    members = await repo.get_band_members(band_id)
    return members

# Venue endpoints
@app.post("/bands/{band_id}/venues", response_model=VenueResponse, status_code=status.HTTP_201_CREATED)
async def create_venue(
    band_id: UUID,
    venue_data: VenueCreate,
    repo: BandRepository = Depends(get_repository)
):
    """Create a new venue for a band"""
    # In a real app, check if user has permission to create venues for this band
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
    repo: BandRepository = Depends(get_repository)
):
    """Get all venues for a band"""
    venues = await repo.get_band_venues(band_id)
    return venues

@app.get("/venues/{venue_id}", response_model=VenueResponse)
async def get_venue(
    venue_id: UUID,
    repo: BandRepository = Depends(get_repository)
):
    """Get venue by ID"""
    venue = await repo.get_venue(venue_id)
    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue not found"
        )
    return venue

@app.delete("/venues/{venue_id}")
async def delete_venue(
    venue_id: UUID,
    repo: BandRepository = Depends(get_repository)
):
    """Delete a venue"""
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
    repo: BandRepository = Depends(get_repository)
):
    """Create a new event for a band"""
    # In a real app, you'd get user_id from authentication token
    created_by = uuid.uuid4()  # Mock user ID for demo
    
    try:
        event = await repo.create_event(event_data, band_id, created_by)
        return event
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create event: {str(e)}"
        )

@app.get("/bands/{band_id}/events", response_model=List[EventResponse])
async def get_band_events(
    band_id: UUID,
    repo: BandRepository = Depends(get_repository)
):
    """Get all events for a band"""
    events = await repo.get_band_events(band_id)
    return events

@app.get("/events/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: UUID,
    repo: BandRepository = Depends(get_repository)
):
    """Get event by ID"""
    event = await repo.get_event(event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    return event

@app.put("/events/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: UUID,
    event_data: EventUpdate,
    repo: BandRepository = Depends(get_repository)
):
    """Update an event"""
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
    repo: BandRepository = Depends(get_repository)
):
    """Delete an event"""
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