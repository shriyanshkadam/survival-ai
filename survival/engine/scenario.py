from dataclasses import dataclass
from survival.engine.balance import (CARRY_CAPACITY, HAND_CAPACITY, INJURY_SEVERITY, MAX_START_INJURIES, MIN_START_HEALTH, SIZE_CLASSES, START_INJURY_WEIGHTS, START_SANITY)
from survival.engine.scenario_data import CAUSES, CHARACTERS, SETTINGS, START_INJURIES
from survival.engine.state import GameState

@dataclass
class Scenario:
    character: str
    setting: str
    cause: str
    state: GameState

def roll_scenario(rng):
    character = rng.choice(list(CHARACTERS))
    kit = CHARACTERS[character]
    setting = rng.choice(SETTINGS)
    cause= rng.choice(CAUSES)

    cap_low, cap_high = CARRY_CAPACITY[kit["gear"]]
    capacity = HAND_CAPACITY + rng.randint(cap_low, cap_high)

    inventory= list(kit["items"])
    item_sizes = {name: SIZE_CLASSES[size] for name, size in kit["items"].items()}

    injuries= []
    damage = 0
    tiers= list(START_INJURY_WEIGHTS)
    weights = list(START_INJURY_WEIGHTS.values())
    for _ in range(rng.randint(0, MAX_START_INJURIES)):
        tier = rng.choices(tiers, weights= weights)[0]
        injury = rng.choice(START_INJURIES[tier])
        if injury in injuries: 
            continue
        injuries.append(injury)
        low, high = INJURY_SEVERITY[tier]
        damage += rng.randint(low, high)

    health = max(MIN_START_HEALTH, 100- damage)
    sanity = rng.randint(*START_SANITY)

    state = GameState(
        health=health, sanity=sanity, injuries=injuries, inventory=inventory,
        capacity=capacity, item_sizes=item_sizes,
    )
    return Scenario(character, setting, cause, state)


