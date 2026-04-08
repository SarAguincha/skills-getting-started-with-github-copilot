"""
Tests for the Mergington High School API application
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add the src directory to the path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities

# Store the initial state of activities for cleanup
INITIAL_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
}


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    # Clear all activities
    activities.clear()
    # Re-add initial activities with fresh participant lists
    for name, data in INITIAL_ACTIVITIES.items():
        activities[name] = {
            **data,
            "participants": data["participants"].copy()
        }
    yield
    # Clean up after test
    activities.clear()


def test_root_redirect(client):
    """Test that root endpoint redirects to static/index.html"""
    # Arrange - Nothing special needed
    
    # Act
    response = client.get("/", follow_redirects=False)
    
    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client):
    """Test getting all activities"""
    # Arrange - Activities are set up by fixture
    
    # Act
    response = client.get("/activities")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"


def test_signup_for_activity_success(client):
    """Test successfully signing up for an activity"""
    # Arrange
    email = "newstudent@mergington.edu"
    activity_name = "Chess Club"
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert f"Signed up {email} for {activity_name}" in data["message"]
    assert email in activities[activity_name]["participants"]


def test_signup_for_nonexistent_activity(client):
    """Test signing up for an activity that doesn't exist"""
    # Arrange
    email = "student@mergington.edu"
    activity_name = "Nonexistent Club"
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_signup_already_signed_up(client):
    """Test signing up for an activity when already signed up"""
    # Arrange
    email = "michael@mergington.edu"  # Already in Chess Club
    activity_name = "Chess Club"
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 400
    assert "Student already signed up for this activity" in response.json()["detail"]


def test_remove_from_activity_success(client):
    """Test successfully removing a student from an activity"""
    # Arrange
    email = "michael@mergington.edu"
    activity_name = "Chess Club"
    
    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert f"Removed {email} from {activity_name}" in data["message"]
    assert email not in activities[activity_name]["participants"]


def test_remove_from_nonexistent_activity(client):
    """Test removing a student from an activity that doesn't exist"""
    # Arrange
    email = "student@mergington.edu"
    activity_name = "Nonexistent Club"
    
    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_remove_not_signed_up_student(client):
    """Test removing a student who is not signed up for the activity"""
    # Arrange
    email = "notstudent@mergington.edu"
    activity_name = "Chess Club"
    
    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 400
    assert "Student not signed up for this activity" in response.json()["detail"]