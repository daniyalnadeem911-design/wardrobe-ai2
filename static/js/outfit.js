let selectedItemIds = new Set();

function getSelectedOccasion() {
  const customInput = document.getElementById("custom-occasion-input");
  const typed = customInput ? customInput.value.trim() : "";
  if (typed) return typed;
  const activeChip = document.querySelector(".chip-btn.selected");
  return activeChip ? activeChip.dataset.occasion : null;
}

function checkReady() {
  const btn = document.getElementById("generate-btn");
  if (btn) btn.disabled = !getSelectedOccasion();
}

document.querySelectorAll(".chip-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".chip-btn").forEach((b) => b.classList.remove("selected"));
    btn.classList.add("selected");
    const customInput = document.getElementById("custom-occasion-input");
    if (customInput) customInput.value = "";
    checkReady();
  });
});

const customOccasionInput = document.getElementById("custom-occasion-input");
if (customOccasionInput) {
  // Listening on 3 events instead of just "input" — some mobile/in-app
  // browsers (Facebook/Instagram's built-in browser especially) don't fire
  // "input" reliably on every keystroke.
  ["input", "keyup", "change"].forEach((evt) => {
    customOccasionInput.addEventListener(evt, () => {
      if (customOccasionInput.value.trim()) {
        document.querySelectorAll(".chip-btn").forEach((b) => b.classList.remove("selected"));
      }
      checkReady();
    });
  });
}

const availableGrids = {
  Upper: document.getElementById("available-items-upper"),
  Lower: document.getElementById("available-items-lower"),
  Footwear: document.getElementById("available-items-footwear"),
  Accessories: document.getElementById("available-items-accessories"),
};
const availableContainer = document.getElementById("available-items-container");

if (availableContainer) {
  fetch("/api/wardrobe").then(r => r.json()).then(data => {
    (data.items || []).forEach((item) => {
      const targetGrid = availableGrids[item.section] || availableGrids.Accessories;
      if (!targetGrid) return;

      const card = document.createElement("label");
      card.className = "card item-card";
      card.style.cursor = "pointer";
      card.innerHTML = `
        <input type="checkbox" data-id="${item.id}" style="margin-bottom:8px;" />
        ${item.image_path ? `<img src="${item.image_path}" alt="${item.name}" />` : ""}
        <h4>${item.name || item.category}</h4>
        <p class="subtle">${item.category} • ${item.color}</p>
      `;
      const checkbox = card.querySelector("input");
      checkbox.addEventListener("change", () => {
        if (checkbox.checked) selectedItemIds.add(item.id);
        else selectedItemIds.delete(item.id);
      });
      targetGrid.appendChild(card);
    });
  });

  document.getElementById("select-all-btn").onclick = () => {
    availableContainer.querySelectorAll('input[type="checkbox"]').forEach(cb => {
      cb.checked = true;
      selectedItemIds.add(parseInt(cb.dataset.id));
    });
  };
  document.getElementById("clear-all-btn").onclick = () => {
    availableContainer.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = false);
    selectedItemIds.clear();
  };
}

const generateBtn = document.getElementById("generate-btn");
if (generateBtn) {
  generateBtn.addEventListener("click", async () => {
    const occasion = getSelectedOccasion();
    if (!occasion) return;

    generateBtn.disabled = true;
    generateBtn.textContent = "Styling your outfit...";

    const res = await fetch("/api/outfit/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        occasion: occasion,
        available_item_ids: Array.from(selectedItemIds),
      }),
    });
    const data = await res.json();

    if (!data.success) {
      alert(data.error);
      generateBtn.disabled = false;
      generateBtn.textContent = "Generate Outfit";
      return;
    }

    sessionStorage.setItem("lastOutfit", JSON.stringify(data));
    window.location.href = "/outfit-result";
  });
}

const outfitGrid = document.getElementById("outfit-grid");
if (outfitGrid) {
  const data = JSON.parse(sessionStorage.getItem("lastOutfit") || "{}");
  const weatherEl = document.getElementById("weather-summary");
  if (weatherEl && data.weather) {
    weatherEl.textContent = `${data.weather.season} weather • ${data.weather.temperature ?? "--"}°C`;
  }
  const occasionEl = document.getElementById("occasion-summary");
  if (occasionEl && data.occasion) {
    occasionEl.textContent = `Occasion: ${data.occasion}`;
  }
  const reasoningEl = document.getElementById("overall-reasoning");
  if (reasoningEl && data.overall_reasoning) {
    reasoningEl.textContent = data.overall_reasoning;
  }
  (data.items || []).forEach((item) => {
    const card = document.createElement("div");
    card.className = "card item-card";
    card.innerHTML = `
      ${item.image_path ? `<img src="${item.image_path}" alt="${item.name}" />` : ""}
      <h4>${item.name || item.category}</h4>
      <p class="subtle">${item.category} • ${item.color}</p>
      <p class="reason">${item.reason || ""}</p>
    `;
    outfitGrid.appendChild(card);
  });
  document.getElementById("favorite-btn").onclick = async () => {
    await fetch(`/api/outfit/${data.outfit_id}/favorite`, { method: "POST" });
    alert("Saved to favorites!");
  };
  document.getElementById("wear-btn").onclick = async () => {
    await fetch(`/api/outfit/${data.outfit_id}/wear`, { method: "POST" });
    alert("Marked as worn today!");
  };
}