import math

from survival.engine.balance import (
    COLD_FOOD_MULT, COLD_THRESHOLD, FOOD_DRAIN, HEAT_THIRST_MULT,
    STARVATION_HEALTH_PER_HOUR, WARMTH_DRAIN, WARMTH_PROTECTION, WATER_DRAIN,
)
from survival.engine.clock import hour_at, phase_of_day

STEP_MINUTES = 30


def protection(inventory):
    best = 0.0
    for item in inventory:
        for word, value in WARMTH_PROTECTION.items():
            if word in item and value > best:
                best = value
    return best


def upkeep(state, env, minutes):
    none = {"food": 0.0, "water": 0.0, "warmth": 0.0, "health": 0}
    if not env or minutes <= 0:
        return none
    setting = env["setting"]
    start_hour = env["start_hour"]
    shield = protection(state.inventory)
    level = {"food": state.food, "water": state.water, "warmth": state.warmth}
    before = dict(level)
    health_loss = 0.0
    done = 0
    while done < minutes:
        step = min(STEP_MINUTES, minutes - done)
        hours = step / 60
        phase = phase_of_day(hour_at(start_hour, state.elapsed_minutes + done))
        cold = WARMTH_DRAIN.get(setting, {}).get(phase, 2)
        rates = {
            "warmth": cold * (1 - shield),
            "food": FOOD_DRAIN * (COLD_FOOD_MULT if cold >= COLD_THRESHOLD else 1.0),
            "water": WATER_DRAIN * HEAT_THIRST_MULT.get(setting, {}).get(phase, 1.0),
        }
        for name, rate in rates.items():
            drain = rate * hours
            if drain > 0:
                share_at_zero = min(1.0, max(0.0, drain - level[name]) / drain)
                health_loss += share_at_zero * hours * STARVATION_HEALTH_PER_HOUR[name]
            level[name] = max(0.0, level[name] - drain)
        done += step
    result = {name: round(level[name] - before[name], 2) for name in level}
    result["health"] = -math.ceil(health_loss) if health_loss > 0.01 else 0
    return result