document.addEventListener("DOMContentLoaded", () => {
    let questionCount = 1;

    // Add a new question dynamically
    function addQuestion() {
        questionCount++;
        const questionsContainer = document.getElementById("questionsContainer");
        const questionDiv = document.createElement("div");
        questionDiv.classList.add("form-group", "mt-3");
        questionDiv.id = `questionContainer${questionCount}`;
        questionDiv.innerHTML = `
            <label>Poll Question ${questionCount}:</label>
            <input type="text" class="form-control" name="questions[]" placeholder="Enter question here" required>
            <div class="mt-2" id="optionsContainer${questionCount}">
                <label>Options:</label>
                <div class="d-flex align-items-center mb-2">
                    <input type="text" class="form-control me-2" name="options[${questionCount - 1}][]" placeholder="Option 1" required>
                    <button type="button" class="btn btn-light btn-sm" onclick="deleteOption(this)">Delete</button>
                </div>
                <div class="d-flex align-items-center mb-2">
                    <input type="text" class="form-control me-2" name="options[${questionCount - 1}][]" placeholder="Option 2" required>
                    <button type="button" class="btn btn-light btn-sm" onclick="deleteOption(this)">Delete</button>
                </div>
            </div>
            <button type="button" class="btn btn-secondary mt-2" onclick="addOption('optionsContainer${questionCount}')">Add Option</button>
            <button type="button" class="btn btn-secondary mt-2" onclick="deleteQuestion('${questionDiv.id}')">Delete Question</button>
        `;
        questionsContainer.appendChild(questionDiv);
    }

    // Add an option dynamically
    function addOption(containerId) {
        const optionsContainer = document.getElementById(containerId);
        const optionCount = optionsContainer.querySelectorAll('input').length + 1;
        const optionDiv = document.createElement("div");
        optionDiv.classList.add("d-flex", "align-items-center", "mb-2");
        optionDiv.innerHTML = `
            <input type="text" class="form-control me-2" placeholder="Option ${optionCount}" required>
            <button type="button" class="btn btn-light btn-sm" onclick="deleteOption(this)">Delete</button>
        `;
        optionsContainer.appendChild(optionDiv);
    }

    // Delete an option
    function deleteOption(button) {
        button.parentElement.remove();
    }

    // Delete a question
    function deleteQuestion(questionId) {
        document.getElementById(questionId).remove();
    }

    // Submit the poll to the backend
    function submitPoll() {
        const questions = [];
        document.querySelectorAll("#questionsContainer .form-group").forEach((questionDiv, index) => {
            const questionText = questionDiv.querySelector("input[name='questions[]']").value.trim();
            const options = Array.from(questionDiv.querySelectorAll(`input[name='options[${index}][]']`)).map(option =>
                option.value.trim()
            );

            if (questionText && options.length > 0) {
                questions.push({ question: questionText, options });
            }
        });

        fetch('/local_create_poll', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ questions }),
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert("Poll created successfully!");
                    location.reload();
                } else {
                    alert("Error: " + data.message);
                }
            })
            .catch(error => {
                console.error("Error:", error);
                alert("An unexpected error occurred.");
            });
    }

    // Load existing polls
    function loadExistingPolls() {
        fetch('/polls')
            .then(response => response.json())
            .then(data => {
                const container = document.getElementById('existingPollsContainer');
                container.innerHTML = ''; // Clear existing content

                if (!data.polls || data.polls.length === 0) {
                    container.innerHTML = '<p>No polls available. Create a new one!</p>';
                    return;
                }

                data.polls.forEach(poll => {
                    const pollCard = document.createElement("div");
                    pollCard.classList.add("card", "mb-3");
                    pollCard.innerHTML = `
                        <div class="card-header">
                            <h5>${poll.question}</h5>
                            <button class="btn btn-light btn-sm float-end" onclick="deletePoll(${poll.id})">Delete Poll</button>
                        </div>
                        <div class="card-body">
                            <ul class="list-group">
                                ${poll.options
                                    .map(
                                        option =>
                                            `<li class="list-group-item d-flex justify-content-between align-items-center">
                                                ${option.option_text} - ${option.votes} votes
                                                <button class="btn btn-light btn-sm" onclick="deleteOptionFromPoll(${option.id}, ${poll.id})">Delete Option</button>
                                            </li>`
                                    )
                                    .join('')}
                            </ul>
                        </div>
                    `;
                    container.appendChild(pollCard);
                });
            })
            .catch(error => {
                console.error("Error loading polls:", error);
                document.getElementById('existingPollsContainer').innerHTML = '<p>Failed to load polls. Please try again later.</p>';
            });
    }

    // Release poll
    document.getElementById("releasePollButton").addEventListener("click", () => {
        fetch("/release_poll", { method: "POST" })
            .then(response => response.json())
            .then(data => {
                if (data.released) {
                    alert("Polls released!");
                } else {
                    alert("Polls retracted.");
                }
            })
            .catch(error => {
                console.error("Error toggling poll release:", error);
            });
    });
    

    // Start timer and redirect to results
    document.getElementById("startTimerButton").addEventListener("click", () => {
        fetch("/start_timer", { method: "POST" })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert("Timer started! Redirecting to results soon...");
                    
                    setTimeout(() => {
                        window.location.href = "/polls/results";
                    }, data.time_remaining * 1000);
                } else {
                    alert("Failed to start timer: " + data.message);
                }
            });
    });

    // Attach global event listeners
    window.addQuestion = addQuestion;
    window.addOption = addOption;
    window.deleteOption = deleteOption;
    window.deleteQuestion = deleteQuestion;
    window.submitPoll = submitPoll;

    // Load polls when the page is loaded
    loadExistingPolls();
});
