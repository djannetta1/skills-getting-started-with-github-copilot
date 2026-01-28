"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add the src directory to the path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    initial_state = {
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
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Join the team to practice and compete in basketball games",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": []
        },
        "Soccer Club": {
            "description": "Learn soccer skills and participate in matches",
            "schedule": "Mondays and Wednesdays, 3:00 PM - 5:00 PM",
            "max_participants": 20,
            "participants": []
        },
        "Art Club": {
            "description": "Explore various art techniques and create projects",
            "schedule": "Fridays, 3:00 PM - 5:00 PM",
            "max_participants": 10,
            "participants": []
        },
        "Drama Club": {
            "description": "Participate in theater productions and improve acting skills",
            "schedule": "Thursdays, 5:00 PM - 7:00 PM",
            "max_participants": 20,
            "participants": []
        },
        "Debate Team": {
            "description": "Engage in debates on various topics and improve public speaking",
            "schedule": "Wednesdays, 4:00 PM - 6:00 PM",
            "max_participants": 12,
            "participants": []
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Tuesdays, 3:00 PM - 5:00 PM",
            "max_participants": 15,
            "participants": []
        }
    }
    
    # Clear and reset activities
    activities.clear()
    activities.update(initial_state)
    yield
    # Clean up after test
    activities.clear()
    activities.update(initial_state)


class TestGetActivities:
    """Tests for the GET /activities endpoint"""

    def test_get_activities_returns_list(self, client, reset_activities):
        """Test that GET /activities returns a list of activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_activity_contains_required_fields(self, client, reset_activities):
        """Test that each activity has all required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity in data.items():
            assert "description" in activity
            assert "schedule" in activity
            assert "max_participants" in activity
            assert "participants" in activity
            assert isinstance(activity["participants"], list)


class TestSignup:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_new_participant(self, client, reset_activities):
        """Test signing up a new participant to an activity"""
        response = client.post(
            "/activities/Basketball Team/signup?email=alex@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "alex@mergington.edu" in data["message"]

    def test_signup_adds_participant_to_activity(self, client, reset_activities):
        """Test that signup actually adds the participant to the activity"""
        email = "alex@mergington.edu"
        client.post(f"/activities/Basketball Team/signup?email={email}")
        
        response = client.get("/activities")
        data = response.json()
        assert email in data["Basketball Team"]["participants"]

    def test_signup_duplicate_participant_fails(self, client, reset_activities):
        """Test that signing up the same participant twice fails"""
        email = "michael@mergington.edu"
        response = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity_fails(self, client, reset_activities):
        """Test that signing up for a non-existent activity fails"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=alex@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_multiple_participants(self, client, reset_activities):
        """Test signing up multiple different participants"""
        emails = [
            "alex@mergington.edu",
            "brian@mergington.edu",
            "chris@mergington.edu"
        ]
        
        for email in emails:
            response = client.post(
                f"/activities/Basketball Team/signup?email={email}"
            )
            assert response.status_code == 200
        
        response = client.get("/activities")
        data = response.json()
        participants = data["Basketball Team"]["participants"]
        
        for email in emails:
            assert email in participants


class TestUnregister:
    """Tests for the POST /activities/{activity_name}/unregister endpoint"""

    def test_unregister_existing_participant(self, client, reset_activities):
        """Test unregistering an existing participant"""
        response = client.post(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Removed" in data["message"]

    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes the participant"""
        email = "michael@mergington.edu"
        client.post(f"/activities/Chess Club/unregister?email={email}")
        
        response = client.get("/activities")
        data = response.json()
        assert email not in data["Chess Club"]["participants"]

    def test_unregister_nonexistent_participant_fails(self, client, reset_activities):
        """Test that unregistering a non-existent participant fails"""
        response = client.post(
            "/activities/Basketball Team/unregister?email=notreal@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"]

    def test_unregister_from_nonexistent_activity_fails(self, client, reset_activities):
        """Test that unregistering from a non-existent activity fails"""
        response = client.post(
            "/activities/Nonexistent Club/unregister?email=alex@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_unregister_multiple_participants(self, client, reset_activities):
        """Test unregistering multiple participants"""
        emails = ["michael@mergington.edu", "daniel@mergington.edu"]
        
        for email in emails:
            response = client.post(
                f"/activities/Chess Club/unregister?email={email}"
            )
            assert response.status_code == 200
        
        response = client.get("/activities")
        data = response.json()
        participants = data["Chess Club"]["participants"]
        
        for email in emails:
            assert email not in participants


class TestSignupAndUnregister:
    """Integration tests for signup and unregister workflows"""

    def test_signup_then_unregister(self, client, reset_activities):
        """Test signing up and then unregistering"""
        email = "alex@mergington.edu"
        activity = "Basketball Team"
        
        # Sign up
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert response.status_code == 200
        
        # Verify signed up
        response = client.get("/activities")
        assert email in response.json()[activity]["participants"]
        
        # Unregister
        response = client.post(
            f"/activities/{activity}/unregister?email={email}"
        )
        assert response.status_code == 200
        
        # Verify unregistered
        response = client.get("/activities")
        assert email not in response.json()[activity]["participants"]

    def test_activity_participant_count_updates(self, client, reset_activities):
        """Test that participant count updates correctly"""
        activity = "Basketball Team"
        email = "alex@mergington.edu"
        
        response = client.get("/activities")
        initial_count = len(response.json()[activity]["participants"])
        
        # Sign up
        client.post(f"/activities/{activity}/signup?email={email}")
        
        response = client.get("/activities")
        new_count = len(response.json()[activity]["participants"])
        assert new_count == initial_count + 1
        
        # Unregister
        client.post(f"/activities/{activity}/unregister?email={email}")
        
        response = client.get("/activities")
        final_count = len(response.json()[activity]["participants"])
        assert final_count == initial_count
