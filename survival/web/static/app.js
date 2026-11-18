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
  document.getElementById("food-bar").style.width = state.food + "%";
  document.getElementById("water-bar").style.width = state.water + "%";
  document.getElementById("temp-bobber").style.left = state.temp + "%";
  document.getElementById("temp-word").textContent = state.temp_word;
  document.getElementById("clock").textContent = clockText(state.hour, state.sky);
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
  document.body.dataset.p = state.sky;
  updateVignette(state.health);
  currentSanity = state.sanity;
  for (const layer of document.querySelectorAll("#sky > div")) {
    layer.classList.toggle("on", layer.dataset.phase === state.sky);
  }
  const info = state.injury_info || {};
  document.getElementById("injuries").textContent = state.injuries.length
    ? state.injuries.map((n) => n + (info[n] && info[n].phase === "acute" ? " (worsening)" : "")).join(", ")
    : "none";
}

async function startGame() {
  try {
    const data = await post("/api/new");
    gameId = data.game_id;
    const s = data.scenario;
    document.getElementById("header").textContent = s.character + " · " + s.setting + " · " + s.cause;
    logEl.textContent = "";
    renderState(data.state);
    const openEl = addEntry(null, "", "");
    setStoryText(openEl, data.opening, data.state.sanity);
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
    if (out.ok) setStoryText(textEl, out.narrative, out.state.sanity);
    else textEl.textContent = out.narrative;
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

const CLOUDS = {
  dawn: { n: 4, a: 52, b: 68, c: "rgba(255,205,180,.38)", w: [70, 130], blur: 3 },
  morning: { n: 3, a: 42, b: 62, c: "rgba(255,255,255,.55)", w: [60, 120], blur: 3 },
  afternoon: { n: 3, a: 44, b: 64, c: "rgba(255,225,190,.5)", w: [60, 120], blur: 3 },
  dusk: { n: 4, a: 50, b: 68, c: "rgba(255,140,110,.34)", w: [70, 140], blur: 3 },
  night: { n: 0 },
};

function addClouds(layer, f) {
  for (let i = 0; i < f.n; i++) {
    const w = f.w[0] + Math.random() * (f.w[1] - f.w[0]);
    const cloud = document.createElement("div");
    cloud.className = "cloud";
    cloud.style.width = w + "px";
    cloud.style.height = w * 0.12 + "px";
    cloud.style.left = 8 + Math.random() * 80 + "%";
    cloud.style.top = f.a + Math.random() * (f.b - f.a) + "%";
    cloud.style.animationDuration = 80 + Math.random() * 60 + "s";
    cloud.style.animationDelay = -Math.random() * 80 + "s";
    for (const b of [[0, 30, 100, 50], [18, 0, 50, 70], [55, 20, 40, 60]]) {
      const blob = document.createElement("div");
      blob.className = "blob";
      blob.style.left = b[0] + "%";
      blob.style.top = b[1] + "%";
      blob.style.width = b[2] + "%";
      blob.style.height = b[3] + "%";
      blob.style.background = f.c;
      blob.style.filter = "blur(" + f.blur + "px)";
      cloud.appendChild(blob);
    }
    layer.appendChild(cloud);
  }
}

function addStars(layer) {
  for (let i = 0; i < 110; i++) {
    const star = document.createElement("div");
    star.className = "star";
    const size = 1 + Math.random() * 1.8;
    star.style.width = size + "px";
    star.style.height = size + "px";
    star.style.left = Math.random() * 100 + "%";
    star.style.top = Math.random() * 52 + "%";
    star.style.animationDelay = -Math.random() * 3 + "s";
    star.style.animationDuration = 2 + Math.random() * 3 + "s";
    if (size > 2.3) star.style.boxShadow = "0 0 4px 1px rgba(255,255,255,.6)";
    layer.appendChild(star);
  }
}

for (const layer of document.querySelectorAll("#sky > div")) {
  const phase = layer.dataset.phase;
  addClouds(layer, CLOUDS[phase]);
  if (phase === "night") addStars(layer);
}

const vignette = document.createElement("div");
vignette.id = "vignette";
document.body.appendChild(vignette);

function updateVignette(health) {
  const t = health >= 50 ? 0 : (50 - Math.max(health, 20)) / 30;
  const strength = health >= 50 ? 0 : 0.2 + 0.8 * t;
  vignette.style.setProperty("--vig", strength);
  vignette.style.setProperty("--amp", 0.12 + 0.23 * t);
  vignette.style.setProperty("--beat", (1.5 - 0.7 * t) + "s");
}

const GLITCH = "#%&@*█▒░▓§¤";

function corruptionRate(sanity) {
  if (sanity > 50) return 0;
  return (5 + (50 - Math.max(sanity, 0)) * 0.5) / 100;
}

function corruptText(text, sanity) {
  const rate = corruptionRate(sanity);
  if (!rate) return text;
  let out = "";
  for (const ch of text) {
    if (/[A-Za-z]/.test(ch) && Math.random() < rate) {
      out += GLITCH[Math.floor(Math.random() * GLITCH.length)];
    } else {
      out += ch;
    }
  }
  return out;
}

function setStoryText(el, text, sanity) {
  el.textContent = "";
  const rate = corruptionRate(sanity);
  let plain = "";
  for (const ch of text) {
    if (rate && /[A-Za-z]/.test(ch) && Math.random() < rate) {
      if (plain) { el.appendChild(document.createTextNode(plain)); plain = ""; }
      const span = document.createElement("span");
      span.className = "glitch";
      span.dataset.real = ch;
      span.textContent = GLITCH[Math.floor(Math.random() * GLITCH.length)];
      el.appendChild(span);
    } else {
      plain += ch;
    }
  }
  if (plain) el.appendChild(document.createTextNode(plain));
}

let currentSanity = 100;
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

function flickerRate(sanity) {
  const s = Math.min(Math.max(sanity, 0), 50);
  return 0.4 + ((50 - s) / 50) * 2.6;
}

setInterval(() => {
  if (reduceMotion) return;
  const chance = flickerRate(currentSanity) * 0.1;
  for (const span of document.querySelectorAll(".glitch")) {
    if (Math.random() < chance) {
      span.textContent = span.textContent === span.dataset.real
        ? GLITCH[Math.floor(Math.random() * GLITCH.length)]
        : span.dataset.real;
    }
  }
}, 100);

startGame();
