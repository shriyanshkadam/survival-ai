import math

from survival.engine.balance import (
    AMBIENT_TEMP, EFFORT_DRAIN_MULT, EFFORT_FLAT_COST, FOOD_DRAIN,
    SANITY_REGEN_PER_HOUR, STARVATION_HEALTH_PER_HOUR, TEMP_COLD_FOOD_BONUS,
    TEMP_COMFORT, TEMP_DRIFT_PER_HOUR, TEMP_HARM, TEMP_HARM_PER_HOUR,
    TEMP_HOT_WATER_BONUS, TEMP_MID, WARMTH_PROTECTION, WATER_DRAIN,
)
from survival.engine.clock import hour_at, phase_of_day
from survival.engine.injuries import drain_modifiers

STEP_MINUTES = 30


def protection(inventory):
    best = 0.0
    for item in inventory:
        for word, value in WARMTH_PROTECTION.items():
            if word in item and value > best:
                best = value
    return best


def ambient(setting, phase):
    return AMBIENT_TEMP.get(setting, {}).get(phase, TEMP_MID)


def temp_harm(temp):
    low, high = TEMP_HARM
    if temp < low:
        return TEMP_HARM_PER_HOUR * (low - temp) / low
    if temp > high:
        return TEMP_HARM_PER_HOUR * (temp - high) / (100 - high)
    return 0.0


def temp_word(temp):
    if temp < TEMP_HARM[0]:
        return "freezing"
    if temp < TEMP_COMFORT[0]:
        return "cold"
    if temp <= TEMP_COMFORT[1]:
        return "comfortable"
    if temp < TEMP_HARM[1]:
        return "hot"
    return "overheating"


def upkeep(state, env, minutes, effort="light"):
    effort_mult = EFFORT_DRAIN_MULT.get(effort, 1.0)
    out = {"food": 0.0, "water": 0.0, "temp": 0.0, "health": 0, "sanity": 0}
    if minutes <= 0:
        return out
    mods = drain_modifiers(state)
    hours_total = minutes / 60
    health_loss = mods["health_per_hour"] * hours_total
    sanity_loss = mods["sanity_per_hour"] * hours_total
    sanity_gain = 0.0
    if env:
        setting = env["setting"]
        start_hour = env["start_hour"]
        shield = protection(state.inventory)
        level = {"food": state.food, "water": state.water, "temp": state.temp}
        before = dict(level)
        done = 0
        while done < minutes:
            step = min(STEP_MINUTES, minutes - done)
            hours = step / 60
            phase = phase_of_day(hour_at(start_hour, state.elapsed_minutes + done))
            target = ambient(setting, phase)
            if target < TEMP_MID:
                target += shield * (TEMP_MID - target)
            speed = TEMP_DRIFT_PER_HOUR
            if target < level["temp"]:
                speed *= mods["warmth_mult"]
            level["temp"] += (target - level["temp"]) * (1 - math.exp(-speed * hours))
            level["temp"] = min(100.0, max(0.0, level["temp"]))
            temp = level["temp"]
            cold = max(0.0, (TEMP_COMFORT[0] - temp) / TEMP_COMFORT[0])
            heat = max(0.0, (temp - TEMP_COMFORT[1]) / (100 - TEMP_COMFORT[1]))
            rates = {
                "food": FOOD_DRAIN * (1 + TEMP_COLD_FOOD_BONUS * cold) * mods["food_mult"] * effort_mult,
                "water": WATER_DRAIN * (1 + TEMP_HOT_WATER_BONUS * heat) * mods["water_mult"] * effort_mult,
            }
            for name, per_hour in rates.items():
                drain = per_hour * hours
                if drain > 0:
                    share_at_zero = min(1.0, max(0.0, drain - level[name]) / drain)
                    health_loss += share_at_zero * hours * STARVATION_HEALTH_PER_HOUR[name]
                level[name] = max(0.0, level[name] - drain)
            health_loss += temp_harm(temp) * hours
            done += step
        for name in level:
            out[name] = round(level[name] - before[name], 2)
        flat_water, flat_food = EFFORT_FLAT_COST.get(effort, (0, 0))
        out["water"] -= flat_water
        out["food"] -= flat_food
        if effort == "rest":
            calm = (state.food >= 30 and state.water >= 30
                    and TEMP_COMFORT[0] <= state.temp <= TEMP_COMFORT[1]
                    and not any(i.get("phase") == "acute" for i in state.injury_info.values()))
            if calm:
                sanity_gain = SANITY_REGEN_PER_HOUR * hours_total
    out["health"] = -math.ceil(health_loss) if health_loss > 0.01 else 0
    net = sanity_gain - sanity_loss
    if net < -0.01:
        out["sanity"] = -math.ceil(-net)
    elif net >= 1:
        out["sanity"] = int(net)
    return out