# Testing Guide for Band Manager API

This guide explains how to run and write tests for the Band Manager API using a controlled testing environment.

## Overview

Our testing strategy includes:

- **Unit Tests**: Test individual functions and methods in isolation
- **Integration Tests**: Test multiple components working together
- **API Tests**: Test HTTP endpoints end-to-end
- **Isolated Test Database**: Each test uses a clean, in-memory SQLite database
- **Test Fixtures**: Reusable test data and setup
- **Factory Pattern**: Consistent test data generation

## Test Structure

```
tests/
├── conftest.py           # Test configuration and fixtures
├── factories.py          # Test data factories
├── test_repository.py    # Repository/database tests
├── test_api.py          # API endpoint tests
└── ...                  # Additional test files
```

## Running Tests

### Quick Start

```bash
# Run all tests
python run_tests.py

# Run specific test types
python run_tests.py --type repository
python run_tests.py --type api
python run_tests.py --type unit

# Run with coverage
python run_tests.py --coverage

# Run specific test file
python run_tests.py --file test_repository.py

# Run specific test
python run_tests.py --test "test_create_profile"
```

### Using Pytest Directly

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific file
pytest tests/test_repository.py

# Run specific test class
pytest tests/test_repository.py::TestProfileRepository

# Run specific test method
pytest tests/test_repository.py::TestProfileRepository::test_create_profile

# Run with coverage
pytest --cov=. --cov-report=html
```

## Test Categories

### 1. Repository Tests (`test_repository.py`)

These test the database operations directly:

```python
@pytest_asyncio.async_test
async def test_create_profile(self, test_repo: BandRepository):
    """Test creating a new profile"""
    profile_data = ProfileFactory()
    user_id = TEST_USER_ID_1
    
    profile = await test_repo.create_profile(profile_data, user_id)
    
    assert profile.user_id == user_id
    assert profile.display_name == profile_data.display_name
```

**What they test:**
- Database CRUD operations
- Business logic in repository layer
- Data relationships and constraints
- Error handling in database operations

### 2. API Tests (`test_api.py`)

These test the HTTP endpoints:

```python
def test_create_profile(self, test_client: TestClient):
    """Test POST /profiles endpoint"""
    profile_data = ProfileFactory()
    
    response = test_client.post("/profiles", json=profile_data.dict())
    
    assert response.status_code == 201
    assert response.json()["display_name"] == profile_data.display_name
```

**What they test:**
- HTTP request/response handling
- Input validation
- Error responses
- JSON serialization
- Status codes

## Test Environment

### Isolated Database

Each test gets a fresh, in-memory SQLite database:

- **Fast**: In-memory database is very quick
- **Isolated**: Tests don't interfere with each other
- **Clean**: No leftover data between tests
- **Consistent**: Same schema as production PostgreSQL

### Test Fixtures

Common test setup is handled by fixtures in `conftest.py`:

```python
@pytest_asyncio.fixture
async def test_repo(test_session) -> BandRepository:
    """Create a test repository instance"""
    return BandRepository(test_session)

@pytest_asyncio.fixture
async def test_client(test_session):
    """Create a test client with dependency override"""
    # FastAPI client with test database
```

### Test Data Factories

Consistent test data generation using Factory Boy:

```python
class ProfileFactory(factory.Factory):
    class Meta:
        model = ProfileCreate
    
    display_name = factory.Sequence(lambda n: f"Test User {n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.display_name.lower()}@example.com")
```

**Benefits:**
- Consistent test data
- Easy to customize for specific tests
- Reduces boilerplate code
- Realistic data generation

## Writing New Tests

### 1. Repository Test Example

```python
@pytest_asyncio.async_test
async def test_update_band_name(self, test_repo: BandRepository):
    """Test updating a band's name"""
    # Create test data
    profile_data = ProfileFactory()
    user_id = TEST_USER_ID_1
    await test_repo.create_profile(profile_data, user_id)
    
    band_data = BandFactory(name="Original Name")
    band = await test_repo.create_band(band_data, user_id)
    
    # Test the operation
    updated_band = await test_repo.update_band(
        band.id, 
        {"name": "Updated Name"}
    )
    
    # Verify results
    assert updated_band is not None
    assert updated_band.name == "Updated Name"
    assert updated_band.id == band.id
```

### 2. API Test Example

```python
def test_update_band_name_api(self, test_client: TestClient):
    """Test PUT /bands/{band_id} endpoint"""
    # Create test band
    band_data = BandFactory()
    create_response = test_client.post("/bands", json=band_data.dict())
    created_band = create_response.json()
    
    # Update the band
    update_data = {"name": "Updated Name"}
    response = test_client.put(
        f"/bands/{created_band['id']}", 
        json=update_data
    )
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
```

## Test Best Practices

### 1. Test Naming

- Use descriptive names: `test_create_profile_with_duplicate_email`
- Follow pattern: `test_[action]_[condition]_[expected_result]`
- Group related tests in classes

### 2. Test Structure (Arrange-Act-Assert)

```python
async def test_join_band(self, test_repo: BandRepository):
    # Arrange - Set up test data
    user1_id = TEST_USER_ID_1
    user2_id = TEST_USER_ID_2
    await test_repo.create_profile(ProfileFactory(), user1_id)
    await test_repo.create_profile(ProfileFactory(), user2_id)
    band = await test_repo.create_band(BandFactory(), user1_id)
    
    # Act - Perform the operation
    membership = await test_repo.join_band(band.join_code, user2_id)
    
    # Assert - Verify the results
    assert membership is not None
    assert membership.user_id == user2_id
    assert membership.role == BandRole.MEMBER
```

### 3. Error Testing

Always test error conditions:

```python
async def test_join_nonexistent_band(self, test_repo: BandRepository):
    """Test joining a band with invalid join code"""
    user_id = TEST_USER_ID_1
    await test_repo.create_profile(ProfileFactory(), user_id)
    
    membership = await test_repo.join_band("invalid_code", user_id)
    
    assert membership is None
```

### 4. Edge Cases

Test boundary conditions:

```python
def test_create_profile_with_maximum_name_length(self, test_client: TestClient):
    """Test creating profile with 100-character name (max allowed)"""
    profile_data = ProfileFactory(display_name="a" * 100)
    
    response = test_client.post("/profiles", json=profile_data.dict())
    
    assert response.status_code == 201
```

## Debugging Tests

### 1. Verbose Output

```bash
pytest -v -s  # -s shows print statements
```

### 2. Run Single Test

```bash
pytest tests/test_repository.py::TestProfileRepository::test_create_profile -v
```

### 3. Debug with Print Statements

```python
async def test_create_profile(self, test_repo: BandRepository):
    profile_data = ProfileFactory()
    print(f"Creating profile: {profile_data.dict()}")  # Debug output
    
    profile = await test_repo.create_profile(profile_data, TEST_USER_ID_1)
    print(f"Created profile: {profile}")  # Debug output
    
    assert profile.display_name == profile_data.display_name
```

### 4. Test Database Inspection

```python
async def test_with_database_inspection(self, test_session):
    """Debug test by inspecting database state"""
    from sqlalchemy import text
    
    # Create some data...
    
    # Inspect database
    result = await test_session.execute(text("SELECT * FROM profiles"))
    rows = result.fetchall()
    print(f"Profiles in database: {rows}")
```

## Continuous Integration

The test suite is designed to run in CI environments:

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python run_tests.py --coverage
```

## Coverage Reporting

Generate code coverage reports:

```bash
# Generate HTML coverage report
python run_tests.py --coverage

# View in browser
open htmlcov/index.html
```

Coverage helps identify:
- Untested code paths
- Missing edge case tests
- Areas needing more test coverage

## Performance Testing

For performance-sensitive operations:

```python
import time

async def test_bulk_event_creation_performance(self, test_repo: BandRepository):
    """Test that creating many events is reasonably fast"""
    # Setup
    profile_data = ProfileFactory()
    user_id = TEST_USER_ID_1
    await test_repo.create_profile(profile_data, user_id)
    
    band_data = BandFactory()
    band = await test_repo.create_band(band_data, user_id)
    
    # Performance test
    start_time = time.time()
    
    for i in range(100):
        event_data = EventFactory(title=f"Event {i}")
        await test_repo.create_event(event_data, band.id, user_id)
    
    elapsed = time.time() - start_time
    
    # Should create 100 events in under 1 second
    assert elapsed < 1.0
```

## Summary

This testing setup provides:

- **Comprehensive Coverage**: Unit, integration, and API tests
- **Fast Execution**: In-memory database and efficient fixtures
- **Reliable**: Isolated tests that don't interfere with each other
- **Maintainable**: Clear structure and reusable components
- **Debuggable**: Good error messages and debugging options

The key to effective testing is:
1. **Write tests as you develop** - Don't leave testing until the end
2. **Test both happy paths and error cases**
3. **Keep tests simple and focused** - One concept per test
4. **Use descriptive names** - Tests are documentation
5. **Maintain test code quality** - Tests are code too!