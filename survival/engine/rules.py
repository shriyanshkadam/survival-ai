from dataclasses import dataclass, field
from survival.engine.balance import (
    RISK_FAIL_CHANCE, INJURY_SEVERITY, DEFAULT_MINUTES, MIN_MINUTES, MAX_MINUTES,
    INGEST_PROFILES, FINDABLE, ALWAYS_AVAILABLE, FORAGE_MISS_CHANCE,
)
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
    if rejected:
        return {"ok": False, "turn": state.turn, "rejected": rejected, "outcome": "rejected"}

    try:
        minutes = int(intent.minutes)
    except (TypeError, ValueError):
        minutes = DEFAULT_MINUTES
    minutes = clamp(minutes, MIN_MINUTES, MAX_MINUTES)
    drain = upkeep(state, env, minutes)
    failed = rng.random() < RISK_FAIL_CHANCE[intent.risk]
    missed = (foraging and not failed and key not in ALWAYS_AVAILABLE
              and rng.random() < FORAGE_MISS_CHANCE)

    if failed:
        low, high = INJURY_SEVERITY[intent.harm]
        damage = rng.randint(low, high)
        injuries = [intent.injury] if intent.injury else []
        result = state.apply(
            health_delta=-damage + drain["health"],
            food_delta=drain["food"], water_delta=drain["water"], warmth_delta=drain["warmth"],
            add_injuries=injuries, minutes=minutes,
        )
    else:
        effects = INGEST_PROFILES[key] if key and not missed else {}
        new_injuries = [effects["injury"][0]] if "injury" in effects else []
        result = state.apply(
            health_delta=drain["health"] + effects.get("health", 0),
            sanity_delta=effects.get("sanity", 0),
            food_delta=drain["food"] + effects.get("food", 0),
            water_delta=drain["water"] + effects.get("water", 0),
            warmth_delta=drain["warmth"] + effects.get("warmth", 0),
            add_injuries=new_injuries,
            remove_items=intent.consumes,
            add_items=intent.produces,
            new_item_sizes=intent.new_item_sizes,
            minutes=minutes,
        )
        if result["ok"] and effects:
            result["ingested"] = {"thing": key, "effects": effects}
        if result["ok"] and missed:
            result["found_nothing"] = True

    if not result["ok"]:
        result["outcome"] = "rejected"
    else:
        result["outcome"] = "failure" if (failed or missed) else "success"
    return result