// Lesson / Playlist Player
(function () {
  const video = document.getElementById("player-video");
  if (!video || typeof ITEMS === "undefined" || ITEMS.length === 0) return;

  let current = 0;
  let currentLoop = 0;
  let pauseTimer = null;

  // ── Load an item ────────────────────────────────────────────────────────

  function loadItem(index) {
    if (pauseTimer) { clearInterval(pauseTimer); pauseTimer = null; }
    current = index;
    currentLoop = 0;
    const item = ITEMS[index];

    hidePauseOverlay();

    if (item.itemType === "text") {
      showTextItem(item);
    } else {
      showVideoItem(item);
    }
    updateUI(index);
  }

  function showVideoItem(item) {
    document.getElementById("player-video").style.display = "";
    document.getElementById("player-text-item").style.display = "none";

    const src = `/videos/${item.videoId}/stream`;
    if (video.getAttribute("src") !== src) {
      video.src = src;
      video.load();
    }
    video.playbackRate = item.speed || 1.0;

    const seekAndPlay = () => {
      video.currentTime = item.start;
      video.play().catch(() => {});
    };
    if (video.readyState >= 2) {
      seekAndPlay();
    } else {
      video.addEventListener("canplay", seekAndPlay, { once: true });
    }
    // Sync speed selector
    const sel = document.getElementById("speed-select");
    if (sel) {
      const pct = Math.round((item.speed || 1.0) * 100);
      // find closest option
      [...sel.options].forEach(o => { o.selected = parseInt(o.value * 100) === pct; });
    }
  }

  function showTextItem(item) {
    video.pause();
    document.getElementById("player-video").style.display = "none";
    const textEl = document.getElementById("player-text-item");
    textEl.style.display = "";
    document.getElementById("player-text-content").textContent = item.title;
    const parts = (item.textInstruction || "").split("\n\n");
    document.getElementById("player-text-body").textContent = parts.slice(1).join("\n\n") || parts[0] || "";
  }

  // ── timeupdate: handle clip end + loop/pause logic ──────────────────────

  video.addEventListener("timeupdate", () => {
    const item = ITEMS[current];
    if (!item || item.itemType === "text") return;
    if (video.currentTime < item.end - 0.15) return;

    video.pause();
    currentLoop++;

    if (currentLoop < (item.loopCount || 1)) {
      updateLoopCounter(item);
      video.currentTime = item.start;
      video.play().catch(() => {});
    } else {
      // All loops done — handle pause then advance
      const pause = item.pauseAfter || 0;
      if (pause > 0) {
        showPauseOverlay(pause, () => advanceOrStop());
      } else {
        advanceOrStop();
      }
    }
  });

  function advanceOrStop() {
    hidePauseOverlay();
    if (current + 1 < ITEMS.length) {
      loadItem(current + 1);
    } else {
      // Playlist done
      document.getElementById("btn-play-pause").textContent = "▶ Neu starten";
    }
  }

  // ── Pause overlay with countdown ────────────────────────────────────────

  function showPauseOverlay(seconds, callback) {
    const overlay = document.getElementById("pause-overlay");
    const countdown = document.getElementById("pause-countdown");
    if (!overlay) { callback(); return; }
    overlay.style.display = "";
    let remaining = seconds;
    countdown.textContent = `${remaining}s`;
    pauseTimer = setInterval(() => {
      remaining--;
      countdown.textContent = remaining > 0 ? `${remaining}s` : "";
      if (remaining <= 0) {
        clearInterval(pauseTimer);
        pauseTimer = null;
        overlay.style.display = "none";
        callback();
      }
    }, 1000);
  }

  function hidePauseOverlay() {
    const overlay = document.getElementById("pause-overlay");
    if (overlay) overlay.style.display = "none";
    if (pauseTimer) { clearInterval(pauseTimer); pauseTimer = null; }
  }

  // ── UI updates ──────────────────────────────────────────────────────────

  function updateUI(index) {
    const item = ITEMS[index];
    document.getElementById("player-title").textContent = item.title;
    document.getElementById("player-counter").textContent =
      `Block ${index + 1} von ${ITEMS.length}`;

    updateLoopCounter(item);

    const tagsEl = document.getElementById("player-tags");
    if (tagsEl) {
      tagsEl.innerHTML = (item.tags || []).map(t =>
        `<span class="tag-chip" style="border-color:${t.color};color:${t.color};">${t.name}</span>`
      ).join("");
    }

    // Notes
    const notesDetails = document.getElementById("player-notes-details");
    const notesEl = document.getElementById("player-notes");
    if (notesDetails && notesEl) {
      const hasNotes = item.notes || item.technicalNotes || item.adaptationNotes;
      notesDetails.style.display = (hasNotes && item.showNotes) ? "" : "none";
      if (hasNotes) {
        let html = "";
        if (item.notes) html += `<p>${item.notes}</p>`;
        if (item.technicalNotes) html += `<p style="margin-top:.4rem;color:#aaa;"><em>Technik:</em> ${item.technicalNotes}</p>`;
        if (item.adaptationNotes) html += `<p style="margin-top:.4rem;color:#aaa;"><em>Für uns:</em> ${item.adaptationNotes}</p>`;
        notesEl.innerHTML = html;
      }
    }

    // Playlist
    document.querySelectorAll(".playlist-item").forEach((el, i) => {
      el.classList.toggle("active", i === index);
    });
    document.getElementById(`playlist-item-${index}`)?.scrollIntoView({ block: "nearest" });
  }

  function updateLoopCounter(item) {
    const el = document.getElementById("player-loop-counter");
    if (!el) return;
    const total = item.loopCount || 1;
    if (total > 1 && item.itemType !== "text") {
      el.textContent = `Wiederholung ${currentLoop + 1} von ${total}`;
    } else {
      el.textContent = "";
    }
  }

  // ── Public controls ─────────────────────────────────────────────────────

  window.nextItem = () => {
    if (current + 1 < ITEMS.length) loadItem(current + 1);
  };
  window.prevItem = () => {
    if (current > 0) loadItem(current - 1);
  };
  window.replayItem = () => {
    currentLoop = 0;
    hidePauseOverlay();
    const item = ITEMS[current];
    if (item.itemType !== "text") {
      video.currentTime = item.start;
      video.play().catch(() => {});
      updateLoopCounter(item);
    }
  };
  window.goToItem = (index) => loadItem(index);
  window.togglePlay = () => {
    const btn = document.getElementById("btn-play-pause");
    if (ITEMS[current]?.itemType === "text") {
      nextItem(); return;
    }
    if (video.paused) { video.play(); btn.textContent = "⏸ Pause"; }
    else              { video.pause(); btn.textContent = "▶ Abspielen"; }
  };
  window.setSpeed = (val) => {
    const rate = parseFloat(val);
    video.playbackRate = rate;
    if (ITEMS[current]) ITEMS[current].speed = rate;
  };

  // ── Fullscreen ──────────────────────────────────────────────────────────

  window.toggleFullscreen = () => {
    const root = document.getElementById("player-root") || document.documentElement;
    if (!document.fullscreenElement) {
      root.requestFullscreen().catch(() => {});
    } else {
      document.exitFullscreen();
    }
  };

  document.addEventListener("fullscreenchange", () => {
    const root = document.getElementById("player-root");
    if (root) root.classList.toggle("is-fullscreen", !!document.fullscreenElement);
    // Hide nav in fullscreen
    const nav = document.querySelector("nav");
    if (nav) nav.style.display = document.fullscreenElement ? "none" : "";
  });

  // ── Keyboard shortcuts ──────────────────────────────────────────────────

  document.addEventListener("keydown", (ev) => {
    if (["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement?.tagName)) return;
    switch (ev.key) {
      case "ArrowRight": ev.preventDefault(); nextItem(); break;
      case "ArrowLeft":  ev.preventDefault(); prevItem(); break;
      case " ":          ev.preventDefault(); togglePlay(); break;
      case "r": case "R": ev.preventDefault(); replayItem(); break;
      case "f": case "F": ev.preventDefault(); toggleFullscreen(); break;
    }
  });

  // ── Start ───────────────────────────────────────────────────────────────
  loadItem(0);
})();
