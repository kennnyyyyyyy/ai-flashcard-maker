// Front end for the flashcard maker: tabs, file picking, calling the API, flipping and downloading.

const $ = (id) => document.getElementById(id);
const form = $("form");
const tabs = document.querySelector(".tabs");
const text = $("text");
const fileInput = $("file");
const drop = $("drop");
const chip = $("chip");
const count = $("count");
const go = $("go");
const errorBox = $("error");
const results = $("results");
const grid = $("grid");

let mode = "text";
let lastCards = [];
let lastSource = "";

// ---- tabs ----
document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => setMode(tab.dataset.tab));
});

function setMode(next) {
  mode = next;
  tabs.dataset.active = next;
  document.querySelectorAll(".tab").forEach((t) => {
    const on = t.dataset.tab === next;
    t.classList.toggle("active", on);
    t.setAttribute("aria-selected", on);
  });
  $("pane-text").hidden = next !== "text";
  $("pane-file").hidden = next !== "file";
  hideError();
}

// ---- text box ----
text.addEventListener("input", () => {
  const words = text.value.trim() ? text.value.trim().split(/\s+/).length : 0;
  $("words").textContent = `${words.toLocaleString()} word${words === 1 ? "" : "s"}`;
});

// ---- file picking ----
fileInput.addEventListener("change", () => showFile(fileInput.files[0]));

["dragenter", "dragover"].forEach((ev) =>
  drop.addEventListener(ev, (e) => { e.preventDefault(); drop.classList.add("over"); }));
["dragleave", "drop"].forEach((ev) =>
  drop.addEventListener(ev, (e) => { e.preventDefault(); drop.classList.remove("over"); }));
drop.addEventListener("drop", (e) => {
  const file = e.dataTransfer.files[0];
  if (!file) return;
  const dt = new DataTransfer();
  dt.items.add(file);
  fileInput.files = dt.files;
  showFile(file);
});

$("chip-x").addEventListener("click", () => {
  fileInput.value = "";
  showFile(null);
});

function showFile(file) {
  hideError();
  drop.hidden = !!file;
  chip.hidden = !file;
  if (!file) return;
  const ext = file.name.split(".").pop().toLowerCase();
  const icon = $("chip-icon");
  icon.textContent = ext === "docx" ? "DOCX" : ext.toUpperCase().slice(0, 4);
  icon.className = `chip-icon ${ext}`;
  $("chip-name").textContent = file.name;
  $("chip-size").textContent = prettySize(file.size);
}

function prettySize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

// ---- slider ----
count.addEventListener("input", () => { $("count-out").textContent = count.value; });

// ---- make cards ----
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  hideError();
  const data = new FormData();
  data.append("count", count.value);
  if (mode === "file") {
    if (!fileInput.files[0]) return showError("Choose a PDF, Word or text file first.");
    data.append("file", fileInput.files[0]);
  } else {
    if (!text.value.trim()) return showError("Paste some notes first.");
    data.append("text", text.value);
  }

  setBusy(true);
  showSkeleton(Math.min(6, Number(count.value)));
  try {
    const res = await fetch("/api/cards", { method: "POST", body: data });
    const body = await res.json().catch(() => ({ error: "The server sent back something unexpected." }));
    if (!res.ok) throw new Error(body.error || "Something went wrong.");
    lastCards = body.cards;
    lastSource = body.source;
    showCards(body);
  } catch (err) {
    results.hidden = true;
    showError(err.message);
  } finally {
    setBusy(false);
  }
});

function setBusy(on) {
  go.classList.toggle("busy", on);
  $("go-label").textContent = on ? "Making flashcards..." : "Make flashcards";
}

function showSkeleton(n) {
  $("reaction").classList.remove("pop");
  results.hidden = false;
  $("results-title").textContent = "Making your flashcards...";
  $("results-sub").textContent = "GPT-4o-mini is reading your notes";
  grid.innerHTML = Array.from({ length: n }, (_, i) => `
    <div class="card skeleton" style="--i:${i}"><div class="card-inner"><div class="face">
      <div class="bar short"></div><div class="bar"></div><div class="bar w80"></div><div class="bar w60"></div>
    </div></div></div>`).join("");
  results.scrollIntoView({ behavior: "smooth", block: "start" });
}

function showCards({ cards, source }) {
  const reaction = $("reaction");
  reaction.classList.remove("pop");
  void reaction.offsetWidth;          // restart the animation
  reaction.classList.add("pop");
  $("results-title").textContent = `${cards.length} flashcard${cards.length === 1 ? "" : "s"}`;
  $("results-sub").textContent = `From ${source}. Click a card to flip it.`;
  grid.innerHTML = "";
  cards.forEach((card, i) => {
    const el = document.createElement("div");
    el.className = "card";
    el.style.setProperty("--i", i);
    el.innerHTML = `
      <div class="card-inner">
        <div class="face front">
          <span class="badge">Q${i + 1}</span>
          <p></p>
          <span class="hint"><svg viewBox="0 0 24 24"><path d="M4 12a8 8 0 0 1 14-5.3M20 12a8 8 0 0 1-14 5.3"/><path d="M18 3v4h-4M6 21v-4h4"/></svg>Show answer</span>
        </div>
        <div class="face back">
          <span class="badge">A${i + 1}</span>
          <p></p>
        </div>
      </div>`;
    el.querySelector(".front p").textContent = card.question;
    el.querySelector(".back p").textContent = card.answer;
    el.addEventListener("click", () => el.classList.toggle("flipped"));
    grid.appendChild(el);
  });
}

$("flip-all").addEventListener("click", () => {
  const cards = [...grid.querySelectorAll(".card:not(.skeleton)")];
  const anyFront = cards.some((c) => !c.classList.contains("flipped"));
  cards.forEach((c, i) => setTimeout(() => c.classList.toggle("flipped", anyFront), i * 60));
});

// ---- downloads ----
document.querySelectorAll("[data-export]").forEach((btn) => {
  btn.addEventListener("click", async () => {
    const fmt = btn.dataset.export;
    const res = await fetch(`/api/export/${fmt}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ cards: lastCards, name: lastSource === "your notes" ? "notes" : lastSource }),
    });
    if (!res.ok) return showError((await res.json()).error);
    const blob = await res.blob();
    const name = (res.headers.get("Content-Disposition") || "").match(/filename="?([^";]+)"?/);
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = name ? name[1] : `flashcards.${fmt}`;
    a.click();
    URL.revokeObjectURL(a.href);
  });
});

// ---- errors ----
function showError(message) {
  errorBox.textContent = message;
  errorBox.hidden = false;
}

function hideError() {
  errorBox.hidden = true;
}
