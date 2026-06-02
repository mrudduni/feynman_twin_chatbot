const API_BASE = "http://127.0.0.1:8000";

const statusEl = document.getElementById("status");
const chatEl = document.getElementById("chat");
const formEl = document.getElementById("chat-form");
const inputEl = document.getElementById("question-input");
const sendBtn = document.getElementById("send-btn");
const lengthSelector = document.getElementById("answer-length");
const voiceInputBtn = document.getElementById("voice-input-btn");
const voiceToggleBtn = document.getElementById("voice-toggle-btn");

// Voice interaction state
let recognition = null;
let isRecording = false;
let voiceOutputEnabled = true;
let speechSynthesis = window.speechSynthesis;

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
  
  // Speak the message if it's from the bot and voice output is enabled
  if (role === "bot" && voiceOutputEnabled) {
    speakText(text);
  }
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

  const answerLength = lengthSelector.value;
  addMessage("user", question);
  inputEl.value = "";
  sendBtn.disabled = true;

  try {
    const response = await fetch(`${API_BASE}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, answer_length: answerLength }),
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

// ============ VOICE INTERACTION FUNCTIONS ============

// Initialize speech recognition
function initSpeechRecognition() {
  if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
      isRecording = true;
      voiceInputBtn.classList.add('recording');
      setStatus("🎤 Listening...", "waiting");
    };

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      inputEl.value = transcript;
      setStatus("Voice input captured", "ok");
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      setStatus(`Voice input error: ${event.error}`, "error");
      isRecording = false;
      voiceInputBtn.classList.remove('recording');
    };

    recognition.onend = () => {
      isRecording = false;
      voiceInputBtn.classList.remove('recording');
    };
  } else {
    console.warn('Speech recognition not supported');
    voiceInputBtn.disabled = true;
    voiceInputBtn.title = "Speech recognition not supported in this browser";
  }
}

// Start/stop voice input
voiceInputBtn.addEventListener('click', () => {
  if (!recognition) {
    initSpeechRecognition();
  }

  if (isRecording) {
    recognition.stop();
  } else {
    try {
      recognition.start();
    } catch (error) {
      console.error('Error starting recognition:', error);
    }
  }
});

// Toggle voice output
voiceToggleBtn.addEventListener('click', () => {
  voiceOutputEnabled = !voiceOutputEnabled;
  voiceToggleBtn.textContent = voiceOutputEnabled ? '🔊' : '🔇';
  voiceToggleBtn.classList.toggle('active', voiceOutputEnabled);
  
  // Stop any ongoing speech
  if (!voiceOutputEnabled) {
    speechSynthesis.cancel();
  }
  
  setStatus(
    voiceOutputEnabled ? "Voice output enabled" : "Voice output disabled",
    "ok"
  );
  setTimeout(() => checkHealth(), 2000);
});

// Text-to-speech function
function speakText(text) {
  if (!voiceOutputEnabled) return;
  
  // Cancel any ongoing speech
  speechSynthesis.cancel();
  
  const utterance = new SpeechSynthesisUtterance(text);
  
  // Try to find a suitable voice (prefer US English male voice for Feynman)
  const voices = speechSynthesis.getVoices();
  const preferredVoice = voices.find(voice => 
    voice.lang.startsWith('en') && voice.name.includes('Male')
  ) || voices.find(voice => voice.lang.startsWith('en-US')) || voices[0];
  
  if (preferredVoice) {
    utterance.voice = preferredVoice;
  }
  
  utterance.rate = 0.95; // Slightly slower for clarity
  utterance.pitch = 1.0;
  utterance.volume = 1.0;
  
  utterance.onstart = () => {
    setStatus("🔊 Speaking...", "waiting");
  };
  
  utterance.onend = () => {
    checkHealth();
  };
  
  utterance.onerror = (event) => {
    console.error('Speech synthesis error:', event);
  };
  
  speechSynthesis.speak(utterance);
}

// Load voices when available (some browsers load them asynchronously)
if (speechSynthesis.onvoiceschanged !== undefined) {
  speechSynthesis.onvoiceschanged = () => {
    speechSynthesis.getVoices();
  };
}

// Initialize speech recognition on page load
initSpeechRecognition();
