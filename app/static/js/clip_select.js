// Floating action bar for multi-clip selection
(function () {
  const bar = document.getElementById("clip-action-bar");
  const countEl = document.getElementById("clip-action-count");
  const idsInput = document.getElementById("clip-action-ids");
  const form = document.getElementById("clip-action-form");
  const lessonSelect = document.getElementById("clip-lesson-select");

  if (!bar) return;

  window.updateSelection = function () {
    const checked = [...document.querySelectorAll(".clip-checkbox:checked")];
    if (checked.length > 0) {
      bar.style.display = "flex";
      countEl.textContent = `${checked.length} Clip${checked.length !== 1 ? "s" : ""} ausgewählt`;
      idsInput.value = checked.map(cb => cb.value).join(",");
    } else {
      bar.style.display = "none";
    }
  };

  window.clearSelection = function () {
    document.querySelectorAll(".clip-checkbox:checked").forEach(cb => cb.checked = false);
    bar.style.display = "none";
  };

  form.addEventListener("submit", function (ev) {
    ev.preventDefault();
    const lessonId = lessonSelect.value;
    const clipIds = idsInput.value;
    if (!clipIds) return;

    if (lessonId === "new") {
      // Redirect to new lesson form with clip_ids pre-filled
      window.location.href = `/lessons/new?clip_ids=${encodeURIComponent(clipIds)}`;
    } else {
      // Submit to bulk-add endpoint
      const f = document.createElement("form");
      f.method = "post";
      f.action = `/lessons/${lessonId}/items/bulk`;
      clipIds.split(",").forEach(id => {
        const inp = document.createElement("input");
        inp.type = "hidden"; inp.name = "clip_ids"; inp.value = id;
        f.appendChild(inp);
      });
      document.body.appendChild(f);
      f.submit();
    }
  });
})();
