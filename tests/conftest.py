"""
Pytest configuration and shared fixtures for activity management tests.
"""
import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Provides a TestClient instance for testing FastAPI endpoints.
    
    Each test gets a fresh client to ensure no state pollution between tests.
    """
    return TestClient(app)


@pytest.fixture
def mock_activities():
    """Factory function for creating test activity data.
    
    Returns a factory function that can generate test activities with defaults.
    """
    def create_activity(
        name="Test Activity",
        description="A test activity",
        schedule="Mondays, 3:30 PM - 4:30 PM",
        max_participants=20,
        participants=None
    ):
        """Create a test activity dictionary with sensible defaults."""
        if participants is None:
            participants = []
        return {
            "description": description,
            "schedule": schedule,
            "max_participants": max_participants,
            "participants": participants.copy()
        }
    
    return create_activity


@pytest.fixture
def test_email_factory():
    """Factory function for generating unique test emails.
    
    Returns a factory that can generate sequential test emails.
    """
    counter = 0
    
    def generate_email(base="student"):
        """Generate a unique test email."""
        nonlocal counter
        counter += 1
        return f"{base}{counter}@mergington.edu"
    
    return generate_email


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to known state before each test.
    
    This fixture automatically runs before every test to ensure
    a consistent starting state and prevent test interdependencies.
    """
    # Store original state
    original_activities = app.state.__dict__.copy() if hasattr(app, "state") else {}
    
    # Reinitialize activities to a clean state
    from src import app as app_module
    app_module.activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 2,  # Small capacity for testing
            "participants": []
        },
        "Programming Class": {
            "description": "Learn programming fundamentals",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 3,
            "participants": []
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": []
        }
    }
    
    yield
    
    # Cleanup could go here if needed
