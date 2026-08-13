document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");
  const signupAllBtn = document.getElementById("signupAllBtn");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        const participantsList = details.participants.length > 0
          ? `<div class="participants-list">${details.participants.map(p => `<div class="participant-item"><span>${p}</span><button class="delete-btn" data-activity="${name}" data-email="${p}" title="Unregister">×</button></div>`).join('')}</div>`
          : `<p><em>No participants yet</em></p>`;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-section">
            <strong>Participants:</strong>
            ${participantsList}
          </div>
        `;

        activitiesList.appendChild(activityCard);

        // Add delete button listeners
        activityCard.querySelectorAll(".delete-btn").forEach(btn => {
          btn.addEventListener("click", async (e) => {
            e.preventDefault();
            const activityName = btn.getAttribute("data-activity");
            const email = btn.getAttribute("data-email");
            
            try {
              const response = await fetch(
                `/activities/${encodeURIComponent(activityName)}/unregister?email=${encodeURIComponent(email)}`,
                { method: "DELETE" }
              );
              
              if (response.ok) {
                fetchActivities();
              } else {
                const result = await response.json();
                alert(result.detail || "Failed to unregister");
              }
            } catch (error) {
              alert("Error unregistering participant");
              console.error(error);
            }
          });
        });

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Handle sign up for all activities
  signupAllBtn.addEventListener("click", async () => {
    const email = document.getElementById("email").value;

    if (!email) {
      messageDiv.textContent = "Please enter an email address";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      return;
    }

    try {
      const response = await fetch("/activities");
      const activities = await response.json();
      const activityNames = Object.keys(activities);

      let successCount = 0;
      let skippedCount = 0;
      const errors = [];

      // Register for each activity
      for (const activityName of activityNames) {
        try {
          const signupResponse = await fetch(
            `/activities/${encodeURIComponent(activityName)}/signup?email=${encodeURIComponent(email)}`,
            { method: "POST" }
          );

          if (signupResponse.ok) {
            successCount++;
          } else {
            const result = await signupResponse.json();
            if (result.detail && result.detail.includes("already signed up")) {
              skippedCount++;
            } else {
              errors.push(`${activityName}: ${result.detail}`);
            }
          }
        } catch (error) {
          errors.push(`${activityName}: Error occurred`);
        }
      }

      // Show results
      let resultMessage = `Successfully registered for ${successCount} activit${successCount === 1 ? 'y' : 'ies'}`;
      if (skippedCount > 0) resultMessage += `, skipped ${skippedCount} (already registered)`;
      if (errors.length > 0) resultMessage += `, ${errors.length} error(s)`;

      messageDiv.textContent = resultMessage;
      messageDiv.className = errors.length > 0 ? "error" : "success";
      messageDiv.classList.remove("hidden");

      signupForm.reset();
      fetchActivities();

      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to register for activities";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error(error);
    }
  });

  // Game state
  let playerScore = 0;
  let computerScore = 0;
  const gameModal = document.getElementById("gameModal");
  const playGameBtn = document.getElementById("playGameBtn");
  const closeGame = document.getElementById("closeGame");
  const choiceBtns = document.querySelectorAll(".choice-btn");
  const gameResultDiv = document.getElementById("gameResult");
  const playerScoreSpan = document.getElementById("playerScore");
  const computerScoreSpan = document.getElementById("computerScore");

  // Open game modal
  playGameBtn.addEventListener("click", () => {
    gameModal.classList.remove("hidden");
  });

  // Close game modal
  closeGame.addEventListener("click", () => {
    gameModal.classList.add("hidden");
    // Reset game
    playerScore = 0;
    computerScore = 0;
    playerScoreSpan.textContent = "0";
    computerScoreSpan.textContent = "0";
    gameResultDiv.classList.add("hidden");
  });

  // Close modal when clicking outside
  window.addEventListener("click", (event) => {
    if (event.target === gameModal) {
      gameModal.classList.add("hidden");
      playerScore = 0;
      computerScore = 0;
      playerScoreSpan.textContent = "0";
      computerScoreSpan.textContent = "0";
      gameResultDiv.classList.add("hidden");
    }
  });

  // Handle game choice
  choiceBtns.forEach((btn) => {
    btn.addEventListener("click", async () => {
      const playerChoice = btn.getAttribute("data-choice");

      try {
        const response = await fetch("/game/rps", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ player_choice: playerChoice }),
        });

        if (!response.ok) {
          throw new Error("Game error");
        }

        const gameData = await response.json();

        // Update scores
        if (gameData.result === "win") {
          playerScore++;
        } else if (gameData.result === "lose") {
          computerScore++;
        }

        playerScoreSpan.textContent = playerScore;
        computerScoreSpan.textContent = computerScore;

        // Display result
        const choiceEmojis = {
          rock: "🪨",
          paper: "📄",
          scissors: "✂️",
        };

        gameResultDiv.innerHTML = `
          <div>
            <p>You chose: ${choiceEmojis[gameData.player_choice]} ${gameData.player_choice}</p>
            <p>Computer chose: ${choiceEmojis[gameData.computer_choice]} ${gameData.computer_choice}</p>
          </div>
          <p>${gameData.message}</p>
        `;
        gameResultDiv.className = `result ${gameData.result}`;
      } catch (error) {
        gameResultDiv.textContent = "Error playing game. Try again!";
        gameResultDiv.className = "result lose";
        console.error(error);
      }
    });
  });

  // Tic Tac Toe Game
  const tictactoeModal = document.getElementById("tictactoeModal");
  const playTicTacToeBtn = document.getElementById("playTicTacToeBtn");
  const closeTicTacToe = document.getElementById("closeTicTacToe");
  const tictactoeCells = document.querySelectorAll(".tictactoe-cell");
  const tictactoeStatus = document.getElementById("tictactoeStatus");
  const resetTicTacToeBtn = document.getElementById("resetTicTacToeBtn");
  
  let tictactoeBoard = ["", "", "", "", "", "", "", "", ""];
  let gameActive = true;

  // Open Tic Tac Toe modal
  playTicTacToeBtn.addEventListener("click", () => {
    tictactoeBoard = ["", "", "", "", "", "", "", "", ""];
    gameActive = true;
    updateTicTacToeBoard();
    tictactoeStatus.textContent = "Your turn (X)";
    tictactoeStatus.style.color = "#1a237e";
    tictactoeModal.classList.remove("hidden");
  });

  // Close Tic Tac Toe modal
  closeTicTacToe.addEventListener("click", () => {
    tictactoeModal.classList.add("hidden");
  });

  // Close modal when clicking outside
  window.addEventListener("click", (event) => {
    if (event.target === tictactoeModal) {
      tictactoeModal.classList.add("hidden");
    }
  });

  // Reset game
  resetTicTacToeBtn.addEventListener("click", () => {
    tictactoeBoard = ["", "", "", "", "", "", "", "", ""];
    gameActive = true;
    updateTicTacToeBoard();
    tictactoeStatus.textContent = "Your turn (X)";
    tictactoeStatus.style.color = "#1a237e";
  });

  function updateTicTacToeBoard() {
    tictactoeCells.forEach((cell, index) => {
      cell.textContent = tictactoeBoard[index];
      cell.classList.toggle("disabled", !gameActive || tictactoeBoard[index] !== "");
    });
  }

  // Handle Tic Tac Toe cell click
  tictactoeCells.forEach((cell) => {
    cell.addEventListener("click", async () => {
      if (!gameActive) return;
      
      const index = parseInt(cell.getAttribute("data-index"));
      
      if (tictactoeBoard[index] !== "") return;
      
      try {
        const response = await fetch("/game/tictactoe", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ board: tictactoeBoard, move: index }),
        });

        if (!response.ok) {
          throw new Error("Game error");
        }

        const gameData = await response.json();
        tictactoeBoard = gameData.board;
        updateTicTacToeBoard();

        // Update status
        if (gameData.status === "player_win") {
          tictactoeStatus.textContent = "You win! 🎉";
          tictactoeStatus.style.color = "#2e7d32";
          gameActive = false;
        } else if (gameData.status === "computer_win") {
          tictactoeStatus.textContent = "Computer wins!";
          tictactoeStatus.style.color = "#c62828";
          gameActive = false;
        } else if (gameData.status === "draw") {
          tictactoeStatus.textContent = "It's a draw!";
          tictactoeStatus.style.color = "#f57f17";
          gameActive = false;
        } else {
          tictactoeStatus.textContent = "Your turn (X)";
          tictactoeStatus.style.color = "#1a237e";
        }
      } catch (error) {
        tictactoeStatus.textContent = "Game error. Try again!";
        tictactoeStatus.style.color = "#c62828";
        console.error(error);
      }
    });
  });

  // Initialize app
  fetchActivities();
});
