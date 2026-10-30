import random
from dataclasses import asdict
from survival.engine.events import Event, EventLog
from survival.engine.rules import resolve
from survival.engine.scenario import roll_scenario

class Game:
    def __init__(self, seed):
        self.seed = seed
        self.rng = random.Random(seed)
        self.scenario = roll_scenario(self.rng)
        self.state = self.scenario.state
        self.log = EventLog()

    def environment(self):
        return {"setting": self.scenario.setting, "start_hour": self.scenario.start_hour}

    def play_turn(self, intent, player_input=""):
        before = self.state.to_dict()
        result = resolve(self.state, intent, self.rng, self.environment())
        self.log.add(Event(
            turn = self.state.turn,
            player_input=player_input,
            changes= asdict(intent),
            ok = result["ok"],
            rejected=result["rejected"],
            state_before=before,
            state_after=self.state.to_dict(),
            outcome=result['outcome'],
            

        ))

        return result
        
