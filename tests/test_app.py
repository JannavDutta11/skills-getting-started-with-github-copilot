"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

client = TestClient(app)


class TestActivities:
    """Test the /activities endpoint"""

    def test_get_activities(self):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Basketball Team" in data
        assert "Soccer Club" in data
        assert "Art Club" in data

    def test_activity_structure(self):
        """Test that activities have the expected structure"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Basketball Team"]
        
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)


class TestSignup:
    """Test the signup endpoint"""

    def test_signup_for_activity(self):
        """Test signing up a student for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "test@mergington.edu" in data["message"]

    def test_signup_duplicate(self):
        """Test that duplicate signups are rejected"""
        # First signup
        response1 = client.post(
            "/activities/Math%20Club/signup?email=duplicate@mergington.edu"
        )
        assert response1.status_code == 200

        # Second signup (should fail)
        response2 = client.post(
            "/activities/Math%20Club/signup?email=duplicate@mergington.edu"
        )
        assert response2.status_code == 400
        data = response2.json()
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity(self):
        """Test signing up for a non-existent activity"""
        response = client.post(
            "/activities/Nonexistent%20Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]


class TestUnregister:
    """Test the unregister endpoint"""

    def test_unregister_from_activity(self):
        """Test unregistering a student from an activity"""
        # First signup
        signup_response = client.post(
            "/activities/Drama%20Club/signup?email=unregister@mergington.edu"
        )
        assert signup_response.status_code == 200

        # Then unregister
        response = client.delete(
            "/activities/Drama%20Club/unregister?email=unregister@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]

    def test_unregister_nonexistent_activity(self):
        """Test unregistering from a non-existent activity"""
        response = client.delete(
            "/activities/Nonexistent%20Club/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    def test_unregister_not_signed_up(self):
        """Test unregistering when not signed up"""
        response = client.delete(
            "/activities/Debate%20Team/unregister?email=notsignup@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]

    def test_participant_removed_from_list(self):
        """Test that participant is actually removed from the list"""
        email = "remove@mergington.edu"
        activity_name = "Gym%20Class"

        # Sign up
        client.post(f"/activities/{activity_name}/signup?email={email}")

        # Verify they're in the list
        response = client.get("/activities")
        assert email in response.json()["Gym Class"]["participants"]

        # Unregister
        client.delete(f"/activities/{activity_name}/unregister?email={email}")

        # Verify they're removed
        response = client.get("/activities")
        assert email not in response.json()["Gym Class"]["participants"]


class TestRoot:
    """Test the root endpoint"""

    def test_root_redirect(self):
        """Test that root redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
