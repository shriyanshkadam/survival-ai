import math

from survival.engine.balance import (
    DEFAULT_INJURY_EFFECTS, DEFAULT_STABILIZE_HOURS, INJURY_BUDGET, INJURY_HOOKS,
    INJURY_TAGS, KNOWN_INJURIES, MAX_ACTION_FAIL_BONUS, MAX_ACTION_FORAGE_MISS,
    MAX_ACTION_MINUTES_MULT, MAX_DRAIN_MULT, MAX_INJURY_EFFECTS, MAX_TOTAL_BLEED,BODY_PARTS, TIER_ORDER,
)

ACUTE_BY_DEFAULT = {
    "health_per_hour", "sanity_per_hour",
    "food_drain_mult", "water_drain_mult", "warmth_drain_mult",
}


def clean_effect(raw):
    if not isinstance(raw, dict):
        return None
    hook = raw.get("hook")
    if hook not in INJURY_HOOKS:
        return None
    try:
        value = float(raw.get("value"))
    except (TypeError, ValueError):
        return None
    if math.isnan(value):
        return None
    low, high = INJURY_HOOKS[hook]
    value = max(low, min(high, value))
    when = raw.get("when")
    if when not in ("acute", "always"):
        when = "acute" if hook in ACUTE_BY_DEFAULT else "always"
    effect = {"hook": hook, "value": round(value, 3), "when": when}
    tags = raw.get("tags")
    if hook == "fail_bonus" and isinstance(tags, list):
        tags = [t for t in tags if t in INJURY_TAGS][:3]
        if tags:
            effect["tags"] = tags
    return effect


def strength(effect):
    low, high = INJURY_HOOKS[effect["hook"]]
    return (effect["value"] - low) / (high - low)


def validate_effects(raw_list, tier):
    if not isinstance(raw_list, list):
        return []
    effects = [e for e in (clean_effect(r) for r in raw_list) if e][:MAX_INJURY_EFFECTS]
    total = sum(strength(e) for e in effects)
    budget = INJURY_BUDGET[tier]
    if total > budget:
        factor = budget / total
        for e in effects:
            low = INJURY_HOOKS[e["hook"]][0]
            e["value"] = round(low + (e["value"] - low) * factor, 3)
    return effects


def normalize_tier(tier):
    if tier == "lethal":
        return "critical"
    return tier if tier in INJURY_BUDGET else "minor"


def make_info(name, tier, since, proposed=None):
    known = KNOWN_INJURIES.get(name)
    if known:
        tier = known["tier"]
        effects = validate_effects(known["effects"], tier)
        stabilize = {"by": list(known["stabilize"]["by"]), "hours": known["stabilize"]["hours"]}
    else:
        tier = normalize_tier(tier)
        effects = validate_effects(proposed, tier) if proposed else []
        if not effects:
            effects = validate_effects(DEFAULT_INJURY_EFFECTS[tier], tier)
        stabilize = {"by": ["rest", "bandage"], "hours": DEFAULT_STABILIZE_HOURS[tier]}
    return {"tier": tier, "effects": effects, "stabilize": stabilize,
            "phase": "acute", "since": since}


def drain_modifiers(state):
    mods = {"health_per_hour": 0.0, "sanity_per_hour": 0.0,
            "food_mult": 1.0, "water_mult": 1.0, "warmth_mult": 1.0}
    for info in state.injury_info.values():
        for e in info.get("effects", []):
            hook, value = e["hook"], e["value"]
            if hook == "health_per_hour":
                mods["health_per_hour"] += value
            elif hook == "sanity_per_hour":
                mods["sanity_per_hour"] += value
            elif hook == "food_drain_mult":
                mods["food_mult"] *= value
            elif hook == "water_drain_mult":
                mods["water_mult"] *= value
            elif hook == "warmth_drain_mult":
                mods["warmth_mult"] *= value
    mods["health_per_hour"] = min(mods["health_per_hour"], MAX_TOTAL_BLEED)
    for key in ("food_mult", "water_mult", "warmth_mult"):
        mods[key] = min(mods[key], MAX_DRAIN_MULT)
    return mods


def action_modifiers(state, tags):
    mods = {"fail_bonus": 0.0, "forage_miss": 0.0, "minutes_mult": 1.0}
    tagset = set(tags or [])
    for info in state.injury_info.values():
        for e in info.get("effects", []):
            hook, value = e["hook"], e["value"]
            if hook == "fail_bonus":
                wanted = e.get("tags")
                if not wanted or tagset & set(wanted):
                    mods["fail_bonus"] += value
            elif hook == "forage_miss":
                mods["forage_miss"] += value
            elif hook == "action_minutes_mult":
                mods["minutes_mult"] *= value
    mods["fail_bonus"] = min(mods["fail_bonus"], MAX_ACTION_FAIL_BONUS)
    mods["forage_miss"] = min(mods["forage_miss"], MAX_ACTION_FORAGE_MISS)
    mods["minutes_mult"] = min(mods["minutes_mult"], MAX_ACTION_MINUTES_MULT)
    return mods


def can_treat(state, name, method):
    info = state.injury_info.get(name)
    if not info or info.get("phase") != "acute":
        return False
    return method in info["stabilize"]["by"]


def describe(state):
    out = []
    for name in state.injuries:
        info = state.injury_info.get(name)
        if info and info.get("phase") == "acute":
            how = " or ".join(info["stabilize"]["by"])
            out.append(f"{name} (still getting worse; can be treated with {how})")
        elif info:
            out.append(f"{name} (stabilized)")
        else:
            out.append(name)
    return out

def body_part(name):
    low = name.lower()
    for part, words in BODY_PARTS.items():
        if any(w in low for w in words):
            return part
    return None


def same_part(state, name):
    part = body_part(name)
    if part is None:
        return None
    for other in state.injuries:
        if other != name and body_part(other) == part:
            return other
    return None


def tier_rank(tier):
    return TIER_ORDER.index(tier) if tier in TIER_ORDER else 0