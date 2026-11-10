const byId = (id) => document.getElementById(id);
const chatBox = byId("chatBox");
const chatForm = byId("chatForm");
const questionInput = byId("question");
const askButton = byId("askBtn");
const quickQuestions = [...document.querySelectorAll("[data-question]")];
const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
const toastRegion = byId("toastRegion");
const sidebar = byId("sidebar");
const dashboardMain = document.querySelector(".dashboard-main");
const sidebarToggle = byId("sidebarToggle");
const sidebarOverlay = byId("sidebarOverlay");
const mobileSidebarQuery = window.matchMedia("(max-width: 760px)");

function showToast(message, type = "success") {
  const toast = document.createElement("div");
  const toastType = ["success", "warning", "error"].includes(type) ? type : "success";
  const icon = {
    success: "ph-check-circle",
    warning: "ph-warning-circle",
    error: "ph-x-circle"
  }[toastType];
  const dismiss = document.createElement("button");
  const iconElement = document.createElement("i");
  const text = document.createElement("span");

  toast.className = `toast toast-${toastType}`;
  toast.setAttribute("role", toastType === "error" ? "alert" : "status");
  iconElement.className = `ph ${icon}`;
  iconElement.setAttribute("aria-hidden", "true");
  text.className = "toast-message";
  text.textContent = message;
  dismiss.className = "toast-close";
  dismiss.type = "button";
  dismiss.setAttribute("aria-label", "Dismiss notification");
  dismiss.innerHTML = '<i class="ph ph-x" aria-hidden="true"></i>';

  let removeTimer;
  const removeToast = () => {
    clearTimeout(removeTimer);
    toast.classList.add("toast-leaving");
    setTimeout(() => toast.remove(), 150);
  };
  dismiss.addEventListener("click", removeToast);
  toast.addEventListener("mouseenter", () => clearTimeout(removeTimer));
  toast.addEventListener("mouseleave", scheduleRemoval);
  toast.addEventListener("focusin", () => clearTimeout(removeTimer));
  toast.addEventListener("focusout", scheduleRemoval);

  function scheduleRemoval() {
    clearTimeout(removeTimer);
    removeTimer = setTimeout(removeToast, 5000);
  }

  if (toastRegion.children.length >= 4) toastRegion.firstElementChild.remove();
  toast.append(iconElement, text, dismiss);
  toastRegion.append(toast);
  scheduleRemoval();
}

function setSidebarOpen(open, returnFocus = false) {
  const isOpen = open && mobileSidebarQuery.matches;
  document.body.classList.toggle("sidebar-open", isOpen);
  sidebarToggle.setAttribute("aria-expanded", String(isOpen));
  sidebarToggle.setAttribute("aria-label", isOpen ? "Close navigation" : "Open navigation");
  sidebar.inert = mobileSidebarQuery.matches && !isOpen;
  dashboardMain.inert = isOpen;
  sidebarOverlay.tabIndex = isOpen ? 0 : -1;
  if (returnFocus) sidebarToggle.focus({ preventScroll: true });
  else if (isOpen) sidebar.querySelector(".sidebar-link").focus();
}

sidebarToggle.addEventListener("click", () => {
  setSidebarOpen(sidebarToggle.getAttribute("aria-expanded") !== "true");
});
sidebarOverlay.addEventListener("click", () => setSidebarOpen(false, true));
sidebar.querySelectorAll("a[href^='#']").forEach((link) => {
  link.addEventListener("click", () => setSidebarOpen(false, true));
});
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && document.body.classList.contains("sidebar-open")) {
    setSidebarOpen(false, true);
  }
});
mobileSidebarQuery.addEventListener("change", () => setSidebarOpen(false));
setSidebarOpen(false);

const sidebarLinks = [...sidebar.querySelectorAll(".sidebar-link[href^='#']")];
if ("IntersectionObserver" in window) {
  const sectionObserver = new IntersectionObserver((entries) => {
    const visible = entries
      .filter((entry) => entry.isIntersecting)
      .sort((first, second) => second.intersectionRatio - first.intersectionRatio)[0];
    if (!visible) return;
    sidebarLinks.forEach((link) => {
      const active = link.hash === `#${visible.target.id}`;
      link.classList.toggle("active", active);
      if (active) link.setAttribute("aria-current", "location");
      else link.removeAttribute("aria-current");
    });
  }, { rootMargin: "-15% 0px -70% 0px", threshold: [0, 0.1, 0.5] });
  ["dashboard", "assistant", "quiz", "glossary", "claims"]
    .map(byId)
    .filter(Boolean)
    .forEach((section) => sectionObserver.observe(section));
}

function escapeHtml(value) {
  const element = document.createElement("div");
  element.textContent = value;
  return element.innerHTML;
}

function addMessage(kind, content) {
  const article = document.createElement("article");
  article.className = `message ${kind === "user" ? "user-message" : "assistant-message"}`;
  article.innerHTML = kind === "user"
    ? `<p>${escapeHtml(content)}</p>`
    : `<strong>Bima</strong><p>${escapeHtml(content)}</p>`;
  chatBox.append(article);
  chatBox.scrollTop = chatBox.scrollHeight;
  return article;
}

function answerText(data) {
  const benefits = Array.isArray(data.benefits) && data.benefits.length
    ? ` Key benefits: ${data.benefits.join(" • ")}.`
    : "";
  return `${data.definition || "I’m sorry, I could not find an answer."}${benefits}${data.next_step ? ` ${data.next_step}` : ""}`;
}

async function ask(question) {
  const clean = question.trim();
  if (!clean || askButton.disabled) return;

  addMessage("user", clean);
  const loading = addMessage("assistant", "Thinking…");
  chatBox.setAttribute("aria-busy", "true");
  askButton.disabled = true;
  questionInput.disabled = true;
  quickQuestions.forEach((button) => {
    button.disabled = true;
  });

  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRF-Token": csrfToken },
      body: JSON.stringify({ question: clean })
    });
    const data = await response.json();
    loading.remove();
    if (response.ok) {
      addMessage("assistant", answerText(data));
      showToast("Bima replied to your question.");
    } else {
      const error = data.error || "Please try again.";
      addMessage("assistant", error);
      showToast(error, "error");
    }
  } catch {
    loading.remove();
    const error = "I can’t reach the service right now. Please check your connection and try again.";
    addMessage("assistant", error);
    showToast("Couldn’t reach Bima. Check your connection and try again.", "error");
  } finally {
    chatBox.setAttribute("aria-busy", "false");
    askButton.disabled = false;
    questionInput.disabled = false;
    quickQuestions.forEach((button) => {
      button.disabled = false;
    });
    questionInput.focus();
  }
}

chatForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const question = questionInput.value.trim();
  if (!question) {
    showToast("Type a question before asking Bima.", "warning");
    questionInput.focus();
    return;
  }
  questionInput.value = "";
  ask(question);
});

quickQuestions.forEach((button) => {
  button.addEventListener("click", () => ask(button.dataset.question));
});

byId("quizForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const button = byId("recommendBtn");
  const output = byId("recommendations");
  const profile = Object.fromEntries(
    ["health", "vehicle", "farmer", "business", "dependents"]
      .map((id) => [id, byId(id).checked])
  );
  if (!Object.values(profile).some(Boolean)) {
    showToast("Choose at least one option to get a useful guide.", "warning");
    byId("health").focus();
    return;
  }
  button.disabled = true;
  button.textContent = "Preparing your guide…";
  output.setAttribute("aria-busy", "true");
  output.innerHTML = "<p class=\"muted\">Finding useful starting points…</p>";

  try {
    const response = await fetch("/recommend", {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRF-Token": csrfToken },
      body: JSON.stringify(profile)
    });
    const data = await response.json();
    if (!response.ok) {
      const error = data.error || "Please try again.";
      output.innerHTML = `<p class="error">${escapeHtml(error)}</p>`;
      showToast(error, "error");
    } else if (!Array.isArray(data.recommendations) || !data.recommendations.length) {
      output.innerHTML = "<p class=\"muted\">Select one or more options to see useful cover to explore.</p>";
      showToast("Choose one or more options to see your starting points.", "warning");
    } else {
      output.innerHTML = `<h3>Your starting points</h3>${data.recommendations.map((item) => `<article class="recommendation"><span>${escapeHtml(item.priority)}</span><h4>${escapeHtml(item.name)}</h4><p>${escapeHtml(item.reason)}</p></article>`).join("")}`;
      showToast("Your cover guide is ready.");
    }
  } catch {
    output.innerHTML = "<p class=\"error\">We could not prepare your guide. Please try again.</p>";
    showToast("We couldn’t prepare your guide. Please try again.", "error");
  } finally {
    output.setAttribute("aria-busy", "false");
    button.disabled = false;
    button.textContent = "See my guide";
  }
});

let glossaryRequestId = 0;

async function loadGlossary(query = "") {
  const output = byId("glossaryResults");
  const requestId = ++glossaryRequestId;
  output.setAttribute("aria-busy", "true");
  output.innerHTML = `<p class="muted">${query ? "Searching the glossary…" : "Loading the glossary…"}</p>`;

  try {
    const response = query
      ? await fetch("/glossary/search", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRF-Token": csrfToken },
        body: JSON.stringify({ query })
      })
      : await fetch("/glossary");
    const data = await response.json();
    if (requestId !== glossaryRequestId) return;
    if (!response.ok) {
      throw new Error(data.error || "The glossary is unavailable right now.");
    }
    const entries = query
      ? data.results
      : Object.entries(data.glossary || {}).map(([term, value]) => ({ term, data: value }));
    output.innerHTML = Array.isArray(entries) && entries.length
      ? entries.map(({ term, data: entry }) => `<details><summary>${escapeHtml(term)}</summary><p>${escapeHtml(entry.definition)}</p><small>Example: ${escapeHtml(entry.example)}</small></details>`).join("")
      : "<p class=\"muted\">No matching terms yet. Try another word.</p>";
  } catch {
    if (requestId === glossaryRequestId) {
      output.innerHTML = "<p class=\"error\">The glossary is unavailable right now. Please try again.</p>";
      showToast("The glossary is unavailable. Please try again.", "error");
    }
  } finally {
    if (requestId === glossaryRequestId) {
      output.setAttribute("aria-busy", "false");
    }
  }
}

let searchTimer;
byId("glossarySearch").addEventListener("input", (event) => {
  clearTimeout(searchTimer);
  const query = event.target.value.trim();
  searchTimer = setTimeout(() => loadGlossary(query), 200);
});
loadGlossary();

byId("claimsForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!byId("claimCover").value || !byId("claimIncident").value) {
    showToast("Choose your cover and what happened to get a checklist.", "warning");
    (!byId("claimCover").value ? byId("claimCover") : byId("claimIncident")).focus();
    return;
  }
  const button = byId("claimGuideBtn");
  const output = byId("claimGuidance");
  button.disabled = true;
  button.textContent = "Preparing checklist…";
  output.setAttribute("aria-busy", "true");
  output.innerHTML = "<p class=\"muted\">Preparing your checklist…</p>";

  try {
    const response = await fetch("/claims/guidance", {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRF-Token": csrfToken },
      body: JSON.stringify({
        cover_type: byId("claimCover").value,
        incident: byId("claimIncident").value
      })
    });
    const data = await response.json();
    if (response.ok) {
      output.innerHTML = `<article class="claim-result"><p class="urgent">Important: ${escapeHtml(data.urgent)}</p><h3>${escapeHtml(data.title)}</h3><div><h4>What to do now</h4><ol>${data.steps.map((step) => `<li>${escapeHtml(step)}</li>`).join("")}</ol></div><div><h4>Keep these ready</h4><ul>${data.documents.map((document) => `<li>${escapeHtml(document)}</li>`).join("")}</ul></div><p class="disclaimer">${escapeHtml(data.disclaimer || "Your insurer's instructions and policy wording control the claim.")}</p></article>`;
      showToast("Your claims checklist is ready.");
    } else {
      const error = data.error || "Please try again.";
      output.innerHTML = `<p class="error">${escapeHtml(error)}</p>`;
      showToast(error, "error");
    }
  } catch {
    output.innerHTML = "<p class=\"error\">We could not load your checklist. Please try again.</p>";
    showToast("We couldn’t load your checklist. Please try again.", "error");
  } finally {
    output.setAttribute("aria-busy", "false");
    button.disabled = false;
    button.textContent = "Show my checklist";
  }
});
