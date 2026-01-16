"""
Pytest configuration and fixtures for AlphaMapping tests.
"""
import os
import sys
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.models.models import Base
from app.core.database import get_db


# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite:///:memory:"

# Create test engine
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db_session() -> Generator:
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session) -> Generator:
    """Create a test client with database override."""
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=test_engine)
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def sample_asset_data():
    """Sample asset data for testing."""
    return {
        "ip": "192.168.1.1",
        "port": 80,
        "protocol": "http",
        "domain": "example.com",
        "host": "www.example.com",
        "title": "Example Website",
        "server": "Apache/2.4",
        "country": "China",
        "city": "Beijing",
        "org": "Example Corp"
    }


@pytest.fixture
def mock_fofa_response():
    """Mock FOFA API response."""
    return {
        "error": False,
        "size": 2,
        "results": [
            ["192.168.1.1", "80", "http", "example.com", "www.example.com", 
             "Example Title", "Apache", "CN", "Beijing", "Example Org",
             "2024-01-01", "", "", "", "", "", "", "", "", "", "", "", ""],
            ["192.168.1.2", "443", "https", "test.com", "www.test.com",
             "Test Title", "Nginx", "US", "New York", "Test Corp",
             "2024-01-02", "", "", "", "", "", "", "", "", "", "", "", ""]
        ]
    }


@pytest.fixture
def mock_geolocation_response():
    """Mock IP geolocation API response."""
    return {
        "status": "success",
        "country": "China",
        "city": "Beijing",
        "lat": 39.9042,
        "lon": 116.4074
    }
