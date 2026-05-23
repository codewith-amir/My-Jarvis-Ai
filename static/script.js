// ============================================
// JARVIS - Frontend JavaScript
// Handles chat, voice input, reminders UI
// ============================================

let isRecording = false;
let recognition = null;

// ====== On Page Load ======
window.addEventListener("DOMContentLoaded", () => {
  updateClock();
  setInterval(updateClock, 1000);
  const ui = document.getElementById("user-input");
  if (ui) ui.focus();
  const cmd = document.getElementById("command-input");
  if (cmd) {
    cmd.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') { e.preventDefault(); sendConsoleCommand(); }
    });
  }
});

// ====== Live Clock ======
function updateClock() {
  const now = new Date();
  const timeStr = now.toLocaleTimeString("en-PK", {
    hour: "2-digit", minute: "2-digit", second: "2-digit"
  });
  const dateStr = now.toLocaleDateString("en-PK", {
    weekday: "short", day: "numeric", month: "short"
  });
  const el = document.getElementById("current-time");
  if (el) el.textContent = `${dateStr}  ${timeStr}`;
}

// ====== Send Message (main function) ======
async function sendMessage() {
  const input = document.getElementById("user-input");
  const message = input.value.trim();
  if (!message) return;

  // Clear input
  input.value = "";
  autoResize(input);

  // Remove welcome card if present
  const welcome = document.querySelector(".welcome-card");
  if (welcome) welcome.remove();

  // Show user message
  appendMessage("user", message);

  // Show typing indicator
  const typingId = showTyping();

  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message })
    });

    const data = await response.json();
    removeTyping(typingId);

    if (data.reply) {
      appendMessage("ai", data.reply);

      // If reminders were listed, also show panel
      if (message.toLowerCase().includes("remind") &&
          message.toLowerCase().includes("show")) {
        loadRemindersPanel();
      }
    } else {
      appendMessage("ai", "Kuch error aya. Dobara try karo.");
    }

  } catch (err) {
    removeTyping(typingId);
    appendMessage("ai", "⚠️ Server se connect nahi ho saka.\nKya Jarvis chal raha hai? Terminal check karo.");
  }
}

// ====== Append a message bubble ======
function appendMessage(role, text) {
  const chatArea = document.getElementById("chat-area");

  const row = document.createElement("div");
  row.className = `message-row ${role}`;

  const avatar = document.createElement("div");
  avatar.className = `avatar ${role}`;
  avatar.textContent = role === "ai" ? "J" : "👤";

  const bubble = document.createElement("div");
  bubble.className = `bubble ${role}`;
  bubble.textContent = text;

  row.appendChild(avatar);
  row.appendChild(bubble);
  chatArea.appendChild(row);
  chatArea.scrollTop = chatArea.scrollHeight;
}

// ====== Typing Indicator ======
function showTyping() {
  const chatArea = document.getElementById("chat-area");
  const id = "typing-" + Date.now();

  const row = document.createElement("div");
  row.className = "message-row ai";
  row.id = id;

  const avatar = document.createElement("div");
  avatar.className = "avatar ai";
  avatar.textContent = "J";

  const bubble = document.createElement("div");
  bubble.className = "typing-bubble";
  bubble.innerHTML = `
    <div class="typing-dot"></div>
    <div class="typing-dot"></div>
    <div class="typing-dot"></div>
  `;

  row.appendChild(avatar);
  row.appendChild(bubble);
  chatArea.appendChild(row);
  chatArea.scrollTop = chatArea.scrollHeight;
  return id;
}

function removeTyping(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

// ====== Quick Command Buttons ======
function sendQuick(text) {
  document.getElementById("user-input").value = text;
  sendMessage();
}

// ====== Focus and type partial text ======
function focusAndType(text) {
  const input = document.getElementById("user-input");
  input.value = text;
  input.focus();
  autoResize(input);
}

// ====== Enter key handler ======
function handleKey(event) {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendMessage();
  }
}

// ====== Auto resize textarea ======
function autoResize(el) {
  el.style.height = "auto";
  el.style.height = Math.min(el.scrollHeight, 120) + "px";
}

// ====== Clear Chat ======
async function clearChat() {
  if (!confirm("Chat history clear karna hai?")) return;

  await fetch("/clear", { method: "POST" });

  const chatArea = document.getElementById("chat-area");
  chatArea.innerHTML = `
    <div class="welcome-card">
      <div class="welcome-icon">🤖</div>
      <h2>Chat clear ho gaya!</h2>
      <p>Naya conversation shuru karo.</p>
      <div class="welcome-chips">
        <span class="chip" onclick="sendQuick('What can you do?')">What can you do?</span>
        <span class="chip" onclick="sendQuick('What is the weather in Lahore?')">Lahore weather?</span>
      </div>
    </div>
  `;
}

// ====== Load Reminders Panel ======
async function loadRemindersPanel() {
  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: "show reminders" })
    });
    const data = await res.json();

    // Parse and show in panel
    const panel = document.getElementById("reminders-panel");
    const list = document.getElementById("reminders-list");
    list.innerHTML = "";

    if (data.reply.includes("koi reminders nahi")) {
      list.innerHTML = `<p style="color:var(--text-muted);font-size:13px;">Abhi koi reminders nahi hain.</p>`;
    } else {
      const lines = data.reply.split("\n").filter(l => /^\d+\./.test(l));
      lines.forEach((line, i) => {
        const item = document.createElement("div");
        item.className = "reminder-item";
        item.innerHTML = `
          <span>${line}</span>
          <button onclick="deleteReminder(${i})" title="Delete">🗑️</button>
        `;
        list.appendChild(item);
      });
    }

    panel.style.display = "block";
  } catch (e) {
    console.error("Reminders load error:", e);
  }
}

// ====== Delete a Reminder ======
async function deleteReminder(index) {
  await fetch("/delete_reminder", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ index })
  });
  loadRemindersPanel(); // Refresh panel
  appendMessage("ai", "✅ Reminder delete ho gaya!");
}

// ====== Voice Input ======
function toggleVoice() {
  if (!("webkitSpeechRecognition" in window) && !("SpeechRecognition" in window)) {
    appendMessage("ai", "⚠️ Tera browser voice input support nahi karta.\nChrome browser use karo voice ke liye.");
    return;
  }

  if (isRecording) {
    stopVoice();
    return;
  }

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new SpeechRecognition();
  recognition.lang = "en-US";
  recognition.continuous = false;
  recognition.interimResults = false;

  recognition.onstart = () => {
    isRecording = true;
    document.getElementById("mic-btn").classList.add("recording");
    document.getElementById("mic-btn").textContent = "🔴";
  };

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    document.getElementById("user-input").value = transcript;
    stopVoice();
    sendMessage();
  };

  recognition.onerror = () => stopVoice();
  recognition.onend = () => stopVoice();
  recognition.start();
}

function stopVoice() {
  isRecording = false;
  const btn = document.getElementById("mic-btn");
  btn.classList.remove("recording");
  btn.textContent = "🎤";
  if (recognition) recognition.stop();
}

// ====== Dashboard Console Helpers ======
function sendConsoleCommand() {
  const input = document.getElementById("command-input");
  if (!input) return;
  const txt = input.value.trim();
  if (!txt) return;
  appendConsoleLog('user', txt);
  input.value = '';
  // simulate AI response
  setTimeout(() => {
    appendConsoleLog('ai', 'Acknowledged. Processing "' + txt + '"');
  }, 500);
}

function appendConsoleLog(role, text) {
  const log = document.getElementById("command-log");
  if (!log) return;
  const div = document.createElement('div');
  div.className = 'log-line ' + (role === 'user' ? 'user' : 'ai');
  div.textContent = (role === 'user' ? '> USER: ' : '> JARVIS: ') + text;
  log.appendChild(div);
  log.scrollTop = log.scrollHeight;
}
