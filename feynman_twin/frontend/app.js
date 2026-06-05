const API_BASE = "http://127.0.0.1:8000" ;

// ============ DOM REFERENCES ============
const statusEl        = document.getElementById("status");
const chatEl          = document.getElementById("chat");
const formEl          = document.getElementById("chat-form");
const inputEl         = document.getElementById("question-input");
const sendBtn         = document.getElementById("send-btn");
const lengthSelector  = document.getElementById("answer-length");
const voiceInputBtn   = document.getElementById("voice-input-btn");
const voiceToggleBtn  = document.getElementById("voice-toggle-btn");

const sidebar           = document.getElementById("sidebar");
const toggleSidebarBtn  = document.getElementById("toggle-sidebar-btn");
const closeSidebarBtn   = document.getElementById("close-sidebar-btn");
const newChatBtn        = document.getElementById("new-chat-btn");
const conversationsList = document.getElementById("conversations-list");
const cardsDueBadge     = document.getElementById("cards-due-badge");

// ============ STATE ============
let currentConversationId = null;
let recognition           = null;
let isRecording           = false;
let voiceOutputEnabled    = true;
let speechSynthesis       = window.speechSynthesis;

// ============ UTILITY ============
function setStatus(text, kind) {
  statusEl.textContent = text;
  statusEl.className = `status status-${kind}`;
}

function formatRelativeDate(isoStr) {
  if (!isoStr) return "";
  const d = new Date(isoStr);
  const now = new Date();
  const diffMs = now - d;
  const diffMin = Math.floor(diffMs / 60000);
  if (diffMin < 1) return "Just now";
  if (diffMin < 60) return `${diffMin}m ago`;
  const diffH = Math.floor(diffMin / 60);
  if (diffH < 24) return `${diffH}h ago`;
  return d.toLocaleDateString();
}

// ============ MESSAGES ============
function addMessage(role, text) {
  const message = document.createElement("article");
  message.className = `message ${role}`;
  message.textContent = text;
  chatEl.appendChild(message);
  chatEl.scrollTop = chatEl.scrollHeight;

  if (role === "bot" && voiceOutputEnabled) {
    speakText(text);
  }
}

function clearChat() {
  chatEl.innerHTML = "";
}

// ============ HEALTH CHECK ============
async function checkHealth() {
  try {
    const response = await fetch(`${API_BASE}/api/health`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    setStatus(
      data.rag_ready ? "Backend online: RAG ready" : "Backend online: RAG not ready",
      "ok"
    );
  } catch (error) {
    setStatus(`Backend unreachable (${error.message})`, "error");
  }
}

// ============ SIDEBAR TOGGLE ============
toggleSidebarBtn.addEventListener("click", () => {
  sidebar.classList.toggle("open");
  if (sidebar.classList.contains("open")) {
    loadConversationList();
  }
});

closeSidebarBtn.addEventListener("click", () => {
  sidebar.classList.remove("open");
});

// ============ CONVERSATION LIST ============
async function loadConversationList() {
  try {
    const res = await fetch(`${API_BASE}/api/conversations`);
    if (!res.ok) return;
    const conversations = await res.json();
    renderConversationList(conversations);
  } catch (err) {
    console.error("Failed to load conversations:", err);
  }
}

function renderConversationList(conversations) {
  conversationsList.innerHTML = "";

  if (conversations.length === 0) {
    conversationsList.innerHTML = `<p style="color:var(--muted);font-size:0.8rem;padding:0.5rem 0.75rem;">No conversations yet.</p>`;
    return;
  }

  conversations.forEach(conv => {
    const item = document.createElement("div");
    item.className = `conv-item ${conv.id === currentConversationId ? "active" : ""}`;
    item.dataset.id = conv.id;

    item.innerHTML = `
      <div class="conv-item-info">
        <div class="conv-title" title="${conv.title}">${conv.title || "Untitled"}</div>
        <div class="conv-date">${formatRelativeDate(conv.last_updated)} - ${conv.message_count} msgs</div>
      </div>
      <div class="conv-actions">
        <button class="conv-action-btn rename-btn" title="Rename">rename</button>
        <button class="conv-action-btn delete-btn" title="Delete">delete</button>
      </div>
    `;

    // Click to load
    item.querySelector(".conv-item-info").addEventListener("click", () => {
      loadConversation(conv.id);
      // On mobile close sidebar after selection
      if (window.innerWidth <= 768) sidebar.classList.remove("open");
    });

    // Rename
    item.querySelector(".rename-btn").addEventListener("click", async (e) => {
      e.stopPropagation();
      const newTitle = prompt("Rename conversation:", conv.title);
      if (newTitle && newTitle.trim()) {
        try {
          await fetch(`${API_BASE}/api/conversations/${conv.id}`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ title: newTitle.trim() })
          });
          loadConversationList();
        } catch (err) {
          console.error("Failed to rename:", err);
        }
      }
    });

    // Delete
    item.querySelector(".delete-btn").addEventListener("click", async (e) => {
      e.stopPropagation();
      if (!confirm(`Delete "${conv.title}"?`)) return;
      try {
        const res = await fetch(`${API_BASE}/api/conversations/${conv.id}`, { method: "DELETE" });
        if (res.ok) {
          if (conv.id === currentConversationId) {
            startNewChat();
          }
          loadConversationList();
        }
      } catch (err) {
        console.error("Failed to delete:", err);
      }
    });

    conversationsList.appendChild(item);
  });
}

// ============ LOAD CONVERSATION ============
async function loadConversation(convId) {
  try {
    const res = await fetch(`${API_BASE}/api/conversations/${convId}`);
    if (!res.ok) throw new Error("Conversation not found");
    const conv = await res.json();

    currentConversationId = convId;
    clearChat();

    // Render all messages
    const messages = conv.messages || [];
    messages.forEach(msg => {
      if (msg.role === "user") {
        addMessage("user", msg.content);
      } else if (msg.role === "assistant") {
        addMessage("bot", msg.content);
      }
    });

    // Highlight active in sidebar
    document.querySelectorAll(".conv-item").forEach(el => {
      el.classList.toggle("active", el.dataset.id === convId);
    });

    if (messages.length === 0) {
      addMessage("bot", "Hello! I'm Richard Feynman. Ask me anything about physics, science, or learning.");
    }

  } catch (err) {
    console.error("Failed to load conversation:", err);
  }
}

// ============ NEW CHAT ============
function startNewChat() {
  currentConversationId = null;
  clearChat();
  // De-select sidebar items
  document.querySelectorAll(".conv-item").forEach(el => el.classList.remove("active"));
}

newChatBtn.addEventListener("click", () => {
  startNewChat();
  if (window.innerWidth <= 768) sidebar.classList.remove("open");
});

// ============ CHAT FORM SUBMIT ============
formEl.addEventListener("submit", async (event) => {
  event.preventDefault();
  const question = inputEl.value.trim();
  if (!question) return;

  const answerLength = lengthSelector.value;
  addMessage("user", question);
  inputEl.value = "";
  sendBtn.disabled = true;

  try {
    const body = {
      question,
      answer_length: answerLength,
      conversation_id: currentConversationId || null
    };

    const response = await fetch(`${API_BASE}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.detail || `HTTP ${response.status}`);
    }

    // Track conversation ID for subsequent messages
    if (payload.conversation_id) {
      currentConversationId = payload.conversation_id;
    }

    addMessage("bot", payload.answer);
    addMessage(
      "meta",
      `Retrieved docs: ${payload.metadata.retrieved_docs ?? 0} | Personality: ${Math.round((payload.metadata.personality_score || 0) * 100)}%`
    );

    // Refresh sidebar list if open
    if (sidebar.classList.contains("open")) {
      loadConversationList();
    }

    // Refresh due badge
    updateCardsDueBadge();

  } catch (error) {
    addMessage("bot", `Error: ${error.message}`);
  } finally {
    sendBtn.disabled = false;
    inputEl.focus();
  }
});

// ============ CARDS DUE BADGE ============
async function updateCardsDueBadge() {
  try {
    const res = await fetch(`${API_BASE}/api/teach-me/stats`);
    if (!res.ok) return;
    const stats = await res.json();
    const count = stats.cards_due || 0;
    cardsDueBadge.textContent = count;
    cardsDueBadge.setAttribute("data-count", count);
    // Show/hide via CSS [data-count="0"] selector
  } catch (err) {
    // Silently fail - badge is non-critical
  }
}

// ============ VOICE FUNCTIONS ============
function initSpeechRecognition() {
  if ("webkitSpeechRecognition" in window || "SpeechRecognition" in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "en-US";

    recognition.onstart = () => {
      isRecording = true;
      voiceInputBtn.classList.add("recording");
      setStatus("Listening... (Requires internet connection)", "waiting");
    };

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      inputEl.value = transcript;
      setStatus("Voice input captured successfully", "ok");
      setTimeout(() => checkHealth(), 2000);
    };

    recognition.onerror = (event) => {
      isRecording = false;
      voiceInputBtn.classList.remove("recording");
      const errMessages = {
        network: "Voice input requires internet. Please check your connection.",
        "not-allowed": "Microphone access denied. Allow mic permissions in browser settings.",
        "no-speech": "No speech detected. Try again.",
        aborted: "Voice input cancelled.",
        "audio-capture": "No microphone found.",
        "service-not-allowed": "Speech recognition unavailable.",
      };
      setStatus(errMessages[event.error] || `Voice input error: ${event.error}`, "error");
      setTimeout(() => checkHealth(), 8000);
    };

    recognition.onend = () => {
      isRecording = false;
      voiceInputBtn.classList.remove("recording");
    };
  } else {
    voiceInputBtn.disabled = true;
    voiceInputBtn.title = "Speech recognition not supported";
    voiceInputBtn.style.opacity = "0.5";
    voiceInputBtn.style.cursor = "not-allowed";
  }
}

voiceInputBtn.addEventListener("click", () => {
  if (!recognition) initSpeechRecognition();
  if (isRecording) {
    recognition.stop();
  } else {
    try { recognition.start(); } catch (e) { console.error(e); }
  }
});

voiceToggleBtn.addEventListener("click", () => {
  voiceOutputEnabled = !voiceOutputEnabled;
  voiceToggleBtn.textContent = voiceOutputEnabled ? "🔊" : "🔇";
  voiceToggleBtn.classList.toggle("active", voiceOutputEnabled);
  if (!voiceOutputEnabled) speechSynthesis.cancel();
  setStatus(voiceOutputEnabled ? "Voice output enabled" : "Voice output disabled", "ok");
  setTimeout(() => checkHealth(), 2000);
});

function speakText(text) {
  if (!voiceOutputEnabled) return;
  speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  const voices = speechSynthesis.getVoices();
  const preferredVoice =
    voices.find(v => v.lang.startsWith("en") && v.name.includes("Male")) ||
    voices.find(v => v.lang.startsWith("en-US")) ||
    voices[0];
  if (preferredVoice) utterance.voice = preferredVoice;
  utterance.rate  = 0.95;
  utterance.pitch = 1.0;
  utterance.volume = 1.0;
  utterance.onstart = () => setStatus("🔊 Speaking...", "waiting");
  utterance.onend   = () => checkHealth();
  utterance.onerror = (e) => console.error("Speech synthesis error:", e);
  speechSynthesis.speak(utterance);
}

if (speechSynthesis.onvoiceschanged !== undefined) {
  speechSynthesis.onvoiceschanged = () => speechSynthesis.getVoices();
}

// ============ INIT ============
checkHealth();
initSpeechRecognition();
updateCardsDueBadge();
// Poll badge every minute in case user keeps app open for a long time without refreshing
setInterval(updateCardsDueBadge, 60000);
