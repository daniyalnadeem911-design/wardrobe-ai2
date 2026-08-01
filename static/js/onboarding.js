document.getElementById("onboarding-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.target;
  const favorite_colors = Array.from(
    form.querySelectorAll('input[name="favorite_colors"]:checked')
  ).map((el) => el.value);

  const payload = {
    gender: form.gender.value,
    height: form.height.value,
    skin_tone: form.skin_tone.value,
    country: form.country.value,
    city: form.city.value,
    preferred_style: form.preferred_style.value,
    favorite_colors,
  };

  const res = await fetch("/api/onboarding", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  if (data.success) {
    window.location.href = "/dashboard";
  } else {
    alert("Could not save profile. Please try again.");
  }
});