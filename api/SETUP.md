# Band Manager API Setup with SQLAlchemy and Supabase

This guide walks you through setting up the Band Manager API with SQLAlchemy ORM and Supabase PostgreSQL database.

## Prerequisites

1. **Python 3.8+** installed on your system
2. **Supabase account** (free tier available at [supabase.com](https://supabase.com))
3. **Git** (for version control)

## Quick Start

### 1. Set Up Supabase Project

1. Go to [supabase.com](https://supabase.com) and create a new project
2. Wait 2-3 minutes for database initialization
3. Go to **Settings > Database** and copy your connection string
4. Go to **Settings > API** and copy your project URL and anon key

### 2. Configure Environment

Create a `.env` file in the `api/` directory:

```bash
# Copy from .env.example and fill in your values
cp .env.example .env
```

Edit `.env` with your Supabase credentials:

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here
DATABASE_URL=postgresql://postgres:your-password@db.your-project-id.supabase.co:5432/postgres
```

### 3. Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

### 4. Create Database Schema

Run the SQL schema in your Supabase SQL Editor:

```sql
-- Create enums
CREATE TYPE band_role AS ENUM ('leader', 'member');
CREATE TYPE event_type AS ENUM ('rehearsal', 'gig');
CREATE TYPE event_status AS ENUM ('planned', 'confirmed', 'cancelled');

-- Create profiles table
CREATE TABLE profiles (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    display_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create bands table
CREATE TABLE bands (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(64) NOT NULL,
    timezone VARCHAR(50) NOT NULL DEFAULT 'America/New_York',
    join_code VARCHAR(20) NOT NULL UNIQUE,
    created_by UUID NOT NULL REFERENCES profiles(user_id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create memberships table
CREATE TABLE memberships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    band_id UUID NOT NULL REFERENCES bands(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES profiles(user_id) ON DELETE CASCADE,
    role band_role NOT NULL DEFAULT 'member',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(band_id, user_id)
);

-- Create venues table
CREATE TABLE venues (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    band_id UUID NOT NULL REFERENCES bands(id) ON DELETE CASCADE,
    name VARCHAR(120) NOT NULL,
    address TEXT,
    notes TEXT
);

-- Create events table
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    band_id UUID NOT NULL REFERENCES bands(id) ON DELETE CASCADE,
    type event_type NOT NULL,
    status event_status NOT NULL DEFAULT 'planned',
    title VARCHAR(120) NOT NULL,
    starts_at_utc TIMESTAMPTZ NOT NULL,
    ends_at_utc TIMESTAMPTZ NOT NULL,
    venue_id UUID REFERENCES venues(id) ON DELETE SET NULL,
    notes TEXT,
    created_by UUID NOT NULL REFERENCES profiles(user_id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT events_time_check CHECK (ends_at_utc > starts_at_utc)
);

-- Create indexes for performance
CREATE INDEX idx_bands_name ON bands(name);
CREATE INDEX idx_memberships_user ON memberships(user_id);
CREATE INDEX idx_memberships_band ON memberships(band_id);
CREATE INDEX idx_venues_band ON venues(band_id);
CREATE INDEX idx_events_band_time ON events(band_id, starts_at_utc);
CREATE INDEX idx_events_time ON events(starts_at_utc);
```

### 5. Test Your Setup

```bash
# Test database connection and basic operations
python test_db.py
```

### 6. Start the API Server

```bash
# Start the development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Visit `http://localhost:8000/docs` to see the interactive API documentation.

## Project Structure

```
api/
├── main.py              # FastAPI application and routes
├── models.py            # SQLAlchemy database models
├── schemas.py           # Pydantic schemas for validation
├── database.py          # Database configuration and connection
├── repository.py        # Database operations and business logic
├── test_db.py          # Database testing script
├── requirements.txt     # Python dependencies
├── .env.example        # Environment variables template
└── .env                # Your environment variables (create this)
```

## Key Features

### 🚀 **Modern Tech Stack**
- **FastAPI**: High-performance async web framework
- **SQLAlchemy 2.0**: Modern Python ORM with async support
- **Supabase**: Managed PostgreSQL with additional features
- **Pydantic**: Data validation and serialization

### 🔄 **Async Everything**
- Async database connections with connection pooling
- Non-blocking I/O operations
- High concurrency support

### 🛡️ **Type Safety**
- Full type hints throughout the codebase
- Pydantic models for request/response validation
- SQLAlchemy models with proper type annotations

### 🏗️ **Clean Architecture**
- **Repository Pattern**: Separates database logic from API logic
- **Dependency Injection**: Clean separation of concerns
- **Schema Validation**: Automatic request/response validation

## API Endpoints

### Profiles
- `POST /profiles` - Create user profile
- `GET /profiles/{user_id}` - Get user profile

### Bands
- `POST /bands` - Create new band
- `GET /bands/{band_id}` - Get band details
- `GET /users/{user_id}/bands` - Get user's bands
- `POST /bands/join/{join_code}` - Join band with code
- `GET /bands/{band_id}/members` - Get band members

### Venues
- `POST /bands/{band_id}/venues` - Create venue
- `GET /bands/{band_id}/venues` - Get band venues
- `GET /venues/{venue_id}` - Get venue details
- `DELETE /venues/{venue_id}` - Delete venue

### Events
- `POST /bands/{band_id}/events` - Create event
- `GET /bands/{band_id}/events` - Get band events
- `GET /events/{event_id}` - Get event details
- `PUT /events/{event_id}` - Update event
- `DELETE /events/{event_id}` - Delete event

## How SQLAlchemy Integration Works

### 1. **Database Models** (`models.py`)
- Define table structure using SQLAlchemy declarative syntax
- Relationships between tables (bands → events, users → memberships)
- Type-safe column definitions with validation

### 2. **Database Session Management** (`database.py`)
- Async session factory for connection pooling
- Automatic transaction management
- Dependency injection for FastAPI routes

### 3. **Repository Pattern** (`repository.py`)
- Encapsulates all database operations
- Business logic separated from web layer
- Reusable database queries with proper error handling

### 4. **Schema Validation** (`schemas.py`)
- Pydantic models for API input/output
- Automatic data validation and serialization
- Separate from database models for flexibility

### 5. **FastAPI Integration** (`main.py`)
- Dependency injection for database sessions
- Error handling and HTTP response codes
- Auto-generated OpenAPI documentation

## Advantages of SQLAlchemy over Raw SQL

1. **Type Safety**: Catch errors at development time
2. **Relationship Management**: Automatic joins and eager loading
3. **Query Building**: Programmatic, reusable query construction
4. **Migration Support**: Database schema versioning with Alembic
5. **Connection Pooling**: Efficient database connection management
6. **Cross-Database**: Works with PostgreSQL, MySQL, SQLite, etc.

## Production Considerations

1. **Environment Variables**: Never commit `.env` to version control
2. **Connection Pooling**: Configure appropriate pool sizes
3. **Migrations**: Use Alembic for schema changes
4. **Authentication**: Add proper user authentication
5. **Rate Limiting**: Implement API rate limiting
6. **Monitoring**: Add logging and monitoring
7. **Security**: Configure CORS properly for production

## Troubleshooting

### Database Connection Issues
- Verify your Supabase credentials
- Check if your IP is whitelisted in Supabase
- Ensure DATABASE_URL format is correct

### Import Errors
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check Python path if running from different directories

### Migration Issues
- Initialize Alembic: `alembic init alembic`
- Generate migrations: `alembic revision --autogenerate -m "Initial migration"`
- Apply migrations: `alembic upgrade head`

## Next Steps

1. **Add Authentication**: Integrate with Supabase Auth or JWT
2. **Add Tests**: Unit and integration tests
3. **Add Caching**: Redis for session management
4. **Add File Upload**: For band photos, setlists, etc.
5. **Add Real-time**: WebSocket notifications for events
6. **Deploy**: To Heroku, Railway, or other cloud platforms
