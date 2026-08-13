"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
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
    "Robotics Club": {
        "description": "Learn about robotics and participate in competitions",
        "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": ["lucas@mergington.edu", "mia@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Mondays and Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 16,
        "participants": ["alex@mergington.edu", "jordan@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore painting, sculpture, and digital art",
        "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
        "max_participants": 18,
        "participants": ["grace@mergington.edu", "taylor@mergington.edu"]
    },
    "Music Ensemble": {
        "description": "Join our orchestra and perform at school events",
        "schedule": "Mondays and Wednesdays, 3:45 PM - 5:00 PM",
        "max_participants": 25,
        "participants": ["ryan@mergington.edu", "avery@mergington.edu"]
    },
    "Science Club": {
        "description": "Conduct experiments and explore scientific concepts",
        "schedule": "Fridays, 3:30 PM - 4:45 PM",
        "max_participants": 20,
        "participants": ["sam@mergington.edu", "casey@mergington.edu"]
    },
    "Drama Club": {
        "description": "Perform in school plays and theatrical productions",
        "schedule": "Tuesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 22,
        "participants": ["morgan@mergington.edu", "bailey@mergington.edu"]
    },
    "Math Club": {
        "description": "Solve challenging math problems and prepare for competitions",
        "schedule": "Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 15,
        "participants": ["rowan@mergington.edu", "quinn@mergington.edu"]
    },
    "Environmental Club": {
        "description": "Learn about sustainability and environmental conservation",
        "schedule": "Wednesdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["cameron@mergington.edu", "dakota@mergington.edu"]
    },
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 14,
        "participants": ["austin@mergington.edu", "blake@mergington.edu"]
    },
    "Student Government": {
        "description": "Lead school events and represent the student body",
        "schedule": "Mondays, 3:30 PM - 4:30 PM",
        "max_participants": 12,
        "participants": ["casey@mergington.edu", "reese@mergington.edu"]
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student already signed up for this activity")

    # Validate activity is not full
    if len(activity["participants"]) >= activity["max_participants"]:
        raise HTTPException(status_code=400, detail="Activity is full")

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Check if student is registered
    if email not in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student is not registered for this activity")

    # Remove student
    activity["participants"].remove(email)
    return {"message": f"Unregistered {email} from {activity_name}"}


import random
from pydantic import BaseModel


class RPSInput(BaseModel):
    """Rock Paper Scissors game input"""
    player_choice: str


@app.post("/game/rps")
def play_rock_paper_scissors(game_input: RPSInput):
    """Play Rock Paper Scissors against the computer.
    
    Args:
        game_input: Contains player_choice (rock, paper, or scissors)
    
    Returns:
        Game result with outcome, computer choice, and result description
    """
    valid_choices = ["rock", "paper", "scissors"]
    player_choice = game_input.player_choice.lower().strip()
    
    # Validate player choice
    if player_choice not in valid_choices:
        raise HTTPException(status_code=400, detail=f"Invalid choice. Must be one of: {', '.join(valid_choices)}")
    
    # Computer makes random choice
    computer_choice = random.choice(valid_choices)
    
    # Determine winner
    if player_choice == computer_choice:
        result = "draw"
        message = "It's a tie!"
    elif (
        (player_choice == "rock" and computer_choice == "scissors") or
        (player_choice == "paper" and computer_choice == "rock") or
        (player_choice == "scissors" and computer_choice == "paper")
    ):
        result = "win"
        message = "You win!"
    else:
        result = "lose"
        message = "Computer wins!"
    
    return {
        "player_choice": player_choice,
        "computer_choice": computer_choice,
        "result": result,
        "message": message
    }


class TicTacToeInput(BaseModel):
    """Tic Tac Toe game input"""
    board: list
    move: int


def find_best_move(board):
    """Find the best move for computer (O) using minimax-like strategy.
    
    Args:
        board: List of 9 cells (X, O, or empty string)
    
    Returns:
        Index of best move for computer, or -1 if board is full
    """
    # Check if computer can win
    for i in range(9):
        if board[i] == "":
            test_board = board.copy()
            test_board[i] = "O"
            if check_winner(test_board) == "O":
                return i
    
    # Check if player can win and block
    for i in range(9):
        if board[i] == "":
            test_board = board.copy()
            test_board[i] = "X"
            if check_winner(test_board) == "X":
                return i
    
    # Take center if available
    if board[4] == "":
        return 4
    
    # Take corners
    corners = [0, 2, 6, 8]
    available_corners = [i for i in corners if board[i] == ""]
    if available_corners:
        return random.choice(available_corners)
    
    # Take any available space
    available = [i for i in range(9) if board[i] == ""]
    return available[0] if available else -1


def check_winner(board):
    """Check if there's a winner.
    
    Args:
        board: List of 9 cells
    
    Returns:
        "X" if X wins, "O" if O wins, None if no winner
    """
    winning_combos = [
        [0, 1, 2],
        [3, 4, 5],
        [6, 7, 8],
        [0, 3, 6],
        [1, 4, 7],
        [2, 5, 8],
        [0, 4, 8],
        [2, 4, 6],
    ]
    
    for combo in winning_combos:
        if board[combo[0]] == board[combo[1]] == board[combo[2]] != "":
            return board[combo[0]]
    
    return None


def is_board_full(board):
    """Check if board is full."""
    return all(cell != "" for cell in board)


@app.post("/game/tictactoe")
def play_tic_tac_toe(game_input: TicTacToeInput):
    """Play Tic Tac Toe against the computer.
    
    Args:
        game_input: Contains board state and player move
    
    Returns:
        Updated board, game status, and computer move (if any)
    """
    board = game_input.board.copy()
    move = game_input.move
    
    # Validate move
    if not isinstance(move, int) or move < 0 or move > 8:
        raise HTTPException(status_code=400, detail="Invalid move index")
    
    if board[move] != "":
        raise HTTPException(status_code=400, detail="Cell already occupied")
    
    # Player makes move
    board[move] = "X"
    
    # Check if player won
    winner = check_winner(board)
    if winner == "X":
        return {
            "board": board,
            "status": "player_win",
            "message": "You win!",
            "computer_move": -1
        }
    
    # Check if board is full (draw)
    if is_board_full(board):
        return {
            "board": board,
            "status": "draw",
            "message": "It's a draw!",
            "computer_move": -1
        }
    
    # Computer makes move
    computer_move = find_best_move(board)
    if computer_move == -1:
        return {
            "board": board,
            "status": "draw",
            "message": "It's a draw!",
            "computer_move": -1
        }
    
    board[computer_move] = "O"
    
    # Check if computer won
    winner = check_winner(board)
    if winner == "O":
        return {
            "board": board,
            "status": "computer_win",
            "message": "Computer wins!",
            "computer_move": computer_move
        }
    
    # Check if board is full (draw)
    if is_board_full(board):
        return {
            "board": board,
            "status": "draw",
            "message": "It's a draw!",
            "computer_move": computer_move
        }
    
    return {
        "board": board,
        "status": "continue",
        "message": "Your turn",
        "computer_move": computer_move
    }
