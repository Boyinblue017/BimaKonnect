const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
const profileForm = document.getElementById("specialistProfileForm");
const passwordForm = document.getElementById("specialistPasswordForm");
const toastRegion = document.getElementById("toastRegion");

function showToast(message, type = "success") {
  const toast = document.createElement("div");
  const icon = document.createElement("i");
  const text = document.createElement("span");
  const close = document.createElement("button");
  toast.className = `directory-toast${type === "error" ? " toast-error" : ""}`;
  toast.setAttribute("role", type === "error" ? "alert" : "status");
  icon.className = `ph ${type === "error" ? "ph-x-circle" : "ph-check-circle"}`;
  icon.setAttribute("aria-hidden", "true");
  text.className = "directory-toast-message";
  text.textContent = message;
  close.type = "button";
  close.setAttribute("aria-label", "Dismiss notification");
  close.textContent = "×";
  close.addEventListener("click", () => toast.remove());
  toast.append(icon, text, close);
  toastRegion.append(toast);
  window.setTimeout(() => toast.remove(), 5000);
}

async function saveForm(form, path, successMessage, reset = false) {
  if (!form.checkValidity()) {
    showToast("Complete the required fields with valid information.", "error");
    form.querySelector(":invalid")?.focus();
    return;
  }
  const button = form.querySelector('button[type="submit"]');
  button.disabled = true;
  try {
    const response = await fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRF-Token": csrfToken },
      body: JSON.stringify(Object.fromEntries(new FormData(form)))
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Could not save your changes.");
    if (reset) form.reset();
    showToast(data.message || successMessage);
  } catch (error) {
    showToast(error.message || "Could not save your changes. Please try again.", "error");
  } finally {
    button.disabled = false;
  }
}

async function loadProfile() {
  try {
    const response = await fetch("/api/specialists/me");
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Could not load your profile.");
    for (const [field, value] of Object.entries(data.profile)) {
      const input = profileForm.elements.namedItem(field);
      if (input) input.value = value;
    }
  } catch (error) {
    showToast(error.message || "Could not load your profile.", "error");
  }
}

profileForm.addEventListener("submit", (event) => {
  event.preventDefault();
  saveForm(profileForm, "/api/specialists/me", "Your profile was updated.");
});

passwordForm.addEventListener("submit", (event) => {
  event.preventDefault();
  saveForm(passwordForm, "/api/specialists/me/password", "Your password was updated.", true);
});

loadProfile();
