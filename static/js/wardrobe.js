const imageInput = document.getElementById("image-input");
const pdfInput = document.getElementById("pdf-input");
const statusEl = document.getElementById("upload-status");

if (imageInput) {
  imageInput.addEventListener("change", async () => {
    const file = imageInput.files[0];
    if (!file) return;
    statusEl.textContent = "Analyzing image...";
    const formData = new FormData();
    formData.append("image", file);
    const res = await fetch("/api/wardrobe/upload-image", { method: "POST", body: formData });
    const data = await res.json();
    statusEl.textContent = data.success
      ? `Saved: ${data.analysis.name}`
      : `Error: ${data.error}`;
    loadWardrobe();
  });
}

if (pdfInput) {
  pdfInput.addEventListener("change", async () => {
    const file = pdfInput.files[0];
    if (!file) return;
    statusEl.textContent = "Reading PDF...";
    const formData = new FormData();
    formData.append("pdf", file);
    const res = await fetch("/api/wardrobe/upload-pdf", { method: "POST", body: formData });
    const data = await res.json();
    statusEl.textContent = data.success
      ? `Imported ${data.count} items`
      : `Error: ${data.error}`;
    loadWardrobe();
  });
}

const sectionGrids = {
  Upper: document.getElementById("wardrobe-grid-upper"),
  Lower: document.getElementById("wardrobe-grid-lower"),
  Footwear: document.getElementById("wardrobe-grid-footwear"),
  Accessories: document.getElementById("wardrobe-grid-accessories"),
};
const searchInput = document.getElementById("search-input");
const categoryFilter = document.getElementById("category-filter");

async function loadWardrobe() {
  if (!sectionGrids.Upper) return;
  const params = new URLSearchParams();
  if (searchInput && searchInput.value) params.append("search", searchInput.value);
  if (categoryFilter && categoryFilter.value) params.append("category", categoryFilter.value);

  const res = await fetch(`/api/wardrobe?${params.toString()}`);
  const data = await res.json();

  Object.values(sectionGrids).forEach((g) => { if (g) g.innerHTML = ""; });

  (data.items || []).forEach((item) => {
    const targetGrid = sectionGrids[item.section] || sectionGrids.Accessories;
    if (!targetGrid) return;

    const card = document.createElement("div");
    card.className = "card item-card";
    card.innerHTML = `
      ${item.image_path ? `<img src="${item.image_path}" alt="${item.name}" />` : ""}
      <h4>${item.name || item.category}</h4>
      <p class="subtle">${item.category} • ${item.color}</p>
      <p class="subtle item-description">${item.description || ""}</p>
      <div class="actions">
        <button class="btn-secondary edit-btn">Edit</button>
        <button class="btn-secondary delete-btn">Delete</button>
      </div>
    `;
    card.querySelector(".edit-btn").addEventListener("click", () => editDescription(item.id, item.description));
    card.querySelector(".delete-btn").addEventListener("click", () => deleteItem(item.id));
    targetGrid.appendChild(card);
  });
}

async function editDescription(id, currentDescription) {
  const updated = prompt("Edit description:", currentDescription || "");
  if (updated === null) return;
  await fetch(`/api/wardrobe/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ description: updated }),
  });
  loadWardrobe();
}

async function deleteItem(id) {
  if (!confirm("Delete this item?")) return;
  await fetch(`/api/wardrobe/${id}`, { method: "DELETE" });
  loadWardrobe();
}

if (searchInput) searchInput.addEventListener("input", loadWardrobe);
if (categoryFilter) categoryFilter.addEventListener("change", loadWardrobe);
if (sectionGrids.Upper) loadWardrobe();