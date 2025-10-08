# Band Manager Backend API Documentation

## 📋 Table of Contents

1. [Overview](#overview)
2. [Technology Stack](#technology-stack)
3. [Architecture](#architecture)
4. [Authentication System](#authentication-system)
5. [Database Design](#database-design)
6. [API Endpoints](#api-endpoints)
7. [Setup Instructions](#setup-instructions)
8. [Testing](#testing)
9. [Deployment](#deployment)
10. [Manual Testing](#manual-testing)

---

## 🎯 Overview

The Band Manager Backend API is a RESTful web service built with FastAPI that provides comprehensive band and music management functionality. It features secure user authentication via Supabase, role-based access control, and a robust data model for managing bands, venues, events, and user profiles.

### Key Features

- **Secure Authentication**: JWT-based authentication with Supabase integration
- **Role-Based Access Control**: Band membership and permission management
- **RESTful API Design**: Clean, intuitive endpoints following REST principles
- **Async/Await Support**: High-performance asynchronous operations
- **Database Migrations**: Automated schema management with Alembic
- **Comprehensive Testing**: Unit, integration, and API tests with pytest
- **Type Safety**: Full Python type hints with Pydantic models

---

## 🛠 Technology Stack

### Core Framework
- **[FastAPI](https://fastapi.tiangolo.com/)** (v0.118.0) - Modern, fast web framework for building APIs
- **[Python](https://python.org)** (3.13+) - Programming language
- **[Uvicorn](https://uvicorn.org/)** (v0.37.0) - ASGI server for running FastAPI

### Database & ORM
- **[PostgreSQL](https://postgresql.org/)** - Primary database (via Supabase)
- **[SQLAlchemy](https://sqlalchemy.org/)** (v2.0.35) - Modern async ORM
- **[Alembic](https://alembic.sqlalchemy.org/)** (v1.13.1) - Database migration tool
- **[asyncpg](https://magicstack.github.io/asyncpg/)** (v0.30.0) - PostgreSQL async driver

### Authentication & Security
- **[Supabase](https://supabase.com/)** (v2.7.4) - Authentication and database backend
- **[PyJWT](https://pyjwt.readthedocs.io/)** (v2.10.1) - JWT token handling
- **[python-jose](https://python-jose.readthedocs.io/)** (v3.5.0) - JSON Web Token utilities

### Data Validation & Serialization
- **[Pydantic](https://docs.pydantic.dev/)** (v2.11.10) - Data validation using Python type annotations
- **[pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)** (v2.11.0) - Settings management

### Testing
- **[pytest](https://pytest.org/)** (v7.4.3) - Testing framework
- **[pytest-asyncio](https://pytest-asyncio.readthedocs.io/)** (v0.21.1) - Async test support
- **[pytest-mock](https://pytest-mock.readthedocs.io/)** (v3.12.0) - Mock utilities
- **[factory-boy](https://factoryboy.readthedocs.io/)** (v3.3.1) - Test data generation
- **[Faker](https://faker.readthedocs.io/)** (v37.8.0) - Fake data generation

### Development & Utilities
- **[python-dotenv](https://python-dotenv.readthedocs.io/)** (v1.1.1) - Environment variable management
- **[requests](https://requests.readthedocs.io/)** (v2.32.5) - HTTP library for testing

---

## 🏗 Architecture

### Project Structure

```
api/
├── main.py                 # FastAPI application and route definitions
├── models.py              # SQLAlchemy database models
├── schemas.py             # Pydantic request/response schemas
├── database.py            # Database configuration and connection
├── repository.py          # Data access layer with business logic
├── auth.py               # Supabase authentication integration
├── requirements.txt      # Python dependencies
├── pyproject.toml       # Project configuration and test settings
├── alembic.ini          # Alembic migration configuration
├── alembic/             # Database migration files
│   ├── env.py
│   └── versions/
└── tests/               # Test suite
    ├── conftest.py      # Test configuration and fixtures
    ├── factories.py     # Test data factories
    ├── test_auth.py     # Authentication tests
    ├── test_api.py      # API endpoint tests
    └── test_repository.py # Repository layer tests
```

### Application Layers

1. **API Layer** (`main.py`)
   - FastAPI route handlers
   - Request/response handling
   - Authentication middleware integration

2. **Authentication Layer** (`auth.py`)
   - JWT token validation
   - Supabase integration
   - User context extraction

3. **Schema Layer** (`schemas.py`)
   - Pydantic models for data validation
   - Request/response serialization
   - Type safety enforcement

4. **Business Logic Layer** (`repository.py`)
   - Data access operations
   - Business rule enforcement
   - Database transaction management

5. **Data Layer** (`models.py`, `database.py`)
   - SQLAlchemy ORM models
   - Database configuration
   - Connection management

---

## 🔐 Authentication System

### Supabase Integration

The application uses **Supabase** for user authentication and authorization:

- **JWT Tokens**: Supabase-issued JWT tokens for API authentication
- **User Management**: User registration, login, and profile management via Supabase
- **Secure Communication**: All API endpoints require valid JWT tokens
- **Role-Based Access**: Band membership and role-based permissions

### Authentication Flow

1. **User Registration/Login**: Users authenticate via Supabase (web UI or API)
2. **JWT Token Generation**: Supabase issues JWT tokens upon successful authentication
3. **Token Validation**: API validates JWT tokens using Supabase's public key
4. **User Context**: Authenticated user information extracted from valid tokens
5. **Authorization**: Band membership and permissions checked for protected operations

### Implementation Details

```python
# FastAPI Dependencies
@app.dependency
async def get_current_user(authorization: str = Header(None)) -> dict:
    """Extract and validate user from JWT token"""
    
@app.dependency  
async def get_current_user_optional(authorization: str = Header(None)) -> dict | None:
    """Optional authentication for endpoints that support both auth modes"""
```

### Environment Variables

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_JWT_SECRET=your-jwt-secret
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/db
```

---

## 💾 Database Design

### Data Models

#### 1. **Profile** - User Profiles
```python
class Profile(Base):
    id: UUID (Primary Key)
    user_id: UUID (Supabase User ID)
    email: str
    first_name: str
    last_name: str
    role: str
    created_at: datetime
    updated_at: datetime
```

#### 2. **Band** - Musical Groups
```python
class Band(Base):
    id: UUID (Primary Key)
    name: str
    genre: str
    description: str (Optional)
    created_by: UUID (Foreign Key -> Profile)
    created_at: datetime
    updated_at: datetime
```

#### 3. **BandMember** - Band Membership
```python
class BandMember(Base):
    id: UUID (Primary Key)
    band_id: UUID (Foreign Key -> Band)
    user_id: UUID (Foreign Key -> Profile)
    role: str
    joined_at: datetime
```

#### 4. **Venue** - Performance Locations
```python
class Venue(Base):
    id: UUID (Primary Key)
    name: str
    address: str
    city: str
    state: str
    zip_code: str (Optional)
    created_by: UUID (Foreign Key -> Profile)
    created_at: datetime
    updated_at: datetime
```

#### 5. **Event** - Band Events/Gigs
```python
class Event(Base):
    id: UUID (Primary Key)
    title: str
    description: str (Optional)
    band_id: UUID (Foreign Key -> Band)
    venue_id: UUID (Foreign Key -> Venue)
    event_date: datetime
    start_time: time (Optional)
    end_time: time (Optional)
    created_by: UUID (Foreign Key -> Profile)
    created_at: datetime
    updated_at: datetime
```

### Database Migrations

The application uses **Alembic** for database schema management:

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Check current migration status
alembic current
```

---

## 🔌 API Endpoints

### Authentication Required

All endpoints require a valid JWT token in the `Authorization` header:
```
Authorization: Bearer <jwt_token>
```

### Utility Endpoints

| Method | Endpoint | Description | Authorization |
|--------|----------|-------------|---------------|
| `GET` | `/` | Health check - API status | None |
| `GET` | `/health` | Detailed health check | None |

### Authentication & Profile Management

| Method | Endpoint | Description | Authorization |
|--------|----------|-------------|---------------|
| `GET` | `/auth/me` | Get current user's profile | Authenticated |
| `PUT` | `/auth/me` | Update current user's profile | Authenticated |
| `POST` | `/profiles` | Create user profile | Authenticated |
| `GET` | `/profiles/{user_id}` | Get specific user profile | Authenticated |
| `GET` | `/profiles/{user_id}/bands` | Get bands for a specific user | Authenticated |

### Band Management

| Method | Endpoint | Description | Authorization |
|--------|----------|-------------|---------------|
| `GET` | `/my/bands` | Get current user's bands | Authenticated |
| `POST` | `/bands` | Create new band | Authenticated |
| `GET` | `/bands/{band_id}` | Get band details | Band member |
| `GET` | `/bands/{band_id}/members` | Get band members | Band member |
| `POST` | `/bands/join/{join_code}` | Join band with code | Authenticated |

### Venue Management

| Method | Endpoint | Description | Authorization |
|--------|----------|-------------|---------------|
| `POST` | `/bands/{band_id}/venues` | Create venue for band | Band member |
| `GET` | `/bands/{band_id}/venues` | Get venues for band | Band member |
| `GET` | `/venues/{venue_id}` | Get venue details | Band member (owns venue) |
| `DELETE` | `/venues/{venue_id}` | Delete venue | Band member (owns venue) |

### Event Management

| Method | Endpoint | Description | Authorization |
|--------|----------|-------------|---------------|
| `POST` | `/bands/{band_id}/events` | Create event for band | Band member |
| `GET` | `/bands/{band_id}/events` | Get events for band | Band member |
| `GET` | `/events/{event_id}` | Get event details | Band member (owns event) |
| `PUT` | `/events/{event_id}` | Update event | Band member (owns event) |
| `DELETE` | `/events/{event_id}` | Delete event | Band member (owns event) |

### Response Formats

All API responses follow consistent JSON formats:

**Success Response:**
```json
{
  "id": "uuid",
  "field1": "value1",
  "field2": "value2",
  "created_at": "2025-01-01T12:00:00Z",
  "updated_at": "2025-01-01T12:00:00Z"
}
```

**Error Response:**
```json
{
  "detail": "Error message describing what went wrong"
}
```

**Validation Error:**
```json
{
  "detail": [
    {
      "loc": ["field_name"],
      "msg": "Validation error message",
      "type": "value_error"
    }
  ]
}
```

---

## ⚙️ Setup Instructions

### Prerequisites

- **Python 3.13+**
- **PostgreSQL** (via Supabase)
- **Git**
- **Supabase Account**

### 1. Clone Repository

```bash
git clone <repository-url>
cd band-manager/api
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the `api/` directory:

```bash
# Database Configuration
DATABASE_URL=postgresql+asyncpg://postgres:[password]@db.[project-ref].supabase.co:5432/postgres

# Supabase Configuration
SUPABASE_URL=https://[project-ref].supabase.co
SUPABASE_KEY=[your-anon-key]
SUPABASE_JWT_SECRET=[your-jwt-secret]

# Optional: Development settings
DEBUG=true
LOG_LEVEL=info
```

### 5. Database Setup

```bash
# Run database migrations
alembic upgrade head
```

### 6. Verify Installation

```bash
# Run tests to verify setup
pytest

# Start development server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 7. Access API Documentation

Once the server is running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

---

## 🧪 Testing

### Test Suite Organization

The application includes comprehensive tests organized by functionality:

- **`test_auth.py`** - Authentication and authorization tests
- **`test_api.py`** - API endpoint integration tests  
- **`test_repository.py`** - Data access layer unit tests
- **`conftest.py`** - Test configuration and shared fixtures
- **`factories.py`** - Test data generation factories

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_auth.py

# Run tests with coverage
pytest --cov=. --cov-report=html

# Run only fast tests (exclude slow integration tests)
pytest -m "not slow"
```

### Test Categories

Tests are marked with categories for selective execution:

- **`@pytest.mark.unit`** - Fast unit tests
- **`@pytest.mark.integration`** - Integration tests
- **`@pytest.mark.api`** - API endpoint tests
- **`@pytest.mark.slow`** - Long-running tests

### Test Fixtures

Key testing fixtures available:

```python
# Database and session fixtures
@pytest.fixture
async def async_session() -> AsyncSession

# Authentication fixtures  
@pytest.fixture
def mock_jwt_token() -> str

@pytest.fixture
def authenticated_client() -> TestClient

# Data factory fixtures
@pytest.fixture
def profile_factory() -> ProfileFactory

@pytest.fixture  
def band_factory() -> BandFactory
```

### Test Data Generation

Uses **Factory Boy** for consistent test data:

```python
# Create test profile
profile = ProfileFactory()

# Create test band with specific attributes
band = BandFactory(name="Test Band", genre="Rock")

# Create multiple test objects
profiles = ProfileFactory.create_batch(5)
```

---

## 🚀 Deployment

### Production Environment Variables

```bash
# Production Database
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database

# Supabase Production Settings
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-production-anon-key
SUPABASE_JWT_SECRET=your-production-jwt-secret

# Production Settings
DEBUG=false
LOG_LEVEL=warning
```

### Docker Deployment (Optional)

Create `Dockerfile`:

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Checklist

- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] Security settings enabled
- [ ] SSL/TLS certificates configured
- [ ] Monitoring and logging setup
- [ ] Backup strategy implemented
- [ ] Performance testing completed

---

## 🔧 Manual Testing

### Getting JWT Tokens for Testing

#### Option 1: HTML Token Generator

Use the included `get_token.html` file:

1. Open file in web browser
2. Enter Supabase user credentials
3. Copy the generated JWT token

#### Option 2: Command Line Script

```bash
# Make script executable
chmod +x get_auth_token.sh

# Get token for test user
./get_auth_token.sh
```

### API Testing Script

Use the included `manual_test.py` script:

```bash
# Run comprehensive API tests
python manual_test.py "YOUR_JWT_TOKEN_HERE"
```

### Manual cURL Testing

```bash
# Test health check (no auth required)
curl -X GET "http://localhost:8000/"

# Test getting current user profile
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Test unauthorized access (should return 403)
curl -X GET "http://localhost:8000/auth/me"

# Test profile creation
curl -X POST "http://localhost:8000/profiles" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "first_name": "Test",
    "last_name": "User",
    "role": "admin"
  }'

# Test getting user's bands
curl -X GET "http://localhost:8000/my/bands" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Test band creation
curl -X POST "http://localhost:8000/bands" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Band",
    "genre": "Rock",
    "description": "A test band"
  }'
```

### Postman Collection

Import the included `Band_Manager_API.postman_collection.json` file into Postman for organized API testing.

---

## 📚 Additional Resources

### FastAPI Documentation
- [FastAPI Official Docs](https://fastapi.tiangolo.com/)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)

### Supabase Documentation  
- [Supabase Docs](https://supabase.com/docs)
- [Supabase Auth](https://supabase.com/docs/guides/auth)

### SQLAlchemy Documentation
- [SQLAlchemy 2.0 Docs](https://docs.sqlalchemy.org/en/20/)
- [Async SQLAlchemy](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)

### Testing Resources
- [pytest Documentation](https://docs.pytest.org/)
- [Factory Boy Guide](https://factoryboy.readthedocs.io/)

---

## 🐛 Troubleshooting

### Common Issues

**1. Database Connection Errors**
```bash
# Check DATABASE_URL format
postgresql+asyncpg://user:password@host:port/database

# Verify Supabase connection settings
```

**2. Authentication Failures**
```bash
# Verify JWT secret matches Supabase project
# Check token expiration times
# Ensure proper Authorization header format
```

**3. Migration Issues**
```bash
# Reset migrations if needed
alembic downgrade base
alembic upgrade head
```

**4. Test Failures**
```bash
# Clear test database
pytest --create-db

# Run tests in isolation
pytest --forked
```

### Getting Help

1. Check the API documentation at `/docs` endpoint
2. Review test files for usage examples
3. Verify environment variable configuration
4. Check Supabase project settings and permissions

---

## AI Usage

AI was used to assist in the programming and documentation of this project.

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

*Documentation last updated: January 2025*