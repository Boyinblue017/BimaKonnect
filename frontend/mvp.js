const byId = (id) => document.getElementById(id);
const chatBox = byId("chatBox");
const chatForm = byId("chatForm");
const questionInput = byId("question");
const askButton = byId("askBtn");
const quickQuestions = [...document.querySelectorAll("[data-question]")];
const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

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
    addMessage("assistant", response.ok
      ? answerText(data)
      : data.error || "Please try again.");
  } catch {
    loading.remove();
    addMessage("assistant", "I can’t reach the service right now. Please check your connection and try again.");
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
    questionInput.setCustomValidity("Please enter an insurance question.");
    chatForm.reportValidity();
    return;
  }
  questionInput.setCustomValidity("");
  questionInput.value = "";
  ask(question);
});

questionInput.addEventListener("input", () => {
  questionInput.setCustomValidity("");
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
      output.innerHTML = `<p class="error">${escapeHtml(data.error || "Please try again.")}</p>`;
    } else if (!Array.isArray(data.recommendations) || !data.recommendations.length) {
      output.innerHTML = "<p class=\"muted\">Select one or more options to see useful cover to explore.</p>";
    } else {
      output.innerHTML = `<h3>Your starting points</h3>${data.recommendations.map((item) => `<article class="recommendation"><span>${escapeHtml(item.priority)}</span><h4>${escapeHtml(item.name)}</h4><p>${escapeHtml(item.reason)}</p></article>`).join("")}`;
    }
  } catch {
    output.innerHTML = "<p class=\"error\">We could not prepare your guide. Please try again.</p>";
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
    } else {
      output.innerHTML = `<p class="error">${escapeHtml(data.error || "Please try again.")}</p>`;
    }
  } catch {
    output.innerHTML = "<p class=\"error\">We could not load your checklist. Please try again.</p>";
  } finally {
    output.setAttribute("aria-busy", "false");
    button.disabled = false;
    button.textContent = "Show my checklist";
  }
});
