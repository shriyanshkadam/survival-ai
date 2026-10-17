from survival.engine.state import Phase

STYLE = (
    "You are the narrator of a realistic survival simulator game. "
    "Write in second person, 2 or 3 sentences, with concrete sensory details. "
    "Tone: grim, dry, a little sarcastic. Never cheerful. "
    "Describe ONLY what the facts say happened, never change the outcome. "
    "Do not invent items the player does not carry, and never mention numbers, "
    "health points or game mechanics."
)

SANITY_NOTES= {
    "steady": "",
    "frayed": "The player is rattled, let small details be slightly off",
    "unraveling":"The player is close to breaking: use fragmented sentences""and let one detail be unreliable",
}

HEALTH_BANDS= [(75, "fine"), (50, "hurt"), (25, "badly hurt"), (0,"near death")]
SANITY_BANDS= [(60, "steady"), (30, "frayed"), (0, "unraveling")]

def band(value, bands):
    for minimum, lable in bands:
        if value >= minimum:
            return lable
    return bands [-1][1]

def build_messages(game, intent, result, player_text):
    s = game.state
    mind= band(s.sanity, SANITY_BANDS)
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
        f"Outcome: {result['outcome']}" + (f" (reasons: {reasons})" if reasons else "") + "\n"
        f"Condition: {band(s.health, HEALTH_BANDS)}; "
        f"injuries: {', '.join(s.injuries) or 'none'}.\n"
        f"Carrying: {', '.join(s.inventory) or 'nothing'}.\n"
        f"Mental state: {mind}.\n"
        + ("The player has just died: write their final moments.\n"
           if s.phase == Phase.DEAD else "")
    )
    system = (STYLE + " " + SANITY_NOTES[mind]).strip()
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
    text = llm.generate(messages, temperature=0.9, max_tokens=200).strip()
    return text or fallback_narration(result)