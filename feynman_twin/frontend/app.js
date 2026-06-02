const API_BASE = "http://127.0.0.1:8000";

const statusEl = document.getElementById("status");
const chatEl = document.getElementById("chat");
const formEl = document.getElementById("chat-form");
const inputEl = document.getElementById("question-input");
const sendBtn = document.getElementById("send-btn");

function setStatus(text, kind) {
  statusEl.textContent = text;
  statusEl.className = `status status-${kind}`;
}

function addMessage(role, text) {
  const message = document.createElement("article");
  message.className = `message ${role}`;
  message.textContent = text;
  chatEl.appendChild(message);
  chatEl.scrollTop = chatEl.scrollHeight;
}

async function checkHealth() {
  try {
    const response = await fetch(`${API_BASE}/api/health`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const data = await response.json();
    setStatus(
      data.rag_ready
        ? "Backend online: RAG is ready"
        : "Backend online: RAG data not ready",
      "ok"
    );
  } catch (error) {
    setStatus(`Backend unreachable (${error.message})`, "error");
  }
}

formEl.addEventListener("submit", async (event) => {
  event.preventDefault();
  const question = inputEl.value.trim();
  if (!question) return;

  addMessage("user", question);
  inputEl.value = "";
  sendBtn.disabled = true;

  try {
    const response = await fetch(`${API_BASE}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.detail || `HTTP ${response.status}`);
    }

    addMessage("bot", payload.answer);
    addMessage(
      "meta",
      `Retrieved docs: ${payload.metadata.retrieved_docs} | Personality score: ${Math.round((payload.metadata.personality_score || 0) * 100)}%`
    );
  } catch (error) {
    addMessage("bot", `Error: ${error.message}`);
  } finally {
    sendBtn.disabled = false;
    inputEl.focus();
  }
});

checkHealth();
