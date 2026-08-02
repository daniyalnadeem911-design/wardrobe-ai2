const signupForm = document.getElementById("signup-form");
if (signupForm) {
  signupForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const errorEl = document.getElementById("signup-error");
    const res = await fetch("/api/signup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: signupForm.username.value.trim(),
        password: signupForm.password.value,
      }),
    });
    const data = await res.json();
    if (data.success) {
      window.location.href = "/onboarding";
    } else if (errorEl) {
      errorEl.textContent = data.error || "Something went wrong.";
    }
  });
}

const loginForm = document.getElementById("login-form");
if (loginForm) {
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const errorEl = document.getElementById("login-error");
    const res = await fetch("/api/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: signupForm.username.value.trim(),
        password: signupForm.password.value,
        invite_code: signupForm.invite_code.value.trim(),
      }),
    });
    const data = await res.json();
    if (data.success) {
      window.location.href = data.onboarded ? "/dashboard" : "/onboarding";
    } else if (errorEl) {
      errorEl.textContent = data.error || "Something went wrong.";
    }
  });
}

const logoutBtn = document.getElementById("logout-btn");
if (logoutBtn) {
  logoutBtn.addEventListener("click", async () => {
    await fetch("/api/logout", { method: "POST" });
    window.location.href = "/login";
  });
}