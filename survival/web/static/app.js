let gameId = null;
let busy = false;

const logEl = document.getElementById("log");
const form = document.getElementById("turn-form");
const input = document.getElementById("action");
const sendBtn = form.querySelector("button");

async function post(url, body) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body || {}),
  });
  if (!res.ok) {
    let detail = "Something went wrong.";
    try { detail = (await res.json()).detail || detail; } catch (e) {}
    throw new Error(detail);
  }
  return res.json();
}

function addEntry(playerText, narrative, cls) {
  for (const old of logEl.querySelectorAll(".entry")) old.classList.add("old");
  const entry = document.createElement("div");
  entry.className = "entry" + (cls ? " " + cls : "");
  if (playerText) {
    const you = document.createElement("div");
    you.className = "you";
    you.textContent = "> " + playerText;
    entry.appendChild(you);
  }
  const text = document.createElement("div");
  text.className = "story-text";
  text.textContent = narrative;
  entry.appendChild(text);
  logEl.appendChild(entry);
  logEl.scrollTop = logEl.scrollHeight;
  return text;
}

function clockText(hour, phase) {
  let h = Math.floor(hour);
  let m = Math.round((hour - h) * 60);
  if (m === 60) { h = (h + 1) % 24; m = 0; }
  const pad = (n) => String(n).padStart(2, "0");
  return pad(h) + ":" + pad(m) + " · " + phase;
}

function renderState(state) {
  document.getElementById("health-bar").style.width = state.health + "%";
  document.getElementById("sanity-bar").style.width = state.sanity + "%";
  document.getElementById("clock").textContent = clockText(state.hour, state.phase_of_day);
  document.getElementById("injuries").textContent = state.injuries.length ? state.injuries.join(", ") : "none";
  document.getElementById("pack-label").textContent = "Pack " + state.used_space + " / " + state.capacity;
  const pack = document.getElementById("pack");
  pack.textContent = "";
  for (const item of state.inventory) {
    const chip = document.createElement("span");
    chip.className = "chip";
    chip.textContent = item;
    pack.appendChild(chip);
  }
  document.getElementById("nearby").textContent = "-";
  for (const layer of document.querySelectorAll("#sky div")) {
    layer.classList.toggle("on", layer.dataset.phase === state.phase_of_day);
  }
}

async function startGame() {
  try {
    const data = await post("/api/new");
    gameId = data.game_id;
    const s = data.scenario;
    document.getElementById("header").textContent = s.character + " · " + s.setting + " · " + s.cause;
    logEl.textContent = "";
    renderState(data.state);
    addEntry(null, data.opening, "");
    input.disabled = false;
    sendBtn.disabled = false;
    input.focus();
  } catch (e) {
    addEntry(null, "Could not start a game. " + e.message, "rejected");
  }
}

function endGame(phase) {
  input.disabled = true;
  sendBtn.disabled = true;
  addEntry(null, phase === "dead" ? "You did not make it." : "You made it out.", "");
  const again = document.createElement("button");
  again.type = "button";
  again.textContent = "New game";
  again.addEventListener("click", () => { again.remove(); startGame(); });
  logEl.appendChild(again);
  logEl.scrollTop = logEl.scrollHeight;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = input.value.trim();
  if (!text || busy || !gameId) return;
  busy = true;
  input.value = "";
  input.disabled = true;
  sendBtn.disabled = true;
  const textEl = addEntry(text, "...", "");
  try {
    const out = await post("/api/turn", { game_id: gameId, text: text });
    textEl.textContent = out.narrative;
    if (!out.ok) textEl.parentElement.classList.add("rejected");
    renderState(out.state);
    logEl.scrollTop = logEl.scrollHeight;
    if (out.state.phase !== "playing") {
      endGame(out.state.phase);
      busy = false;
      return;
    }
  } catch (e) {
    textEl.textContent = e.message;
    textEl.parentElement.classList.add("rejected");
  }
  busy = false;
  input.disabled = false;
  sendBtn.disabled = false;
  input.focus();
});

startGame();