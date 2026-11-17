import secrets
import time
import traceback
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from survival.engine.clock import hour_at, phase_of_day, sky_phase
from survival.engine.game import Game
from survival.llm.factory import build_llm, build_guard_llm
from survival.pipeline.turn import play_text
from pathlib import Path
from survival.llm.base import LLMUnavailable
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from survival.pipeline.narrator import fallback_opening, narrate_opening
from survival.pipeline.session_log import SessionLogger
from survival.version import VERSION

load_dotenv()

app = FastAPI()
llm = build_llm()
guard_llm = build_guard_llm()
print("Providers:", [p.name for p in llm.providers], flush=True)
games = {}
loggers = {}
STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

MAX_INPUT_LENGTH = 300
MAX_TURNS = 150
MAX_GAMES = 200
IDLE_SECONDS = 3600
last_seen = {}


def drop_game(game_id):
    games.pop(game_id, None)
    loggers.pop(game_id, None)
    last_seen.pop(game_id, None)


def cleanup():
    now = time.monotonic()
    for game_id in [g for g, t in last_seen.items() if now - t > IDLE_SECONDS]:
        drop_game(game_id)
    while len(games) >= MAX_GAMES:
        drop_game(min(last_seen, key=last_seen.get))

class TurnRequest(BaseModel):
    game_id: str
    text: str

def snapshot(game):
    state = game.state
    hour = hour_at(game.scenario.start_hour, state.elapsed_minutes)
    return {
        **state.to_dict(),
        "used_space": state.used_space(),
        "hour": round(hour, 2),
        "phase_of_day": phase_of_day(hour),
        "sky": sky_phase(hour),
    }

@app.get("/api/ping")
def ping():
    return {"status": "ok"}


@app.post("/api/new")
def new_game():
    cleanup()
    game_id = secrets.token_hex(8)
    game = Game(secrets.randbits(32))
    games[game_id] = game
    last_seen[game_id] = time.monotonic()
    loggers[game_id] = SessionLogger(game_id, game)
    s = game.scenario
    try:
        opening = narrate_opening(llm, game)
    except RuntimeError:
        opening = fallback_opening(game)
    loggers[game_id].write({"kind": "opening", "text": opening,
                            "narrator_model": getattr(llm, "last_used", None)})
    return {
        "game_id": game_id,
        "scenario": {"character": s.character, "setting": s.setting, "cause": s.cause},
        "state": snapshot(game),
        "opening": opening,
    }

@app.post("/api/turn")
def take_turn(req: TurnRequest):
    game = games.get(req.game_id)
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found! start new game.")
    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Type an action first.")
    if len(text) > MAX_INPUT_LENGTH:
        raise HTTPException(status_code=400, detail="That action is too long.")
    last_seen[req.game_id] = time.monotonic()
    if game.state.turn >= MAX_TURNS:
        return {
            "ok": False,
            "outcome": "rejected",
            "narrative": "This story has gone on long enough. Start a new game to try again.",
            "state": snapshot(game),
        }
    try:
        out = play_text(game, llm, text, loggers.get(req.game_id), guard_llm=guard_llm)
    except (RuntimeError, LLMUnavailable):
        raise HTTPException(status_code=502, detail="The simulator hit a problem. Try again.")
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Something went wrong. Try again.")
    return {
        "ok": out["ok"],
        "outcome": out.get("outcome"),
        "narrative": out["narrative"],
        "state": snapshot(game),
    }

@app.get("/api/version")
def version():
    return {"version": VERSION}


@app.api_route("/", methods=["GET", "HEAD"])
def home():
    return FileResponse(STATIC_DIR / "index.html")
