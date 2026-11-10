const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
const form = document.getElementById("specialistCreateForm");
const list = document.getElementById("adminSpecialistList");
const count = document.getElementById("adminSpecialistCount");
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

function node(tag, className, text) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (text !== undefined) element.textContent = text;
  return element;
}

async function loadSpecialists() {
  list.setAttribute("aria-busy", "true");
  try {
    const response = await fetch("/api/admin/specialists");
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Could not load specialist accounts.");
    list.replaceChildren();
    count.textContent = `${data.specialists.length} ${data.specialists.length === 1 ? "account" : "accounts"}`;
    if (!data.specialists.length) {
      list.append(node("p", "directory-message", "No specialist accounts have been added."));
    }
    data.specialists.forEach((specialist) => {
      const row = node("article", "admin-specialist-row");
      const details = node("div");
      details.append(
        node("h3", "", specialist.display_name),
        node("p", "", `${specialist.specialty} · ${specialist.region} · ${specialist.public_email}`)
      );
      const rating = node("span", "admin-rating", specialist.average_rating === null
        ? "No ratings yet"
        : `★ ${Number(specialist.average_rating).toFixed(1)} (${specialist.rating_count})`);
      row.append(details, rating);
      list.append(row);
    });
  } catch (error) {
    list.replaceChildren(node("p", "directory-message", error.message || "Could not load specialist accounts."));
    showToast(error.message || "Could not load specialist accounts.", "error");
  } finally {
    list.setAttribute("aria-busy", "false");
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!form.checkValidity()) {
    showToast("Complete the required fields with valid contact details.", "error");
    form.querySelector(":invalid")?.focus();
    return;
  }
  const button = form.querySelector('button[type="submit"]');
  const payload = Object.fromEntries(new FormData(form));
  button.disabled = true;
  try {
    const response = await fetch("/api/admin/specialists", {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRF-Token": csrfToken },
      body: JSON.stringify(payload)
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Could not create the specialist account.");
    form.reset();
    showToast("Specialist account created. Share the temporary password securely.");
    await loadSpecialists();
  } catch (error) {
    showToast(error.message || "Could not create the specialist account.", "error");
  } finally {
    button.disabled = false;
  }
});

loadSpecialists();
