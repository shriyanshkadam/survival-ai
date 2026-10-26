import secrets
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from survival.engine.clock import hour_at, phase_of_day
from survival.engine.game import Game
from survival.llm.groq_llm import GroqLLM
from survival.pipeline.turn import play_text
from pathlib import Path

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from survival.pipeline.narrator import fallback_opening, narrate_opening

load_dotenv()

app = FastAPI()
llm = GroqLLM()
games = {}
STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

MAX_INPUT_LENGTH = 300

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
        "phase_of_day": phase_of_day(hour)

    }

@app.get("/api/ping")
def ping():
    return {"status": "ok"}


@app.post("/api/new")
def new_game():
    game_id = secrets.token_hex(8)
    game = Game(secrets.randbits(32))
    games[game_id] = game
    s = game.scenario
    try:
        opening = narrate_opening(llm, game)
    except RuntimeError:
        opening = fallback_opening(game)
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
    try:
        out = play_text(game, llm, text)
        if game.log.events: print("INTENT:", game.log.events[-1].changes, game.log.events[-1].rejected) 
    except RuntimeError:
        raise HTTPException(status_code=502, detail="The simulator hit a problem. Try again.")
    return {
        "ok": out["ok"],
        "outcome": out.get("outcome"),
        "narrative": out["narrative"],
        "state": snapshot(game),
    }

@app.get("/")
def home():
    return FileResponse(STATIC_DIR / "index.html")