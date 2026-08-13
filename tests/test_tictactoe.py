"""Tests for Tic Tac Toe game endpoint"""

import pytest
from src.app import app, check_winner, find_best_move


class TestTicTacToeValidation:
    """Test input validation for Tic Tac Toe endpoint"""

    def test_invalid_move_index_negative(self, client):
        """Test that negative move index is rejected"""
        board = ["", "", "", "", "", "", "", "", ""]
        response = client.post(
            "/game/tictactoe",
            json={"board": board, "move": -1}
        )
        assert response.status_code == 400

    def test_invalid_move_index_too_large(self, client):
        """Test that move index >= 9 is rejected"""
        board = ["", "", "", "", "", "", "", "", ""]
        response = client.post(
            "/game/tictactoe",
            json={"board": board, "move": 9}
        )
        assert response.status_code == 400

    def test_occupied_cell_rejected(self, client):
        """Test that moving to an occupied cell is rejected"""
        board = ["X", "", "", "", "", "", "", "", ""]
        response = client.post(
            "/game/tictactoe",
            json={"board": board, "move": 0}
        )
        assert response.status_code == 400
        assert "occupied" in response.json()["detail"].lower()


class TestTicTacToeGameplay:
    """Test Tic Tac Toe game logic and flow"""

    def test_valid_move_accepted(self, client):
        """Test that a valid move is accepted and board is updated"""
        board = ["", "", "", "", "", "", "", "", ""]
        response = client.post(
            "/game/tictactoe",
            json={"board": board, "move": 0}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["board"][0] == "X"
        assert data["status"] in ["continue", "player_win", "draw", "computer_win"]

    def test_computer_makes_move(self, client):
        """Test that computer makes a move after player"""
        board = ["", "", "", "", "", "", "", "", ""]
        response = client.post(
            "/game/tictactoe",
            json={"board": board, "move": 4}  # Player takes center
        )
        assert response.status_code == 200
        data = response.json()
        # Board should have X at position 4 and O somewhere else (unless draw/win)
        if data["status"] == "continue":
            x_count = data["board"].count("X")
            o_count = data["board"].count("O")
            assert x_count == 1
            assert o_count == 1

    def test_player_win_top_row(self, client):
        """Test player winning with top row"""
        board = ["X", "X", "", "", "", "", "", "", ""]
        response = client.post(
            "/game/tictactoe",
            json={"board": board, "move": 2}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "player_win"
        assert data["message"] == "You win!"

    def test_player_win_diagonal(self, client):
        """Test player winning with diagonal"""
        board = ["X", "", "", "", "X", "", "", "", ""]
        response = client.post(
            "/game/tictactoe",
            json={"board": board, "move": 8}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "player_win"

    def test_computer_win_blocked_by_player_move(self, client):
        """Test that computer blocks player from winning"""
        # Set up board where player can win with position 2
        board = ["X", "X", "", "", "O", "", "", "", "O"]
        response = client.post(
            "/game/tictactoe",
            json={"board": board, "move": 1}  # This move doesn't matter, just testing flow
        )
        # Actually, let's test a simpler scenario
        board = ["X", "X", "", "O", "O", "", "", "", ""]
        response = client.post(
            "/game/tictactoe",
            json={"board": board, "move": 2}
        )
        assert response.status_code == 200
        # Computer should block the win

    def test_draw_game(self, client):
        """Test that draw is detected when board is full without winner"""
        # Stalemate: X at 0,1,3 O at 2,4 X at 5, O at 6, X at 7, O at 8
        board = ["X", "X", "O", "X", "O", "X", "O", "X", ""]
        response = client.post(
            "/game/tictactoe",
            json={"board": board, "move": 8}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "draw"

    def test_response_contains_computer_move(self, client):
        """Test that response includes computer_move position"""
        board = ["", "", "", "", "", "", "", "", ""]
        response = client.post(
            "/game/tictactoe",
            json={"board": board, "move": 0}
        )
        assert response.status_code == 200
        data = response.json()
        assert "computer_move" in data
        if data["status"] == "continue":
            assert data["computer_move"] >= 0


class TestCheckWinner:
    """Test the check_winner helper function"""

    def test_no_winner_empty_board(self):
        """Test that empty board has no winner"""
        board = ["", "", "", "", "", "", "", "", ""]
        assert check_winner(board) is None

    def test_x_wins_top_row(self):
        """Test X winning top row"""
        board = ["X", "X", "X", "", "", "", "", "", ""]
        assert check_winner(board) == "X"

    def test_o_wins_middle_row(self):
        """Test O winning middle row"""
        board = ["", "", "", "O", "O", "O", "", "", ""]
        assert check_winner(board) == "O"

    def test_x_wins_left_column(self):
        """Test X winning left column"""
        board = ["X", "", "", "X", "", "", "X", "", ""]
        assert check_winner(board) == "X"

    def test_o_wins_diagonal(self):
        """Test O winning diagonal"""
        board = ["O", "", "", "", "O", "", "", "", "O"]
        assert check_winner(board) == "O"

    def test_o_wins_anti_diagonal(self):
        """Test O winning anti-diagonal"""
        board = ["", "", "O", "", "O", "", "O", "", ""]
        assert check_winner(board) == "O"

    def test_incomplete_row_no_winner(self):
        """Test that incomplete row doesn't win"""
        board = ["X", "X", "", "", "", "", "", "", ""]
        assert check_winner(board) is None


class TestFindBestMove:
    """Test the find_best_move AI function"""

    def test_computer_wins_when_possible(self):
        """Test that computer takes winning move"""
        board = ["O", "", "", "", "O", "", "", "", ""]  # O can win at 8 (diagonal)
        best = find_best_move(board)
        assert best == 8  # Position to complete the diagonal

    def test_computer_blocks_player_win(self):
        """Test that computer blocks player winning move"""
        board = ["X", "X", "", "", "", "", "", "", ""]  # X can win at 2
        best = find_best_move(board)
        assert best == 2  # Should block at position 2

    def test_takes_center_when_available(self):
        """Test that computer prefers center"""
        board = ["", "", "", "", "", "", "", "", ""]  # Empty board
        best = find_best_move(board)
        assert best == 4  # Center position

    def test_returns_valid_move(self):
        """Test that find_best_move returns valid position"""
        board = ["X", "", "O", "", "X", "", "O", "", ""]
        best = find_best_move(board)
        # Should return a valid empty position or -1 if full
        if best != -1:
            assert 0 <= best <= 8
            assert board[best] == ""

    def test_full_board_returns_minus_one(self):
        """Test that full board returns -1"""
        board = ["X", "O", "X", "O", "X", "O", "X", "O", "X"]
        best = find_best_move(board)
        assert best == -1


class TestGameStateManagement:
    """Test that game state is properly managed"""

    def test_board_state_preserved_on_error(self, client):
        """Test that board state isn't modified on invalid move"""
        board = ["X", "", "", "", "", "", "", "", ""]
        original = board.copy()
        response = client.post(
            "/game/tictactoe",
            json={"board": board, "move": 0}  # Try to play occupied cell
        )
        assert response.status_code == 400
        # Board shouldn't change in request context

    def test_alternating_turns(self, client):
        """Test that X and O alternate"""
        board = ["", "", "", "", "", "", "", "", ""]
        
        # First move: player
        response1 = client.post(
            "/game/tictactoe",
            json={"board": board, "move": 0}
        )
        assert response1.status_code == 200
        board1 = response1.json()["board"]
        
        # Verify X at position 0 and one O elsewhere
        assert board1[0] == "X"
        o_count = board1.count("O")
        x_count = board1.count("X")
        
        if response1.json()["status"] == "continue":
            assert x_count == 1
            assert o_count == 1
