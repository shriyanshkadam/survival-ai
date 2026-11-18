from dataclasses import dataclass
from survival.engine.balance import (CARRY_CAPACITY, HAND_CAPACITY, INJURY_SEVERITY, MAX_START_INJURIES, MIN_START_HEALTH, SIZE_CLASSES, START_INJURY_WEIGHTS, START_SANITY, START_NEEDS, FOOD_DRAIN, WATER_DRAIN, TEMP_MID)
from survival.engine.scenario_data import CHARACTERS, START_INJURIES, CAUSE_WARMTH_HIT, CAUSE_HOURS_OUT,CHARACTER_SETTINGS, CHARACTER_CAUSES
from survival.engine.state import GameState, clamp
from survival.engine.injuries import make_info
from survival.engine.clock import phase_of_day
from survival.engine.needs import ambient

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
    setting = rng.choice(CHARACTER_SETTINGS[character])
    cause = rng.choice(CHARACTER_CAUSES[character])

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
    ambient_now = ambient(setting, phase_of_day(start_hour))
    state.temp = int(clamp(
        TEMP_MID + (ambient_now - TEMP_MID) * 0.5
        - CAUSE_WARMTH_HIT.get(cause, 0) * 0.5 + rng.randint(-5, 5)
    ))
    return Scenario(character, setting, cause, state, start_hour, hours_out)
