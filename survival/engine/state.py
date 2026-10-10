from dataclasses import dataclass, field
from survival.engine.balance import SIZE_CLASSES
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
    capacity: int = 10
    item_sizes: dict[str, float] = field(default_factory=dict)

    def used_space(self):
        return sum(self.item_sizes.get(item,1) for item in self.inventory)

    def apply(self, health_delta= 0, sanity_delta= 0,
              add_items=(), remove_items=(),
              add_injuries=(), heal_injuries=(), new_item_sizes=None):
        
        if self.phase != Phase.PLAYING:
            return{"ok": False, "rejected":["game is over"]}

        rejected= []
        temp_inventory = list(self.inventory)
        for item in remove_items:
            if item in temp_inventory:
                temp_inventory.remove(item)
            else:
                rejected.append(f"cannot remove '{item}': not in inventory")

        temp_injuries = list(self.injuries)
        for injury in heal_injuries:
            if injury in temp_injuries:
                temp_injuries.remove(injury)
            else:
                rejected.append(f"cannot heal '{injury}': not injured")

        known_sizes = dict(self.item_sizes)
        pending= {}
        for item, size_class in (new_item_sizes or {}).items():
            if size_class not in SIZE_CLASSES:
                rejected.append(f'unknown size class"{size_class}" for "{item}"')
                continue
            size = SIZE_CLASSES[size_class]
            if item in known_sizes and known_sizes[item] != size:
                rejected.append(f'"{item}" already has size {known_sizes[item]}')
            else:
                pending[item] = size
        sizes = {**known_sizes, **pending}
        for item in add_items:
             if item not in sizes: 
                rejected.append(f"unknown size for'{item}': declare it in new_item_sizes")

        used = sum(sizes.get(item,1) for item in temp_inventory + list(add_items))
            
        if used > self.capacity:
            rejected.append(f"not enough space: need {used}, capacity is {self.capacity}")
    
        if rejected:
            return {"ok": False, "turn": self.turn, "rejected":rejected}

        health_before, sanity_before = self.health, self.sanity

        self.health = clamp(self.health + health_delta)
        self.sanity = clamp(self.sanity + sanity_delta)

        self.item_sizes.update(pending)
        for item in remove_items:

         self.inventory.remove(item)
        self.inventory.extend(add_items)

        for injury in heal_injuries:
            self.injuries.remove(injury)
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
    def to_dict(self):
        return {
            "health": self.health,
            "sanity": self.sanity,
            "injuries": list(self.injuries),
            "inventory": list(self.inventory),
            "turn": self.turn,
            "phase": self.phase.value,
            "capacity": self.capacity,
            "item_sizes": dict(self.item_sizes),
            
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            health = data["health"],
            sanity = data["sanity"],
            injuries = list(data["injuries"]),
            inventory = list(data["inventory"]),
            turn = data["turn"],
            phase = Phase(data["phase"]),
            capacity= data["capacity"],
            item_sizes= dict(data["item_sizes"])
            )



            
              