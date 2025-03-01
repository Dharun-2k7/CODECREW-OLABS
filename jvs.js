function showRegister() {
    document.getElementById("login-section").style.display = "none";
    document.getElementById("register-section").style.display = "block";
}

function showLogin() {
    document.getElementById("register-section").style.display = "none";
    document.getElementById("login-section").style.display = "block";
}

function register() {
    let username = document.getElementById("reg-username").value;
    let password = document.getElementById("reg-password").value;
    let dob = document.getElementById("reg-dob").value;
    let role = document.getElementById("reg-role").value;
    let linkedStudent = document.getElementById("reg-linked-student").value;

    if (!username || !password || !dob) {
        alert("Please fill in all required fields.");
        return;
    }

    fetch("http://127.0.0.1:5000/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password, dob, role, linkedStudent })
    })
    .then(res => {
        if (!res.ok) {
            throw new Error("Registration failed. Please try again.");
        }
        return res.json();
    })
    .then(data => {
        document.getElementById("register-message").innerText = data.message;
        if (data.success) showLogin();
    })
    .catch(error => {
        console.error("Registration error:", error);
        alert(error.message || "Error during registration. Please try again.");
    });
}

function login() {
    let username = document.getElementById("login-username").value;
    let password = document.getElementById("login-password").value;
    let dob = document.getElementById("login-dob").value;

    fetch("http://127.0.0.1:5000/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password, dob })
    })
    .then(res => {
        if (!res.ok) {
            throw new Error("Login failed. Please check your credentials.");
        }
        return res.json();
    })
    .then(data => {
        document.getElementById("login-message").innerText = data.message;
        if (data.success) {
            document.getElementById("user-role").innerText = data.role;
            document.getElementById("login-section").style.display = "none";
            document.getElementById("dashboard").style.display = "block";
        }
    })
    .catch(error => {
        console.error("Login error:", error);
        alert(error.message || "Error logging in. Please try again.");
    });
}

function logout() {
    document.getElementById("dashboard").style.display = "none";
    document.getElementById("login-section").style.display = "block";
    document.getElementById("login-message").innerText = "";
    document.getElementById("register-message").innerText = "";
}

function showChat() {
    document.getElementById("dashboard").style.display = "none";
    document.getElementById("chatbot-section").style.display = "block";
}

let chatHistory = [];

function askChatbot() {
    let question = document.getElementById("chat-question").value;
    if (question.trim() === "") return;

    chatHistory.push({ sender: "user", message: question });
    updateChatHistory();

    document.getElementById("chat-question").value = "";
    document.getElementById("chatbot-response").innerText = "Typing...";

    fetch("http://127.0.0.1:5000/chatbot", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question })
    })
    .then(res => {
        if (!res.ok) {
            throw new Error("Failed to get response from chatbot.");
        }
        return res.json();
    })
    .then(data => {
        chatHistory.push({ sender: "bot", message: data.response });
        updateChatHistory();
    })
    .catch(error => {
        console.error("Chatbot error:", error);
        alert(error.message || "Error interacting with the chatbot. Please try again.");
    });
}

function updateChatHistory() {
    const chatContainer = document.getElementById("chatbot-response");
    chatContainer.innerHTML = "";

    chatHistory.forEach(chat => {
        const chatMessage = document.createElement("div");
        chatMessage.className = chat.sender === "user" ? "chat-message user" : "chat-message bot";
        chatMessage.innerText = chat.message;
        chatContainer.appendChild(chatMessage);
    });

    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Function to display response progressively
function displayResponse(response) {
    const responseElement = document.getElementById("chatbot-response");
    responseElement.innerText = "";
    let index = 0;

    function typeChar() {
        if (index < response.length) {
            responseElement.innerText += response.charAt(index);
            index++;
            setTimeout(typeChar, 50); // Adjust typing speed here
        }
    }

    typeChar();
}