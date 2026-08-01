// Theme toggle — persisted in a cookie-free way via localStorage-free session flag
const themeBtn = document.getElementById("theme-toggle");

function applyTheme(theme) {
  document.body.classList.toggle("dark", theme === "dark");
  if (themeBtn) themeBtn.textContent = theme === "dark" ? "☀️" : "🌙";
}

// Initial theme from data attribute set server-side would be ideal;
// fallback to system preference for first load.
const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
applyTheme(prefersDark ? "dark" : "light");

if (themeBtn) {
  themeBtn.addEventListener("click", async () => {
    const newTheme = document.body.classList.contains("dark") ? "light" : "dark";
    applyTheme(newTheme);
    await fetch("/api/settings/theme", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ theme: newTheme }),
    });
  });
}