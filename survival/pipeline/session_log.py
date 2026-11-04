import json
import os
from datetime import datetime
from pathlib import Path

from survival.version import VERSION

LOG_DIR = Path(__file__).resolve().parents[2] / "data" / "logs"


def logging_enabled():
    return os.environ.get("LOG_SESSIONS") == "1"


class SessionLogger:
    def __init__(self, game_id, game, enabled=None, directory=None):
        self.enabled = logging_enabled() if enabled is None else enabled
        self.path = None
        if not self.enabled:
            return
        folder = Path(directory) if directory else LOG_DIR
        try:
            folder.mkdir(parents=True, exist_ok=True)
        except OSError:
            self.enabled = False
            return
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.path = folder / f"{stamp}-{game_id}.jsonl"
        s = game.scenario
        self.write({
            "kind": "header",
            "version": VERSION,
            "game_id": game_id,
            "seed": game.seed,
            "character": s.character,
            "setting": s.setting,
            "cause": s.cause,
            "start_hour": s.start_hour,
            "hours_out": getattr(s, "hours_out", None),
            "state": game.state.to_dict(),
        })

    def write(self, record):
        if not self.enabled:
            return
        line = {"time": datetime.now().isoformat(timespec="seconds"), **record}
        try:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(json.dumps(line, ensure_ascii=False, default=str) + "\n")
        except OSError:
            pass