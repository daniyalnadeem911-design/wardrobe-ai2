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
    generateBtn.textContent = "Styling your outfits...";

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

// v9: outfit_result.html now shows up to 3 option cards instead of one grid.
const optionsContainer = document.getElementById("options-container");
if (optionsContainer) {
  const data = JSON.parse(sessionStorage.getItem("lastOutfit") || "{}");

  const weatherEl = document.getElementById("weather-summary");
  if (weatherEl && data.weather) {
    weatherEl.textContent = `${data.weather.season} weather • ${data.weather.temperature ?? "--"}°C`;
  }
  const occasionEl = document.getElementById("occasion-summary");
  if (occasionEl && data.occasion) {
    occasionEl.textContent = `Occasion: ${data.occasion}`;
  }

  (data.options || []).forEach((option, index) => {
    const optionCard = document.createElement("section");
    optionCard.className = "card option-card";
    optionCard.style.marginTop = "20px";

    const itemsHtml = (option.items || []).map(item => `
      <div class="card item-card">
        ${item.image_path ? `<img src="${item.image_path}" alt="${item.name}" />` : ""}
        <h4>${item.name || item.category}</h4>
        <p class="subtle">${item.category} • ${item.color}</p>
        <p class="reason">${item.reason || ""}</p>
      </div>
    `).join("");

    optionCard.innerHTML = `
      <h3>Option ${index + 1}${index === 0 ? " (Best Match)" : ""}</h3>
      <p class="overall-reasoning">${option.overall_reasoning || ""}</p>
      <div class="card-grid">${itemsHtml}</div>
      <div class="actions">
        <button class="btn-primary choose-btn">Choose This Outfit</button>
      </div>
    `;

    const chooseBtn = optionCard.querySelector(".choose-btn");
    chooseBtn.addEventListener("click", async () => {
      chooseBtn.disabled = true;
      chooseBtn.textContent = "Saving...";

      const res = await fetch("/api/outfit/choose", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          occasion: data.occasion,
          weather: data.weather,
          upper_id: option.upper_id,
          lower_id: option.lower_id,
          footwear_id: option.footwear_id,
          accessory_id: option.accessory_id,
          jacket_id: option.jacket_id,
          reasoning: option.reasoning,
        }),
      });
      const chosen = await res.json();

      if (!chosen.success) {
        alert("Could not save this outfit. Please try again.");
        chooseBtn.disabled = false;
        chooseBtn.textContent = "Choose This Outfit";
        return;
      }

      const actions = optionCard.querySelector(".actions");
      actions.innerHTML = `
        <button class="btn-secondary favorite-btn">♥ Save to Favorites</button>
        <button class="btn-primary wear-btn">Mark as Worn</button>
      `;
      actions.querySelector(".favorite-btn").onclick = async () => {
        await fetch(`/api/outfit/${chosen.outfit_id}/favorite`, { method: "POST" });
        alert("Saved to favorites!");
      };
      actions.querySelector(".wear-btn").onclick = async () => {
        await fetch(`/api/outfit/${chosen.outfit_id}/wear`, { method: "POST" });
        alert("Marked as worn today!");
      };
    });

    optionsContainer.appendChild(optionCard);
  });
}