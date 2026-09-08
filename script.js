async function sendMessage() {

    const input = document.getElementById("message");
    const chat = document.getElementById("chat");
    const message = input.value.trim();

    if (!message) {
        return;
    }

    const user = document.createElement("div");
    user.className = "user";
    user.textContent = message;
    chat.appendChild(user);

    input.value = "";

    const loading = document.createElement("div");
    loading.className = "bot";
    loading.textContent = "🤔 FamilyCare AI is thinking...";
    chat.appendChild(loading);

    document.getElementById("intent").textContent = "Analyzing request";
    document.getElementById("plan").textContent = "Checking care data";

    try {
        const response = await fetch("/api/assistant", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: message })
        });

        const data = await response.json();

        loading.remove();

        const bot = document.createElement("div");
        bot.className = "bot";
        bot.textContent = data.response;
        chat.appendChild(bot);

        const tool = document.getElementById("tool");
        if (data.tool_used && data.tool_used !== "none") {
            tool.textContent = data.tool_used;
        } else {
            tool.textContent = "No tool required";
        }

        document.getElementById("intent").textContent = data.tool_used || "General chat";
        document.getElementById("plan").textContent = data.response.split("\n")[0] || "Ready";

    } catch (error) {
        loading.textContent = "❌ Unable to connect to the AI agent.";
        console.error(error);
    }

    chat.scrollTop = chat.scrollHeight;
}


document.getElementById("message").addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
});