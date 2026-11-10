const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
const list = document.getElementById("specialistList");
const search = document.getElementById("specialistSearch");
const count = document.getElementById("specialistCount");
const toastRegion = document.getElementById("toastRegion");
let specialists = [];

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
  if (toastRegion.children.length >= 4) toastRegion.firstElementChild.remove();
  toast.append(icon, text, close);
  toastRegion.append(toast);
  window.setTimeout(() => toast.remove(), 5000);
}

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function contactLink(iconName, label, href) {
  const link = document.createElement("a");
  link.href = href;
  const icon = element("i", `ph ${iconName}`);
  icon.setAttribute("aria-hidden", "true");
  link.append(icon, document.createTextNode(label));
  return link;
}

function buildCard(specialist) {
  const card = element("article", "specialist-card");
  const top = element("div", "specialist-card-top");
  const avatar = element("span", "specialist-avatar");
  const avatarIcon = element("i", "ph ph-user-circle");
  avatarIcon.setAttribute("aria-hidden", "true");
  avatar.append(avatarIcon);
  const identity = element("div");
  identity.append(
    element("h3", "", specialist.display_name),
    element("p", "specialist-specialty", specialist.specialty)
  );
  top.append(avatar, identity);

  const location = element("p", "specialist-location");
  const locationIcon = element("i", "ph ph-map-pin");
  locationIcon.setAttribute("aria-hidden", "true");
  location.append(locationIcon, document.createTextNode(specialist.region));

  const bio = element("p", "specialist-bio", specialist.bio);
  const contact = element("div", "specialist-contact");
  contact.append(
    contactLink("ph-envelope-simple", specialist.public_email, `mailto:${specialist.public_email}`),
    contactLink("ph-phone", specialist.phone, `tel:${specialist.phone.replace(/[^\d+]/g, "")}`)
  );

  const ratingSummary = element("div", "specialist-rating-summary");
  const stars = element("span", "rating-stars", "★★★★★");
  stars.setAttribute("aria-label", specialist.average_rating === null
    ? "No ratings yet"
    : `${specialist.average_rating} out of 5 stars`);
  const average = specialist.average_rating === null
    ? "New"
    : Number(specialist.average_rating).toFixed(1);
  ratingSummary.append(
    stars,
    element("span", "rating-value", average),
    element(
      "span",
      "rating-total",
      `${specialist.rating_count} ${specialist.rating_count === 1 ? "rating" : "ratings"}`
    )
  );

  card.append(top, location, bio, contact, ratingSummary);
  if (!specialist.is_own_profile) card.append(buildRatingForm(specialist));
  else card.append(element("p", "rating-total", "This is your profile."));
  return card;
}

function buildRatingForm(specialist) {
  const form = element("form", "rating-form");
  const fieldset = document.createElement("fieldset");
  fieldset.append(element("legend", "", specialist.my_rating
    ? `Your rating: ${specialist.my_rating} out of 5 — update it`
    : "Rate this specialist"));

  for (let rating = 1; rating <= 5; rating += 1) {
    const wrapper = element("span", "rating-choice");
    const input = document.createElement("input");
    const inputId = `rating-${specialist.id}-${rating}`;
    input.id = inputId;
    input.type = "radio";
    input.name = `rating-${specialist.id}`;
    input.value = String(rating);
    input.required = true;
    input.checked = specialist.my_rating === rating;
    const label = document.createElement("label");
    label.htmlFor = inputId;
    label.textContent = "★";
    label.setAttribute("aria-label", `${rating} ${rating === 1 ? "star" : "stars"}`);
    wrapper.append(input, label);
    fieldset.append(wrapper);
  }

  const submit = element("button", "rating-submit", specialist.my_rating ? "Update rating" : "Submit rating");
  submit.type = "submit";
  const submitIcon = element("i", "ph ph-paper-plane-tilt");
  submitIcon.setAttribute("aria-hidden", "true");
  submit.prepend(submitIcon);
  form.append(fieldset, submit);
  form.addEventListener("submit", (event) => submitRating(event, specialist.id));
  return form;
}

function renderSpecialists() {
  const query = search.value.trim().toLowerCase();
  const filtered = specialists.filter((specialist) =>
    [specialist.display_name, specialist.specialty, specialist.region, specialist.bio]
      .some((value) => value.toLowerCase().includes(query))
  );
  list.replaceChildren();
  count.textContent = `${filtered.length} ${filtered.length === 1 ? "specialist" : "specialists"}`;
  if (!filtered.length) {
    list.append(element("p", "directory-message", query
      ? "No specialists match that search. Try another name, cover area, or location."
      : "There are no specialist profiles yet."));
    return;
  }
  filtered.forEach((specialist) => list.append(buildCard(specialist)));
}

async function loadSpecialists() {
  list.setAttribute("aria-busy", "true");
  try {
    const response = await fetch("/api/specialists");
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Could not load specialist profiles.");
    specialists = Array.isArray(data.specialists) ? data.specialists : [];
    renderSpecialists();
  } catch (error) {
    list.replaceChildren(element("p", "directory-message", error.message || "Could not load specialists. Please try again."));
    showToast(error.message || "Could not load specialists. Please try again.", "error");
  } finally {
    list.setAttribute("aria-busy", "false");
  }
}

async function submitRating(event, specialistId) {
  event.preventDefault();
  const form = event.currentTarget;
  const selected = form.querySelector('input[type="radio"]:checked');
  if (!selected) {
    showToast("Choose a star rating before submitting.", "error");
    return;
  }
  const button = form.querySelector("button");
  button.disabled = true;
  try {
    const response = await fetch(`/api/specialists/${specialistId}/rating`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRF-Token": csrfToken },
      body: JSON.stringify({ rating: Number(selected.value) })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Could not save your rating.");
    showToast("Your rating was saved.");
    await loadSpecialists();
  } catch (error) {
    showToast(error.message || "Could not save your rating. Please try again.", "error");
    button.disabled = false;
  }
}

search.addEventListener("input", renderSpecialists);
loadSpecialists();
