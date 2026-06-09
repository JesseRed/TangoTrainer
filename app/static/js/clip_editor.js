// Clip-Editor: Start/Ende-Marking während Wiedergabe
(function () {
  const video = document.getElementById("clip-video");
  const startInput = document.getElementById("start_seconds");
  const endInput = document.getElementById("end_seconds");
  const startDisplay = document.getElementById("start-display");
  const endDisplay = document.getElementById("end-display");
  const previewBtn = document.getElementById("preview-clip");

  if (!video) return;

  function fmt(s) {
    const m = Math.floor(s / 60);
    const sec = (s % 60).toFixed(1).padStart(4, "0");
    return `${m}:${sec}`;
  }

  function setStart() {
    const t = video.currentTime;
    startInput.value = t.toFixed(2);
    if (startDisplay) startDisplay.textContent = fmt(t);
  }

  function setEnd() {
    const t = video.currentTime;
    endInput.value = t.toFixed(2);
    if (endDisplay) endDisplay.textContent = fmt(t);
  }

  document.getElementById("btn-set-start")?.addEventListener("click", setStart);
  document.getElementById("btn-set-end")?.addEventListener("click", setEnd);

  // Keyboard shortcuts: S = start, E = end, Space = play/pause
  document.addEventListener("keydown", (ev) => {
    // Only when video element is on the page and not focused in a text input
    if (["INPUT", "TEXTAREA"].includes(document.activeElement?.tagName)) return;
    if (ev.key === "s" || ev.key === "S") { ev.preventDefault(); setStart(); }
    if (ev.key === "e" || ev.key === "E") { ev.preventDefault(); setEnd(); }
  });

  // Preview clip button: jump to start and play until end
  previewBtn?.addEventListener("click", () => {
    const start = parseFloat(startInput.value) || 0;
    const end = parseFloat(endInput.value) || video.duration;
    video.currentTime = start;
    video.play();

    const stopAt = (ev) => {
      if (video.currentTime >= end) {
        video.pause();
        video.removeEventListener("timeupdate", stopAt);
      }
    };
    video.addEventListener("timeupdate", stopAt);
  });

  // Update time display continuously
  video.addEventListener("timeupdate", () => {
    const cur = document.getElementById("current-time");
    if (cur) cur.textContent = fmt(video.currentTime);
  });
})();
