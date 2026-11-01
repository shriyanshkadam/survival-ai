from dataclasses import dataclass, field
from survival.engine.balance import (
    RISK_FAIL_CHANCE, INJURY_SEVERITY, DEFAULT_MINUTES, MIN_MINUTES, MAX_MINUTES,
    INGEST_PROFILES, FINDABLE, ALWAYS_AVAILABLE, FORAGE_MISS_CHANCE,
    STRESS_SANITY, EFFORT_DRAIN_MULT, IMPOSSIBLE_INJURY_WORDS, HARM_CAP_NO_CLIMB,
)
from survival.engine.injuries import (
    action_modifiers, can_treat, make_info, normalize_tier, same_part, tier_rank,
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
    tags: list[str] = field(default_factory=list)
    treats: str = ""
    treatment: str = ""
    injury_effects: list[dict] = field(default_factory=list)
    effort: str = "light"
    stress: str = "none"


def resolve(state, intent, rng, env=None):
    rejected = []
    for item in intent.requires:
        if item not in state.inventory:
            rejected.append(f"missing required item '{item}'")
    if intent.risk not in RISK_FAIL_CHANCE:
        rejected.append(f"unknown risk level'{intent.risk}'")
    if intent.risk != "none" and intent.harm not in INJURY_SEVERITY:
        rejected.append(f"unknown harm tier'{intent.harm}'")
    for word in IMPOSSIBLE_INJURY_WORDS:
        if word in (intent.injury or "").lower():
            rejected.append(f"'{intent.injury}' cannot happen from this action")
            break

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

    harm = intent.harm if intent.harm in INJURY_SEVERITY else "minor"
    if harm in ("critical", "lethal") and "climb" not in intent.tags:
        harm = HARM_CAP_NO_CLIMB
    effort = intent.effort if intent.effort in EFFORT_DRAIN_MULT else "light"
    stress = STRESS_SANITY.get(intent.stress, 0)

    try:
        minutes = int(intent.minutes)
    except (TypeError, ValueError):
        minutes = DEFAULT_MINUTES
    mods = action_modifiers(state, intent.tags)
    minutes = clamp(int(clamp(minutes, MIN_MINUTES, MAX_MINUTES) * mods["minutes_mult"]),
                    MIN_MINUTES, MAX_MINUTES)
    drain = upkeep(state, env, minutes, effort)

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
        low, high = INJURY_SEVERITY[harm]
        damage = rng.randint(low, high)
        names, profiles, heal, hit_again = [], {}, [], None
        if intent.injury:
            if intent.injury in state.injuries:
                hit_again = intent.injury
            else:
                clash = same_part(state, intent.injury)
                if clash is None:
                    names = [intent.injury]
                else:
                    old_tier = state.injury_info.get(clash, {}).get("tier", "minor")
                    if tier_rank(normalize_tier(harm)) > tier_rank(old_tier):
                        names = [intent.injury]
                        heal = [clash]
                    else:
                        hit_again = clash
            if names:
                profiles[names[0]] = make_info(
                    names[0], harm, state.elapsed_minutes + minutes, intent.injury_effects)
        result = state.apply(
            health_delta=-damage + drain["health"],
            sanity_delta=drain["sanity"] - stress,
            food_delta=drain["food"], water_delta=drain["water"], warmth_delta=drain["warmth"],
            add_injuries=names, heal_injuries=heal, injury_profiles=profiles, minutes=minutes,
        )
        if result["ok"]:
            if names:
                result["new_injury"] = names[0]
            if hit_again:
                result["hit_again"] = hit_again
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
            sanity_delta=drain["sanity"] + effects.get("sanity", 0) - stress,
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