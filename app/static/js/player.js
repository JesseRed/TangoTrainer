// Lesson / Playlist Player
(function () {
  const video = document.getElementById("player-video");
  if (typeof ITEMS === "undefined" || ITEMS.length === 0) return;

  let current = 0;
  let currentLoop = 0;
  let pauseTimer = null;
  let ratingCallback = null;

  // ── WebSocket Remote Control ─────────────────────────────────────────────

  let wsConn = null;
  let wsDelay = 1000;

  function connectWS() {
    if (typeof SESSION_ID === "undefined") return;
    const proto = location.protocol === "https:" ? "wss:" : "ws:";
    wsConn = new WebSocket(`${proto}//${location.host}/ws/${SESSION_ID}`);
    wsConn.onopen = () => { wsDelay = 1000; };
    wsConn.onclose = () => {
      setTimeout(connectWS, wsDelay);
      wsDelay = Math.min(wsDelay * 2, 10000);
    };
    wsConn.onmessage = (ev) => {
      try {
        const msg = JSON.parse(ev.data);
        if (msg.type === "state") return;
        switch (msg.cmd) {
          case "next":       window.nextItem(); break;
          case "prev":       window.prevItem(); break;
          case "replay":     window.replayItem(); break;
          case "play_pause": window.togglePlay(); break;
          case "fullscreen": window.toggleFullscreen(); break;
          case "speed":      window.setSpeed(msg.value); break;
          case "rate":       if (msg.rating) handleRemoteRating(msg.rating); break;
        }
      } catch {}
    };
  }

  function wsBroadcast(msg) {
    if (wsConn && wsConn.readyState === 1) {
      wsConn.send(JSON.stringify(msg));
    }
  }

  connectWS();

  // ── Load an item ────────────────────────────────────────────────────────

  function loadItem(index) {
    if (pauseTimer) { clearInterval(pauseTimer); pauseTimer = null; }
    current = index;
    currentLoop = 0;
    const item = ITEMS[index];

    hidePauseOverlay();
    hideRatingOverlay();

    if (item.itemType === "text") {
      showTextItem(item);
    } else if (item.itemType === "audio") {
      showAudioItem(item);
    } else {
      showVideoItem(item);
    }
    updateUI(index);
    wsBroadcast({ type: "state", title: item.title, meta: `Block ${index + 1} von ${ITEMS.length}` });
  }

  function showVideoItem(item) {
    if (video) video.style.display = "";
    const audioEl = document.getElementById("player-audio");
    if (audioEl) { audioEl.pause(); audioEl.style.display = "none"; }
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
    const sel = document.getElementById("speed-select");
    if (sel) {
      const pct = Math.round((item.speed || 1.0) * 100);
      [...sel.options].forEach(o => { o.selected = parseInt(o.value * 100) === pct; });
    }
  }

  function showTextItem(item) {
    if (video) video.pause();
    if (video) video.style.display = "none";
    const audioEl = document.getElementById("player-audio");
    if (audioEl) { audioEl.pause(); audioEl.style.display = "none"; }
    const textEl = document.getElementById("player-text-item");
    textEl.style.display = "";
    document.getElementById("player-text-content").textContent = item.title;
    const parts = (item.textInstruction || "").split("\n\n");
    document.getElementById("player-text-body").textContent = parts.slice(1).join("\n\n") || parts[0] || "";
  }

  function showAudioItem(item) {
    if (video) { video.pause(); video.style.display = "none"; }
    document.getElementById("player-text-item").style.display = "none";
    const audioEl = document.getElementById("player-audio");
    if (!audioEl) { advanceOrStop(); return; }
    audioEl.style.display = "";
    audioEl.src = `/music/${item.audioId}/stream`;
    audioEl.playbackRate = item.speed || 1.0;
    audioEl.play().catch(() => {});
    audioEl.onended = () => advanceOrStop();
  }

  // ── timeupdate: handle clip end + loop/pause logic ──────────────────────

  if (video) {
    video.addEventListener("timeupdate", () => {
      const item = ITEMS[current];
      if (!item || item.itemType !== "clip") return;
      if (video.currentTime < item.end - 0.15) return;

      video.pause();
      currentLoop++;

      if (currentLoop < (item.loopCount || 1)) {
        updateLoopCounter(item);
        video.currentTime = item.start;
        video.play().catch(() => {});
      } else {
        const pause = item.pauseAfter || 0;
        if (pause > 0) {
          showPauseOverlay(pause, () => advanceOrStop());
        } else {
          advanceOrStop();
        }
      }
    });
  }

  function advanceOrStop() {
    hidePauseOverlay();
    const item = ITEMS[current];
    const doNext = () => {
      if (current + 1 < ITEMS.length) {
        loadItem(current + 1);
      } else {
        const btn = document.getElementById("btn-play-pause");
        if (btn) btn.textContent = "▶ Neu starten";
      }
    };
    if (item && item.itemType === "clip" && item.id) {
      showRatingOverlay(doNext);
    } else {
      doNext();
    }
  }

  // ── Rating overlay ──────────────────────────────────────────────────────

  function showRatingOverlay(callback) {
    ratingCallback = callback;
    const overlay = document.getElementById("rating-overlay");
    if (overlay) overlay.style.display = "";
  }

  function hideRatingOverlay() {
    const overlay = document.getElementById("rating-overlay");
    if (overlay) overlay.style.display = "none";
    ratingCallback = null;
  }

  window.submitRating = async function (rating) {
    const item = ITEMS[current];
    hideRatingOverlay();
    if (rating && item && item.id) {
      const fd = new FormData();
      fd.append("clip_id", item.id);
      if (typeof LESSON_ID !== "undefined" && LESSON_ID) fd.append("lesson_id", LESSON_ID);
      fd.append("rating", rating);
      fetch("/practice-log", { method: "POST", body: fd }).catch(() => {});
    }
    if (ratingCallback) { const cb = ratingCallback; ratingCallback = null; cb(); }
  };

  function handleRemoteRating(rating) {
    if (ratingCallback) {
      window.submitRating(rating);
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

    document.querySelectorAll(".playlist-item").forEach((el, i) => {
      el.classList.toggle("active", i === index);
    });
    document.getElementById(`playlist-item-${index}`)?.scrollIntoView({ block: "nearest" });
  }

  function updateLoopCounter(item) {
    const el = document.getElementById("player-loop-counter");
    if (!el) return;
    const total = item.loopCount || 1;
    if (total > 1 && item.itemType !== "text" && item.itemType !== "audio") {
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
    hideRatingOverlay();
    const item = ITEMS[current];
    if (item.itemType === "clip") {
      video.currentTime = item.start;
      video.play().catch(() => {});
      updateLoopCounter(item);
    } else if (item.itemType === "audio") {
      const audioEl = document.getElementById("player-audio");
      if (audioEl) { audioEl.currentTime = 0; audioEl.play().catch(() => {}); }
    }
  };
  window.goToItem = (index) => loadItem(index);
  window.togglePlay = () => {
    const btn = document.getElementById("btn-play-pause");
    const item = ITEMS[current];
    if (item?.itemType === "text") { window.nextItem(); return; }
    if (item?.itemType === "audio") {
      const audioEl = document.getElementById("player-audio");
      if (!audioEl) return;
      if (audioEl.paused) { audioEl.play(); if (btn) btn.textContent = "⏸ Pause"; }
      else                { audioEl.pause(); if (btn) btn.textContent = "▶ Abspielen"; }
      return;
    }
    if (!video) return;
    if (video.paused) { video.play(); if (btn) btn.textContent = "⏸ Pause"; }
    else              { video.pause(); if (btn) btn.textContent = "▶ Abspielen"; }
  };
  window.setSpeed = (val) => {
    const rate = parseFloat(val);
    if (video) video.playbackRate = rate;
    const audioEl = document.getElementById("player-audio");
    if (audioEl) audioEl.playbackRate = rate;
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
    const nav = document.querySelector("nav");
    if (nav) nav.style.display = document.fullscreenElement ? "none" : "";
  });

  // ── Keyboard shortcuts ──────────────────────────────────────────────────

  document.addEventListener("keydown", (ev) => {
    if (["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement?.tagName)) return;
    switch (ev.key) {
      case "ArrowRight": ev.preventDefault(); window.nextItem(); break;
      case "ArrowLeft":  ev.preventDefault(); window.prevItem(); break;
      case " ":          ev.preventDefault(); window.togglePlay(); break;
      case "r": case "R": ev.preventDefault(); window.replayItem(); break;
      case "f": case "F": ev.preventDefault(); window.toggleFullscreen(); break;
    }
  });

  // ── Start ───────────────────────────────────────────────────────────────
  loadItem(0);
})();
