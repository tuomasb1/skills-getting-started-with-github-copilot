"""
Integration tests for the Activities Management API.

Tests the full endpoint behavior including happy paths and error cases.
"""
import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""
    
    def test_get_activities_returns_all_activities(self, client):
        """Verify GET /activities returns all activities."""
        response = client.get("/activities")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
    
    def test_activity_has_required_fields(self, client):
        """Verify each activity has required fields."""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_details in data.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)
    
    def test_participant_count_reflects_signups(self, client, test_email_factory):
        """Verify participant count is accurate after signups."""
        email1 = test_email_factory()
        email2 = test_email_factory()
        
        # Sign up two students
        client.post(f"/activities/Chess%20Club/signup?email={email1}")
        client.post(f"/activities/Chess%20Club/signup?email={email2}")
        
        # Check activities reflect both participants
        response = client.get("/activities")
        data = response.json()
        
        assert len(data["Chess Club"]["participants"]) == 2
        assert email1 in data["Chess Club"]["participants"]
        assert email2 in data["Chess Club"]["participants"]


class TestSignupHappyPath:
    """Tests for successful POST /activities/{activity}/signup requests."""
    
    def test_signup_new_student_success(self, client, test_email_factory):
        """Successfully sign up a new student for an activity."""
        email = test_email_factory()
        
        response = client.post(f"/activities/Chess%20Club/signup?email={email}")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert "Chess Club" in data["message"]
    
    def test_signup_reflects_in_activity_list(self, client, test_email_factory):
        """Verify signup is reflected in GET /activities response."""
        email = test_email_factory()
        
        client.post(f"/activities/Chess%20Club/signup?email={email}")
        response = client.get("/activities")
        data = response.json()
        
        assert email in data["Chess Club"]["participants"]
    
    def test_multiple_students_can_signup_for_same_activity(self, client, test_email_factory):
        """Multiple students can sign up for the same activity."""
        email1 = test_email_factory()
        email2 = test_email_factory()
        
        response1 = client.post(f"/activities/Gym%20Class/signup?email={email1}")
        response2 = client.post(f"/activities/Gym%20Class/signup?email={email2}")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        activities = client.get("/activities").json()
        assert email1 in activities["Gym Class"]["participants"]
        assert email2 in activities["Gym Class"]["participants"]
    
    def test_student_can_signup_for_different_activities(self, client):
        """A student can sign up for multiple different activities."""
        email = "multi@mergington.edu"
        
        response1 = client.post(f"/activities/Chess%20Club/signup?email={email}")
        response2 = client.post(f"/activities/Programming%20Class/signup?email={email}")
        response3 = client.post(f"/activities/Gym%20Class/signup?email={email}")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response3.status_code == 200
        
        activities = client.get("/activities").json()
        assert email in activities["Chess Club"]["participants"]
        assert email in activities["Programming Class"]["participants"]
        assert email in activities["Gym Class"]["participants"]


class TestSignupErrors:
    """Tests for error cases in POST /activities/{activity}/signup."""
    
    def test_signup_nonexistent_activity_returns_404(self, client, test_email_factory):
        """Signing up for non-existent activity returns 404."""
        email = test_email_factory()
        
        response = client.post(f"/activities/Fake%20Activity/signup?email={email}")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]
    
    def test_signup_duplicate_email_returns_400(self, client, test_email_factory):
        """Signing up with duplicate email returns 400."""
        email = test_email_factory()
        
        # First signup should succeed
        response1 = client.post(f"/activities/Chess%20Club/signup?email={email}")
        assert response1.status_code == 200
        
        # Second signup with same email should fail
        response2 = client.post(f"/activities/Chess%20Club/signup?email={email}")
        
        assert response2.status_code == 400
        data = response2.json()
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_at_capacity_returns_400(self, client, test_email_factory):
        """Signing up for full activity returns 400."""
        email1 = test_email_factory()
        email2 = test_email_factory()
        email3 = test_email_factory()
        
        # Chess Club has max_participants = 2
        response1 = client.post(f"/activities/Chess%20Club/signup?email={email1}")
        response2 = client.post(f"/activities/Chess%20Club/signup?email={email2}")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Third signup should fail
        response3 = client.post(f"/activities/Chess%20Club/signup?email={email3}")
        
        assert response3.status_code == 400
        data = response3.json()
        assert "full" in data["detail"].lower()
    
    def test_state_unchanged_after_failed_signup(self, client, test_email_factory):
        """Activity state remains unchanged after failed signup."""
        email = test_email_factory()
        
        # Get initial state
        initial = client.get("/activities").json()
        initial_participants = initial["Chess Club"]["participants"].copy()
        
        # Try duplicate signup
        client.post(f"/activities/Chess%20Club/signup?email={email}")
        client.post(f"/activities/Chess%20Club/signup?email={email}")  # Duplicate
        
        # Verify state unchanged (only one signup)
        after = client.get("/activities").json()
        assert after["Chess Club"]["participants"] == initial_participants + [email]


class TestUnregisterHappyPath:
    """Tests for successful DELETE /activities/{activity}/unregister requests."""
    
    def test_unregister_removes_student(self, client, test_email_factory):
        """Successfully unregister a student from an activity."""
        email = test_email_factory()
        
        # Sign up
        client.post(f"/activities/Chess%20Club/signup?email={email}")
        
        # Unregister
        response = client.delete(f"/activities/Chess%20Club/unregister?email={email}")
        
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert email in data["message"]
    
    def test_unregister_reflects_in_activity_list(self, client, test_email_factory):
        """Verify unregister is reflected in GET /activities response."""
        email = test_email_factory()
        
        # Sign up
        client.post(f"/activities/Chess%20Club/signup?email={email}")
        
        # Unregister
        client.delete(f"/activities/Chess%20Club/unregister?email={email}")
        
        # Verify removed from participants
        response = client.get("/activities")
        data = response.json()
        assert email not in data["Chess Club"]["participants"]
    
    def test_unregister_opens_spot_for_new_signup(self, client, test_email_factory):
        """Unregistering opens a spot for new signups."""
        email1 = test_email_factory()
        email2 = test_email_factory()
        email3 = test_email_factory()
        
        # Fill Chess Club (capacity = 2)
        client.post(f"/activities/Chess%20Club/signup?email={email1}")
        client.post(f"/activities/Chess%20Club/signup?email={email2}")
        
        # Unregister first student
        client.delete(f"/activities/Chess%20Club/unregister?email={email1}")
        
        # Third student should now be able to sign up
        response = client.post(f"/activities/Chess%20Club/signup?email={email3}")
        
        assert response.status_code == 200
        
        # Verify participants
        activities = client.get("/activities").json()
        assert email1 not in activities["Chess Club"]["participants"]
        assert email2 in activities["Chess Club"]["participants"]
        assert email3 in activities["Chess Club"]["participants"]


class TestUnregisterErrors:
    """Tests for error cases in DELETE /activities/{activity}/unregister."""
    
    def test_unregister_nonexistent_activity_returns_404(self, client, test_email_factory):
        """Unregistering from non-existent activity returns 404."""
        email = test_email_factory()
        
        response = client.delete(f"/activities/Fake%20Activity/unregister?email={email}")
        
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_unregister_unregistered_student_returns_400(self, client, test_email_factory):
        """Unregistering a student not in the activity returns 400."""
        email = test_email_factory()
        
        response = client.delete(f"/activities/Chess%20Club/unregister?email={email}")
        
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"].lower()
    
    def test_state_unchanged_after_failed_unregister(self, client, test_email_factory):
        """Activity state remains unchanged after failed unregister."""
        email1 = test_email_factory()
        email2 = test_email_factory()
        
        # Sign up email1
        client.post(f"/activities/Chess%20Club/signup?email={email1}")
        
        # Try to unregister email2 (not signed up)
        client.delete(f"/activities/Chess%20Club/unregister?email={email2}")
        
        # Verify email1 still registered
        response = client.get("/activities")
        data = response.json()
        assert email1 in data["Chess Club"]["participants"]
        assert len(data["Chess Club"]["participants"]) == 1
