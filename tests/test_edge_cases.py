"""
Edge case and boundary condition tests for the Activities Management API.

Tests unusual scenarios, capacity transitions, and data edge cases.
"""
import pytest


class TestCapacityBoundaries:
    """Tests for activity capacity boundaries and transitions."""
    
    def test_activity_at_exact_capacity(self, client, test_email_factory):
        """Verify activity at exact capacity rejects additional signups."""
        # Programming Class has capacity of 3
        emails = [test_email_factory() for _ in range(3)]
        
        # Fill to capacity
        for email in emails:
            response = client.post(f"/activities/Programming%20Class/signup?email={email}")
            assert response.status_code == 200
        
        # Verify all signed up
        activities = client.get("/activities").json()
        assert len(activities["Programming Class"]["participants"]) == 3
        
        # Try to exceed capacity
        excess_email = test_email_factory()
        response = client.post(f"/activities/Programming%20Class/signup?email={excess_email}")
        assert response.status_code == 400
        assert "full" in response.json()["detail"].lower()
    
    def test_capacity_one_activity(self, client, test_email_factory):
        """Test activity with capacity of 1."""
        # Modify Gym Class to have capacity 1
        from src import app as app_module
        app_module.activities["Gym Class"]["max_participants"] = 1
        
        email1 = test_email_factory()
        email2 = test_email_factory()
        
        # First signup succeeds
        response1 = client.post(f"/activities/Gym%20Class/signup?email={email1}")
        assert response1.status_code == 200
        
        # Second signup fails
        response2 = client.post(f"/activities/Gym%20Class/signup?email={email2}")
        assert response2.status_code == 400
    
    def test_large_capacity_activity(self, client, test_email_factory):
        """Test activity with large capacity."""
        # Gym Class has capacity 30, verify multiple signups work
        emails = [test_email_factory() for _ in range(10)]
        
        for email in emails:
            response = client.post(f"/activities/Gym%20Class/signup?email={email}")
            assert response.status_code == 200
        
        activities = client.get("/activities").json()
        assert len(activities["Gym Class"]["participants"]) == 10


class TestEmailHandling:
    """Tests for email handling and variations."""
    
    def test_email_case_consistency(self, client):
        """Test how email case is handled (current implementation treats as case-sensitive)."""
        email_lowercase = "student@mergington.edu"
        email_uppercase = "STUDENT@mergington.edu"
        email_mixed = "Student@Mergington.edu"
        
        # All three should be treated as different emails (case-sensitive)
        response1 = client.post(f"/activities/Chess%20Club/signup?email={email_lowercase}")
        response2 = client.post(f"/activities/Chess%20Club/signup?email={email_uppercase}")
        response3 = client.post(f"/activities/Chess%20Club/signup?email={email_mixed}")
        
        # All should succeed (capacity is 2, but we only add 2 successfully)
        assert response1.status_code == 200
        assert response2.status_code == 200
        # response3 should fail due to capacity
        assert response3.status_code == 400
    
    def test_email_with_special_characters(self, client):
        """Test emails with special characters (URL encoding considerations)."""
        # Note: '+' in URL gets converted to space, so we use alternatives
        emails_with_special = [
            "student.name@mergington.edu",
            "student_123@mergington.edu",
            "student-name@mergington.edu"
        ]
        
        # All should be accepted
        for email in emails_with_special:
            response = client.post(f"/activities/Programming%20Class/signup?email={email}")
            assert response.status_code == 200
        
        activities = client.get("/activities").json()
        for email in emails_with_special:
            assert email in activities["Programming Class"]["participants"]
    
    def test_empty_email_accepted_by_backend(self, client):
        """Test that backend currently accepts empty email (no validation).
        
        This documents current behavior - backend should ideally validate this.
        """
        response = client.post("/activities/Chess%20Club/signup?email=")
        
        # Backend currently accepts empty email (no validation)
        assert response.status_code == 200
        
        # Verify it was added (shows no email validation)
        activities = client.get("/activities").json()
        assert "" in activities["Chess Club"]["participants"]


class TestActivityNameHandling:
    """Tests for activity name handling."""
    
    def test_activity_name_case_sensitivity(self, client, test_email_factory):
        """Test activity name case sensitivity."""
        email = test_email_factory()
        
        # Exact name should work
        response1 = client.post(f"/activities/Chess%20Club/signup?email={email}")
        assert response1.status_code == 200
        
        # Different case should fail
        email2 = test_email_factory()
        response2 = client.post(f"/activities/chess%20club/signup?email={email2}")
        assert response2.status_code == 404
    
    def test_activity_name_with_spaces_url_encoded(self, client, test_email_factory):
        """Test that activity names with spaces are properly URL encoded."""
        email = test_email_factory()
        
        # Spaces should be %20 encoded
        response = client.post(f"/activities/Chess%20Club/signup?email={email}")
        assert response.status_code == 200
        
        # Verify it shows up in activities
        activities = client.get("/activities").json()
        assert email in activities["Chess Club"]["participants"]


class TestSequentialOperations:
    """Tests for sequential signup and unregister operations."""
    
    def test_signup_unregister_signup_cycle(self, client, test_email_factory):
        """Test sign up, unregister, sign up again cycle."""
        email = test_email_factory()
        
        # First signup
        response1 = client.post(f"/activities/Chess%20Club/signup?email={email}")
        assert response1.status_code == 200
        
        # Unregister
        response2 = client.delete(f"/activities/Chess%20Club/unregister?email={email}")
        assert response2.status_code == 200
        
        # Sign up again
        response3 = client.post(f"/activities/Chess%20Club/signup?email={email}")
        assert response3.status_code == 200
        
        # Verify in activity
        activities = client.get("/activities").json()
        assert email in activities["Chess Club"]["participants"]
        assert activities["Chess Club"]["participants"].count(email) == 1
    
    def test_multiple_signup_unregister_sequences(self, client, test_email_factory):
        """Test multiple interleaved signup/unregister sequences."""
        emails = [test_email_factory() for _ in range(3)]
        
        # Sign up all
        for email in emails:
            client.post(f"/activities/Programming%20Class/signup?email={email}")
        
        # Unregister middle one
        client.delete(f"/activities/Programming%20Class/unregister?email={emails[1]}")
        
        # Sign up new one
        new_email = test_email_factory()
        client.post(f"/activities/Programming%20Class/signup?email={new_email}")
        
        # Verify final state
        activities = client.get("/activities").json()
        participants = activities["Programming Class"]["participants"]
        
        assert emails[0] in participants
        assert emails[1] not in participants
        assert emails[2] in participants
        assert new_email in participants


class TestConcurrentActivityManagement:
    """Tests for managing multiple activities simultaneously."""
    
    def test_signups_isolated_between_activities(self, client, test_email_factory):
        """Verify signup for one activity doesn't affect others."""
        email = test_email_factory()
        
        # Sign up for Chess Club
        client.post(f"/activities/Chess%20Club/signup?email={email}")
        
        # Verify email only in Chess Club, not others
        activities = client.get("/activities").json()
        
        assert email in activities["Chess Club"]["participants"]
        assert email not in activities["Programming Class"]["participants"]
        assert email not in activities["Gym Class"]["participants"]
    
    def test_capacity_independent_across_activities(self, client, test_email_factory):
        """Capacity for one activity should not affect others."""
        emails = [test_email_factory() for _ in range(4)]
        
        # Fill Chess Club (capacity 2)
        client.post(f"/activities/Chess%20Club/signup?email={emails[0]}")
        client.post(f"/activities/Chess%20Club/signup?email={emails[1]}")
        
        # Still able to sign up for Programming Class (capacity 3)
        response1 = client.post(f"/activities/Programming%20Class/signup?email={emails[2]}")
        response2 = client.post(f"/activities/Programming%20Class/signup?email={emails[3]}")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
