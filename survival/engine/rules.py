from dataclasses import dataclass, field
from survival.engine.balance import (
    RISK_FAIL_CHANCE, INJURY_SEVERITY, DEFAULT_MINUTES, MIN_MINUTES, MAX_MINUTES,
    INGEST_PROFILES, FINDABLE, ALWAYS_AVAILABLE, FORAGE_MISS_CHANCE,
)
from survival.engine.injuries import action_modifiers, can_treat, make_info
from survival.engine.items import match_key
from survival.engine.needs import upkeep
from survival.engine.state import clamp


@dataclass
class Intent:
    description: str
    requires: list[str] = field(default_factory=list)
    consumes: list[str] = field(default_factory=list)
    produces: list[str] = field(default_factory=list)
    new_item_sizes: dict[str, str] = field(default_factory=dict)
    risk: str = "none"
    harm: str = "minor"
    injury: str = ""
    minutes: int = DEFAULT_MINUTES
    ingests: str = ""
    tags: list[str] = field(default_factory=list)
    treats: str = ""
    treatment: str = ""
    injury_effects: list[dict] = field(default_factory=list)


def resolve(state, intent, rng, env=None):
    rejected = []
    for item in intent.requires:
        if item not in state.inventory:
            rejected.append(f"missing required item '{item}'")
    if intent.risk not in RISK_FAIL_CHANCE:
        rejected.append(f"unknown risk level'{intent.risk}'")
    if intent.risk != "none" and intent.harm not in INJURY_SEVERITY:
        rejected.append(f"unknown harm tier'{intent.harm}'")

    key = None
    foraging = False
    if intent.ingests:
        key = match_key(intent.ingests)
        if key is None:
            rejected.append(f"'{intent.ingests}' is not something that can be eaten or drunk here")
        elif not intent.consumes:
            foraging = True
            findable = FINDABLE.get(env["setting"], ()) if env else ()
            if key not in ALWAYS_AVAILABLE and key not in findable:
                rejected.append(f"no '{key}' can be found here")

    if intent.treats:
        if intent.treats not in state.injuries:
            rejected.append(f"you do not have an injury called '{intent.treats}'")
        elif not can_treat(state, intent.treats, intent.treatment):
            rejected.append(f"'{intent.treatment or 'that'}' cannot treat '{intent.treats}' right now")
    if rejected:
        return {"ok": False, "turn": state.turn, "rejected": rejected, "outcome": "rejected"}

    try:
        minutes = int(intent.minutes)
    except (TypeError, ValueError):
        minutes = DEFAULT_MINUTES
    mods = action_modifiers(state, intent.tags)
    minutes = clamp(int(clamp(minutes, MIN_MINUTES, MAX_MINUTES) * mods["minutes_mult"]),
                    MIN_MINUTES, MAX_MINUTES)
    drain = upkeep(state, env, minutes)

    base = RISK_FAIL_CHANCE[intent.risk]
    if intent.risk == "none":
        chance = 0.0
    elif base >= 1.0:
        chance = 1.0
    else:
        chance = min(0.95, base + mods["fail_bonus"])
    failed = rng.random() < chance
    miss_chance = min(0.9, FORAGE_MISS_CHANCE + mods["forage_miss"])
    missed = (foraging and not failed and key not in ALWAYS_AVAILABLE
              and rng.random() < miss_chance)

    if failed:
        low, high = INJURY_SEVERITY[intent.harm]
        damage = rng.randint(low, high)
        names = [intent.injury] if intent.injury else []
        since = state.elapsed_minutes + minutes
        profiles = {n: make_info(n, intent.harm, since, intent.injury_effects) for n in names}
        result = state.apply(
            health_delta=-damage + drain["health"], sanity_delta=drain["sanity"],
            food_delta=drain["food"], water_delta=drain["water"], warmth_delta=drain["warmth"],
            add_injuries=names, injury_profiles=profiles, minutes=minutes,
        )
        if result["ok"] and names:
            result["new_injury"] = names[0]
    else:
        effects = INGEST_PROFILES[key] if key and not missed else {}
        new_injuries = []
        profiles = {}
        if "injury" in effects:
            name, tier = effects["injury"]
            new_injuries = [name]
            profiles[name] = make_info(name, tier, state.elapsed_minutes + minutes)
        result = state.apply(
            health_delta=drain["health"] + effects.get("health", 0),
            sanity_delta=drain["sanity"] + effects.get("sanity", 0),
            food_delta=drain["food"] + effects.get("food", 0),
            water_delta=drain["water"] + effects.get("water", 0),
            warmth_delta=drain["warmth"] + effects.get("warmth", 0),
            add_injuries=new_injuries,
            injury_profiles=profiles,
            stabilize_injuries=[intent.treats] if intent.treats else [],
            remove_items=intent.consumes,
            add_items=intent.produces,
            new_item_sizes=intent.new_item_sizes,
            minutes=minutes,
        )
        if result["ok"] and effects:
            result["ingested"] = {"thing": key, "effects": effects}
        if result["ok"] and missed:
            result["found_nothing"] = True
        if result["ok"] and intent.treats:
            result["treated"] = intent.treats
        if result["ok"] and new_injuries:
            result["new_injury"] = new_injuries[0]

    if not result["ok"]:
        result["outcome"] = "rejected"
    else:
        result["outcome"] = "failure" if (failed or missed) else "success"
    return result