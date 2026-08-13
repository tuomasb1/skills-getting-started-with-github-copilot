"""
Tests for the Rock Paper Scissors minigame endpoint.
"""
import pytest


class TestRockPaperScissors:
    """Tests for POST /game/rps endpoint."""

    def test_rock_beats_scissors(self, client, monkeypatch):
        """Verify rock beats scissors."""
        # Mock random to return scissors for computer
        import random
        monkeypatch.setattr(random, "choice", lambda x: "scissors")

        response = client.post(
            "/game/rps",
            json={"player_choice": "rock"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["player_choice"] == "rock"
        assert data["computer_choice"] == "scissors"
        assert data["result"] == "win"
        assert data["message"] == "You win!"

    def test_paper_beats_rock(self, client, monkeypatch):
        """Verify paper beats rock."""
        import random
        monkeypatch.setattr(random, "choice", lambda x: "rock")

        response = client.post(
            "/game/rps",
            json={"player_choice": "paper"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["player_choice"] == "paper"
        assert data["computer_choice"] == "rock"
        assert data["result"] == "win"

    def test_scissors_beats_paper(self, client, monkeypatch):
        """Verify scissors beats paper."""
        import random
        monkeypatch.setattr(random, "choice", lambda x: "paper")

        response = client.post(
            "/game/rps",
            json={"player_choice": "scissors"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["player_choice"] == "scissors"
        assert data["computer_choice"] == "paper"
        assert data["result"] == "win"

    def test_draw_when_same_choice(self, client, monkeypatch):
        """Verify draw when player and computer choose same."""
        import random
        monkeypatch.setattr(random, "choice", lambda x: "rock")

        response = client.post(
            "/game/rps",
            json={"player_choice": "rock"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["result"] == "draw"
        assert data["message"] == "It's a tie!"

    def test_computer_wins_rock_vs_paper(self, client, monkeypatch):
        """Verify computer wins when rock plays paper."""
        import random
        monkeypatch.setattr(random, "choice", lambda x: "paper")

        response = client.post(
            "/game/rps",
            json={"player_choice": "rock"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["result"] == "lose"
        assert data["message"] == "Computer wins!"

    def test_computer_wins_paper_vs_scissors(self, client, monkeypatch):
        """Verify computer wins when paper plays scissors."""
        import random
        monkeypatch.setattr(random, "choice", lambda x: "scissors")

        response = client.post(
            "/game/rps",
            json={"player_choice": "paper"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["result"] == "lose"

    def test_computer_wins_scissors_vs_rock(self, client, monkeypatch):
        """Verify computer wins when scissors plays rock."""
        import random
        monkeypatch.setattr(random, "choice", lambda x: "rock")

        response = client.post(
            "/game/rps",
            json={"player_choice": "scissors"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["result"] == "lose"

    def test_invalid_choice_returns_400(self, client):
        """Verify invalid choice returns 400 error."""
        response = client.post(
            "/game/rps",
            json={"player_choice": "dynamite"}
        )

        assert response.status_code == 400
        data = response.json()
        assert "Invalid choice" in data["detail"]

    def test_case_insensitive_input(self, client, monkeypatch):
        """Verify player choice is case insensitive."""
        import random
        monkeypatch.setattr(random, "choice", lambda x: "scissors")

        # Test uppercase
        response = client.post(
            "/game/rps",
            json={"player_choice": "ROCK"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["player_choice"] == "rock"
        assert data["result"] == "win"

    def test_whitespace_trimmed(self, client, monkeypatch):
        """Verify whitespace is trimmed from input."""
        import random
        monkeypatch.setattr(random, "choice", lambda x: "scissors")

        response = client.post(
            "/game/rps",
            json={"player_choice": "  rock  "}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["player_choice"] == "rock"
        assert data["result"] == "win"
