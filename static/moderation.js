function moderateText() {
    let userInput = document.getElementById("textInput").value.trim();
    let moderationBox = document.getElementById("moderationBox");
    let loading = document.getElementById("loading");

    if (userInput === "") {
        moderationBox.innerHTML = `<p class="text-danger">Please enter a text.</p>`;
        return;
    }

    moderationBox.innerHTML = "";
    loading.style.display = "block";

    fetch("/api/moderate-text", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ text: userInput })
    })
    .then(response => response.json())
    .then(data => {
        loading.style.display = "none";
        if (data.moderated_text !== userInput) {
            moderationBox.innerHTML = `
                <p class="text-danger"><strong>⚠ Detected offensive content:</strong> "${userInput}"</p>
                <p class="text-success"><strong>✅ Suggested correction:</strong> "${data.moderated_text}"</p>
            `;
        } else {
            moderationBox.innerHTML = `<p class="text-success">✅ This text looks appropriate, you can use it as is.</p>`;
        }
    })
    .catch(error => {
        console.error("Error:", error);
        loading.style.display = "none";
        moderationBox.innerHTML = `<p class="text-danger">An error occurred. Please try again.</p>`;
    });
}
