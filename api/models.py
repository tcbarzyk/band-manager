"""
SQLAlchemy models for the Band Manager application.
These models define the database schema and relationships.
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.sql import func
from sqlalchemy import TypeDecorator, CHAR
from sqlalchemy.dialects import postgresql
import enum
import uuid

class Base(DeclarativeBase):
    pass

# UUID type that works with both PostgreSQL and SQLite
class GUID(TypeDecorator):
    """Platform-independent GUID type.
    
    Uses PostgreSQL's UUID type, otherwise uses CHAR(36), storing as string.
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(postgresql.UUID())
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return str(uuid.UUID(value))
            else:
                return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value)
            return value

# Enums
class BandRole(str, enum.Enum):
    LEADER = "leader"
    MEMBER = "member"

class EventType(str, enum.Enum):
    REHEARSAL = "rehearsal"
    GIG = "gig"

class EventStatus(str, enum.Enum):
    PLANNED = "planned"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"

class Profile(Base):
    """User profiles table"""
    __tablename__ = "profiles"
    
    user_id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    display_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    # Relationships
    created_bands = relationship("Band", back_populates="creator")
    memberships = relationship("Membership", back_populates="user")
    created_events = relationship("Event", back_populates="creator")

class Band(Base):
    """Bands table"""
    __tablename__ = "bands"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String(64), nullable=False)
    timezone = Column(String(50), nullable=False, default="America/New_York")
    join_code = Column(String(20), nullable=False, unique=True)
    created_by = Column(GUID(), ForeignKey("profiles.user_id"), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    # Relationships
    creator = relationship("Profile", back_populates="created_bands")
    memberships = relationship("Membership", back_populates="band", cascade="all, delete-orphan")
    venues = relationship("Venue", back_populates="band", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="band", cascade="all, delete-orphan")

class Membership(Base):
    """Memberships junction table - links users to bands with roles"""
    __tablename__ = "memberships"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    band_id = Column(GUID(), ForeignKey("bands.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(GUID(), ForeignKey("profiles.user_id", ondelete="CASCADE"), nullable=False)
    role = Column(SQLEnum(BandRole), nullable=False, default=BandRole.MEMBER)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    # Relationships
    band = relationship("Band", back_populates="memberships")
    user = relationship("Profile", back_populates="memberships")
    
    # Unique constraint
    __table_args__ = (
        {"schema": None},
    )

class Venue(Base):
    """Venues table"""
    __tablename__ = "venues"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    band_id = Column(GUID(), ForeignKey("bands.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(120), nullable=False)
    address = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    band = relationship("Band", back_populates="venues")
    events = relationship("Event", back_populates="venue")

class Event(Base):
    """Events table"""
    __tablename__ = "events"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    band_id = Column(GUID(), ForeignKey("bands.id", ondelete="CASCADE"), nullable=False)
    type = Column(SQLEnum(EventType), nullable=False)
    status = Column(SQLEnum(EventStatus), nullable=False, default=EventStatus.PLANNED)
    title = Column(String(120), nullable=False)
    starts_at_utc = Column(DateTime(timezone=True), nullable=False)
    ends_at_utc = Column(DateTime(timezone=True), nullable=False)
    venue_id = Column(GUID(), ForeignKey("venues.id", ondelete="SET NULL"), nullable=True)
    notes = Column(Text, nullable=True)
    created_by = Column(GUID(), ForeignKey("profiles.user_id"), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    # Relationships
    band = relationship("Band", back_populates="events")
    venue = relationship("Venue", back_populates="events")
    creator = relationship("Profile", back_populates="created_events")
