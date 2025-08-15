const recordBtn = document.getElementById("recordBtn");
const statusEl = document.getElementById("status");
const transcriptEl = document.getElementById("transcript");
const aiResponseEl = document.getElementById("aiResponse");
const audioPlayer = document.getElementById("audioPlayer");
const historyEl = document.getElementById("history");
const clearBtn = document.getElementById("clearHistoryBtn");

let recorder;
let chunks = [];

// Session handling via URL ?session=...
const urlParams = new URLSearchParams(window.location.search);
let sessionId = urlParams.get("session") || crypto.randomUUID();
if (!urlParams.get("session")) {
  urlParams.set("session", sessionId);
  window.history.replaceState({}, "", `${location.pathname}?${urlParams}`);
}

recordBtn.onclick = () => {
  if (!recorder || recorder.state === "inactive") {
    startRecording();
  } else {
    stopRecording();
  }
};

async function startRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    recorder = new MediaRecorder(stream);
    chunks = [];
    recorder.ondataavailable = (e) => chunks.push(e.data);
    recorder.onstop = sendAudio;
    recorder.start();
    statusEl.textContent = "🎙️ Recording...";
    recordBtn.textContent = "⏹ Stop Recording";
    recordBtn.classList.add("recording");
  } catch (err) {
    console.error(err);
    statusEl.textContent = "Mic access denied.";
  }
}

function stopRecording() {
  if (recorder && recorder.state !== "inactive") {
    recorder.stop();
    statusEl.textContent = "Processing…";
    recordBtn.textContent = "🎤 Start Recording";
    recordBtn.classList.remove("recording");
  }
}

async function sendAudio() {
  const blob = new Blob(chunks, { type: "audio/webm" });
  const formData = new FormData();
  formData.append("audio", blob, "audio.webm"); // ✅ backend expects 'audio'

  try {
    const resp = await fetch(`/agent/chat/${sessionId}`, {
      method: "POST",
      body: formData
    });

    let data;
    try {
      data = await resp.json();
    } catch {
      throw new Error("Server returned invalid JSON");
    }

    if (!resp.ok) {
      throw new Error(data.error || "Server error");
    }

    // ✅ keys match backend JSON
    transcriptEl.textContent = data.transcript || "(No transcript)";
    aiResponseEl.textContent = data.ai_response || "(No AI response)";
    historyEl.textContent = data.history || "(No chat history yet)";

    if (data.audio_url) {
      audioPlayer.src = data.audio_url;
      audioPlayer.play().catch(() => {});
      audioPlayer.onended = () => startRecording();
    } else {
      audioPlayer.removeAttribute("src");
    }

    statusEl.textContent = "Ready";
  } catch (err) {
    console.error(err);
    transcriptEl.textContent = "(Error: could not get transcript)";
    aiResponseEl.textContent = "(Error: could not get AI response)";
    historyEl.textContent = "(Error loading chat history)";
    statusEl.textContent = "⚠️ Error occurred. Please try again.";
  }
}

// Clear chat history
clearBtn.onclick = async () => {
  if (!confirm("Are you sure you want to clear the chat history?")) return;
  try {
    const resp = await fetch(`/agent/clear/${sessionId}`, { method: "POST" });
    const data = await resp.json();
    if (data.ok) {
      historyEl.textContent = "(No chat history yet)";
      transcriptEl.textContent = "(No transcript)";
      aiResponseEl.textContent = "(No AI response)";
      audioPlayer.src = "";
      statusEl.textContent = "Chat history cleared.";
    } else {
      alert("Failed to clear chat history.");
    }
  } catch {
    alert("Failed to clear chat history.");
  }
};
