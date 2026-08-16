const themeBtn = document.getElementById("theme-toggle");

// v10: <body> already arrives with the correct "dark" class from the server
// (see app.py's inject_theme + base.html), so this only needs to run when
// the button is actually clicked — no more checking the OS theme on every
// page load, which was the thing silently overriding your saved choice.
function applyTheme(theme) {
  document.body.classList.toggle("dark", theme === "dark");
}

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

// v9: mobile hamburger menu toggle
const navToggle = document.getElementById("nav-toggle");
const navLinks = document.getElementById("nav-links");
if (navToggle && navLinks) {
  navToggle.addEventListener("click", () => {
    navLinks.classList.toggle("open");
  });
  navLinks.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => navLinks.classList.remove("open"));
  });
}