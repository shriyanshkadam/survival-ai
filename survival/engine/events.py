import json
from dataclasses import dataclass, asdict

@dataclass
class Event:
    turn: int
    player_input: str
    changes: dict
    ok: bool
    rejected: list[str]
    state_before: dict
    state_after: dict
    narrative: str = ""

class EventLog:
    def __init__(self):
        self.events = []

    def add(self, event):
        self.events.append(event)

    def last(self, n):
        return self.events[-n:]

    def to_list(self):
        return [asdict(e) for e in self.events]

    def save(self, path):
        with open(path, "w", encoding='utf-8') as f:
            for e in self.events:
                f.write(json.dumps(asdict(e)) + '\n')

    @classmethod
    def load(cls, path):
        log = cls()
        with open(path, encoding='utf-8') as f:
            for line in f:
                log.add(Event(**json.loads(line)))
        return log