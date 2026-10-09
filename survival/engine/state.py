from dataclasses import dataclass, field
from enum import Enum

class Phase(Enum):
    PLAYING = "playing"
    DEAD = "dead"
    ESCAPED = "escaped"

def clamp(value, low=0, high=100):
    return max(low,min(high,value))

@dataclass
class GameState:
    health : int = 100
    sanity: int = 100
    injuries: list[str] = field(default_factory= list)
    inventory: list[str] = field(default_factory= list)
    turn: int = 0
    phase: Phase = Phase.PLAYING

    def apply(self, health_delta= 0, sanity_delta= 0,
              add_items=(), remove_items=(),
              add_injuries=(), heal_injuries=()):
        if self.phase != Phase.PLAYING:
            return{"ok": False, "rejected":["game is over"]}

        rejected= []
        health_before, sanity_before = self.health, self.sanity

        self.health = clamp(self.health + health_delta)
        self.sanity = clamp(self.sanity + sanity_delta)

        for item in remove_items:
            if item in self.inventory:
                self.inventory.remove(item)
            else:
                rejected.append(f"cannot remove '{item}': not in inventory")
        self.inventory.extend(add_items)

        for injury in heal_injuries:
            if injury in self.injuries:
                self.injuries.remove(injury)
            else:
                rejected.append(f"cannot remove'{injury}': not injured")

        for injury in add_injuries:
            if injury not in self.injuries:
                self.injuries.append(injury)

        self.turn += 1
        if self.health == 0 or self.sanity == 0:
            self.phase = Phase.DEAD

        return {
            "ok": True,
            "turn": self.turn,
            "health": (health_before, self.health),
            "sanity": (sanity_before, self.sanity),
            "rejected": rejected,
            "phase": self.phase.value,
        }
    


            
              