const BACKEND_URL = "http://<YOUR_BACKEND_IP_OR_DOMAIN>:5000/ask";

const startBtn = document.getElementById("startBtn");
const questionEl = document.getElementById("question");
const answerEl   = document.getElementById("answer");
const latencyEl  = document.getElementById("latency");

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
if (!SpeechRecognition) alert("Use Chrome or Edge for voice support.");

const rec = new SpeechRecognition();
rec.lang = "en-US";
rec.interimResults = false;
rec.maxAlternatives = 1;
rec.continuous = false;

let processing = false;

rec.onresult = async (e) => {
    const text = e.results[0][0].transcript.trim();
    if (!text) return;

    questionEl.innerText = "Q: " + text;
    answerEl.innerText = "Thinking...";

    processing = true;
    const startTime = performance.now();

    try {
        const res = await fetch(BACKEND_URL, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ text })
        });
        const data = await res.json();
        answerEl.innerText = "A: " + data.answer;
        const latency = ((performance.now() - startTime) / 1000).toFixed(2);
        latencyEl.innerText = `Latency: ${latency}s`;
    } catch (err) {
        answerEl.innerText = "Error connecting to backend";
    }

    processing = false;
};

rec.onerror = (e) => console.log("Speech error:", e.error);
rec.onend = () => {
    if (!processing) setTimeout(() => rec.start(), 500);
};

startBtn.onclick = () => {
    rec.start();
    startBtn.innerText = "Listening…";
    startBtn.disabled = true;
};
