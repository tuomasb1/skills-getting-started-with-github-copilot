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

  // Initialize app
  fetchActivities();
});
