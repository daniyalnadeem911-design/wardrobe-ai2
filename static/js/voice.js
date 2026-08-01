const micBtn = document.getElementById("mic-btn");
const transcriptEl = document.getElementById("voice-transcript");

if (micBtn && "webkitSpeechRecognition" in window) {
  const recognition = new webkitSpeechRecognition();
  recognition.continuous = false;
  recognition.lang = "en-US";

  micBtn.addEventListener("click", () => {
    transcriptEl.textContent = "Listening...";
    recognition.start();
  });

  recognition.onresult = (event) => {
    const text = event.results[0][0].transcript;
    transcriptEl.textContent = `You said: "${text}"`;

    // Simple keyword match against known occasions
    const known = ["casual", "office", "wedding", "gym", "date", "party", "university", "traditional"];
    const match = known.find((k) => text.toLowerCase().includes(k));
    if (match) {
      const btn = document.querySelector(`.chip-btn[data-occasion*="${match}" i]`);
      if (btn) btn.click();
    }
  };

  recognition.onerror = () => {
    transcriptEl.textContent = "Couldn't hear that — please try again or pick an occasion above.";
  };
} else if (micBtn) {
  micBtn.style.display = "none";
}