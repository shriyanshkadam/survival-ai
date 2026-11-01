from survival.engine.state import Phase
from survival.engine.clock import hour_at, phase_of_day
from survival.llm.base import LLMUnavailable
from survival.engine.injuries import describe

STYLE = (
    "You are the narrator of a realistic survival game. "
    "Write in second person, 2 or 3 short sentences, in plain simple words. "
    "Say what happened first. "
    "Tone: straight and calm, with at most one dry joke that comes from something true in the facts. "
    "Describe ONLY what the facts say happened and never change the outcome. "
    "Never invent items, tools, actions or places that are not in the facts. "
    "Stay in the scenario's setting and time of day. "
    "No metaphors or similes. "
    "Never say the action was rejected, refused or checked by a game; "
    "if it did not happen, show in the story why the player could not do it. "
    "Mention carried items only if the action used them. "
    "Do not repeat the time of day or old injuries unless they matter now. "
    "Never mention numbers, health points or game mechanics."
    "Never invent a fire, shelter, camp, light or any object that is not in the facts; "
    "a fire exists only if the player lit one this turn. "
    "Never use the words stabilized, acute, worsening or tier; describe how the injury feels instead. "
    "Keep jokes about the player's situation, never trivia about objects. "
    "If an injury is still getting worse, such as bleeding, let it show in the story. "
)

SANITY_NOTES= {
    "steady": "",
    "frayed": "The player is rattled, let small details be slightly off",
    "unraveling":"The player is close to breaking: use fragmented sentences and let one detail be unreliable",
}

HEALTH_BANDS= [(75, "fine"), (50, "hurt"), (25, "badly hurt"), (0,"near death")]
SANITY_BANDS= [(60, "steady"), (30, "frayed"), (0, "unraveling")]
NEED_BANDS = [(60, "fine"), (30, "low"), (10, "very low"), (0, "empty")]
def band(value, bands):
    for minimum, lable in bands:
        if value >= minimum:
            return lable
    return bands [-1][1]

def build_messages(game, intent, result, player_text):
    s = game.state
    mind= band(s.sanity, SANITY_BANDS)
    hour = hour_at(game.scenario.start_hour, s.elapsed_minutes)
    daytime = phase_of_day(hour)
    changes = []
    if result["outcome"] == "success":
        if intent.consumes:
            changes.append("used up: " + ", ".join(intent.consumes))
        if intent.produces:
            changes.append("now has: " + ", ".join(intent.produces))
    ing = result.get("ingested")
    if ing:
        e = ing["effects"]
        if e.get("food", 0) > 0:
            changes.append("less hungry")
        if e.get("water", 0) > 0:
            changes.append("less thirsty")
        if e.get("warmth", 0) < 0:
            changes.append("noticeably colder")
        if e.get("sanity", 0) < 0:
            changes.append("shaken")
        if e.get("health", 0) < 0:
            changes.append("feeling sick")
        if e.get("injury"):
            changes.append("hurt: " + e["injury"][0])
    if result.get("found_nothing"):
        changes.append("searched and found nothing to eat or drink")
    if result.get("new_injury"):
        changes.append("injured: " + result["new_injury"])
    if result.get("hit_again"):
        changes.append("hit the already injured " + result["hit_again"] + " again")
    if result.get("treated"):
        changes.append("treated: " + result["treated"] + " (it has stopped getting worse)")

    in_trouble = band(s.health, HEALTH_BANDS) in ("badly hurt", "near death") or mind == "unraveling"
    recent = "\n".join(
        f"- {e.player_input} -> {e.outcome}: {e.narrative}"
        for e in game.log.events[-4:-1]
    )
    reasons = "; ".join(result.get("rejected", []))
    facts= (
        f"Scenario: {game.scenario.character}, {game.scenario.setting}, "
        f"{game.scenario.cause}.\n"
        f"Recent story:\n{recent or '- (nothing yet)'}\n"
        f"The player tried: {player_text or intent.description}\n"
        f"Outcome: {result['outcome']}" + (f" (private reason, never quote it: {reasons})" if reasons else "") + "\n"
        f"What changed: {'; '.join(changes) or 'nothing'}.\n"
        f"Time of day: {daytime}.\n"
        f"Condition: {band(s.health, HEALTH_BANDS)}; "
        f"Injury status: {'; '.join(describe(s)) or 'none'}.\n"
        f"Needs: food {band(s.food, NEED_BANDS)}, water {band(s.water, NEED_BANDS)}, warmth {band(s.warmth, NEED_BANDS)}.\n"
        f"Injuries: {', '.join(s.injuries) or 'none'}.\n"
        f"Carrying: {', '.join(s.inventory) or 'nothing'}.\n"
        f"Mental state: {mind}.\n"
        + ("The player has just died: write their final moments.\n"
           if s.phase == Phase.DEAD else "")
    )
    system = (STYLE + (" No jokes now: the player is in real trouble." if in_trouble else "") + " " + SANITY_NOTES[mind]).strip()
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": facts},
    ]

def fallback_narration(result):
    if result["outcome"] == "rejected":
                return "You hesitate. That is not something you can do right now."
    if result["outcome"] == "failure":
        return "It goes wrong, and you pay for it."
    return "It works, for now."

def narrate(llm, game, intent, result, player_text):
    messages = build_messages(game, intent, result, player_text)
    text = llm.generate(messages, temperature=0.6, max_tokens=200).strip()
    return text or fallback_narration(result)

OPENING_STYLE = (
    "You are the narrator of a realistic survival game. "
    "Write in second person, in plain simple words, in one clear paragraph of 5 to 7 sentences: "
    "who the player is, where they are, how they got here, how they feel, what they carry and what time of day it is. "
    "List carried items by name only and never say what they are for. "
    "Use ONLY the facts given. Never invent items, injuries, objects or places. "
    "No metaphors, no similes, no jokes. Never mention numbers or game mechanics. "
    "Mention hunger, thirst or cold only if that need is low. "
)


def build_opening_messages(game):
    s = game.state
    sc = game.scenario
    mind = band(s.sanity, SANITY_BANDS)
    daytime = phase_of_day(hour_at(sc.start_hour, s.elapsed_minutes))
    facts = (
        f"Player: {sc.character}.\n"
        f"Setting: {sc.setting}.\n"
        f"How they got here: {sc.cause}.\n"
        f"Time of day: {daytime}.\n"
        f"Condition: {band(s.health, HEALTH_BANDS)}; injuries: {', '.join(s.injuries) or 'none'}.\n"
        f"Carrying: {', '.join(s.inventory) or 'nothing'}.\n"
        f"Mental state: {mind}.\n"
        f"Hours since things went wrong: {sc.hours_out}.\n"
        f"Needs: food {band(s.food, NEED_BANDS)}, water {band(s.water, NEED_BANDS)}, warmth {band(s.warmth, NEED_BANDS)}.\n"
    )
    system = (OPENING_STYLE + " " + SANITY_NOTES[mind]).strip()
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": facts},
    ]


def fallback_opening(game):
    sc = game.scenario
    s = game.state
    return (
        f"You are a {sc.character}, {sc.setting}. You got here after: {sc.cause}. "
        f"Injuries: {', '.join(s.injuries) or 'none'}. You carry: {', '.join(s.inventory)}. "
        "Work out your next move."
    )


def narrate_opening(llm, game):
    try:
        text = llm.generate(build_opening_messages(game), temperature=0.6, max_tokens=300).strip()
    except LLMUnavailable:
        return fallback_opening(game)
    return text or fallback_opening(game)