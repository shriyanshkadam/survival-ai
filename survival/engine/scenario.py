from dataclasses import dataclass
from survival.engine.balance import (CARRY_CAPACITY, HAND_CAPACITY, INJURY_SEVERITY, MAX_START_INJURIES, MIN_START_HEALTH, SIZE_CLASSES, START_INJURY_WEIGHTS, START_SANITY, START_NEEDS, FOOD_DRAIN, WARMTH_DRAIN, WARMTH_PROTECTION, WATER_DRAIN)
from survival.engine.scenario_data import CAUSES, CHARACTERS, SETTINGS, START_INJURIES, CAUSE_WARMTH_HIT, CAUSE_HOURS_OUT
from survival.engine.state import GameState, clamp
from survival.engine.injuries import make_info

@dataclass
class Scenario:
    character: str
    setting: str
    cause: str
    state: GameState
    start_hour: int = 12
    hours_out: int = 0


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
    info= {}
    damage = 0
    tiers= list(START_INJURY_WEIGHTS)
    weights = list(START_INJURY_WEIGHTS.values())
    for _ in range(rng.randint(0, MAX_START_INJURIES)):
        tier = rng.choices(tiers, weights= weights)[0]
        injury = rng.choice(START_INJURIES[tier])
        if injury in injuries: 
            continue
        injuries.append(injury)
        info[injury] = make_info(injury, tier, 0)
        low, high = INJURY_SEVERITY[tier]
        damage += rng.randint(low, high)

    health = max(MIN_START_HEALTH, 100- damage)
    sanity = rng.randint(*START_SANITY)

    state = GameState(
        health=health, sanity=sanity, injuries=injuries, inventory=inventory,
        capacity=capacity, item_sizes=item_sizes, injury_info= info,
    )
    start_hour = rng.randint(0, 23)
    hours_out = rng.randint(*CAUSE_HOURS_OUT[cause])
    state.food = int(clamp(100 - FOOD_DRAIN * hours_out + rng.randint(-10, 10)))
    state.water = int(clamp(100 - WATER_DRAIN * hours_out + rng.randint(-10, 10)))
    state.warmth = int(clamp(
        100 - WARMTH_DRAIN.get(setting, {}).get("day", 2) * hours_out
        - CAUSE_WARMTH_HIT.get(cause, 0) + rng.randint(-10, 10)
    ))
    return Scenario(character, setting, cause, state, start_hour, hours_out)
