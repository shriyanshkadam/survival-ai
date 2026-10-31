from dataclasses import dataclass, field
from survival.engine.balance import SIZE_CLASSES
from enum import Enum
import copy

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
    elapsed_minutes: int = 0
    food: float = 100.0
    water: float = 100.0
    warmth: float = 100.0
    injury_info: dict = field(default_factory=dict)

    def used_space(self):
        return sum(self.item_sizes.get(item,1) for item in self.inventory)

    def _stabilize(self, name):
        info = self.injury_info.get(name)
        if not info:
            return
        info["phase"] = "stabilized"
        info["effects"] = [e for e in info["effects"] if e.get("when") == "always"]

    def _age_injuries(self):
        for name, info in self.injury_info.items():
            if info.get("phase") != "acute":
                continue
            hours = info.get("stabilize", {}).get("hours", 24)
            if self.elapsed_minutes - info.get("since", 0) >= hours * 60:
                self._stabilize(name)

    def apply(self, health_delta= 0, sanity_delta= 0,
              add_items=(), remove_items=(),
              add_injuries=(), heal_injuries=(), new_item_sizes=None, minutes=0,
              food_delta=0, water_delta=0, warmth_delta=0,
              injury_profiles=None, stabilize_injuries=()
            ):
        
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
        for injury in stabilize_injuries:
            info = self.injury_info.get(injury)
            if injury not in temp_injuries or not info or info.get("phase") != "acute":
                rejected.append(f"cannot stabilize '{injury}'")

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
        self.food = clamp(self.food + food_delta)
        self.water = clamp(self.water + water_delta)
        self.warmth = clamp(self.warmth + warmth_delta)

        self.item_sizes.update(pending)
        for item in remove_items:

         self.inventory.remove(item)
        self.inventory.extend(add_items)

        for injury in heal_injuries:
            self.injuries.remove(injury)
            self.injury_info.pop(injury, None)
        for injury in add_injuries:
            if injury not in self.injuries:
                self.injuries.append(injury)
                if injury_profiles and injury in injury_profiles:
                    self.injury_info[injury] = copy.deepcopy(injury_profiles[injury])
        for injury in stabilize_injuries:
            self._stabilize(injury)

        self.elapsed_minutes += minutes
        self._age_injuries()
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
            "needs": {"food": self.food, "water": self.water, "warmth": self.warmth},
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
            "elapsed_minutes": self.elapsed_minutes,
            "food": self.food,
            "water": self.water,
            "warmth": self.warmth,
            "injury_info": copy.deepcopy(self.injury_info),
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
            item_sizes= dict(data["item_sizes"]),
            elapsed_minutes= data.get("elapsed_minutes", 0),
            food= data.get("food", 100.0),
            water= data.get("water", 100.0),
            warmth= data.get("warmth", 100.0),
            injury_info= copy.deepcopy(data.get("injury_info", {})),
            )



            
              