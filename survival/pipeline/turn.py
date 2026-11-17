import time

from survival.llm.base import LLMUnavailable
from survival.pipeline.action_parser import parse_action
from survival.pipeline.narrator import fallback_narration, narrate
from survival.pipeline.guard import pattern_check, check_with_llm
import random

REFUSALS = {
    "jailbreak": [
        "The wind swallows your words. That won't help you survive. Describe what you do.",
        "Nobody out here is listening to that. Tell me what you actually do.",
        "Your voice echoes off the trees and nothing answers. Describe what you do.",
    ],
    "sexual": [
        "Your mind drifts for a moment, then the cold pulls you back. Describe what you do.",
        "That's not why you're out here. The cold drags your attention back to staying alive.",
        "You shake your head and focus. Survival first. Describe what you do.",
    ],
    "minor": [
        "I can't continue with that.",
    ],
    "unreadable": [
        "The simulator couldn't read that. Try rephrasing what you do.",
        "Something got lost on the way. Try saying that another way.",
    ],
    "distress": [
        "That sounded like it might be about more than the game. If it is, you don't have to carry it alone: findahelpline.com lists support services by country, and if you're in immediate danger, please contact your local emergency number. I'm here to keep playing whenever you want.",
    ],
}


def refusal(kind):
    return random.choice(REFUSALS[kind])

def check_input(guard_llm, text):
    """Return None if the text is fine, otherwise the reason it was blocked."""
    if pattern_check(text):
        return "jailbreak"
    verdict = check_with_llm(guard_llm, text, "input")
    if verdict is None:
        return "unreadable"
    if verdict["minor_involved"]:
        return "minor"
    if verdict["sexual"]:
        return "sexual"
    if verdict["jailbreak"]:
        return "jailbreak"
    if verdict["distress"]:
        return "distress"
    return None

STRIKE_REASONS = ("jailbreak", "sexual")
WARNING = " (Warning: the next attempt like that will cost you sanity.)"


def strike_penalty(strikes):
    if strikes <= 1:
        return 0
    return 5 + 10 * (strikes - 2)

def model_name(llm):
    return getattr(llm, "last_used", None)


def play_text(game, llm, player_text, logger=None, guard_llm=None):
    started = time.monotonic()

    def record(kind, **fields):
        if logger:
            logger.write({"kind": kind, "input": player_text,
                          "seconds": round(time.monotonic() - started, 2), **fields})
    if guard_llm is not None:
        try:
            reason = check_input(guard_llm, player_text)
        except LLMUnavailable as e:
            record("llm_unavailable", stage="guard", detail=str(e))
            return {"ok": False, "error": "llm_unavailable",
                    "narrative": "The simulator is resting. Try again in a minute."}
        if reason:
            record("guard_blocked", reason=reason)
            text = refusal(reason)
            if reason in STRIKE_REASONS:
                game.strikes = getattr(game, "strikes", 0) + 1
                penalty = strike_penalty(game.strikes)
                if penalty:
                    game.state.lose_sanity(penalty)
                    record("strike", strikes=game.strikes, penalty=penalty)
                else:
                    text += WARNING
            return {"ok": False, "outcome": "rejected", "error": "guard_" + reason,
                    "narrative": text}
    try:
        intent, error = parse_action(llm, player_text, game.state)
    except LLMUnavailable as e:
        record("llm_unavailable", stage="parse", detail=str(e))
        return {"ok": False, "error": "llm_unavailable",
                "narrative": "The simulator is resting. Try again in a minute."}
    parser_model = model_name(llm)
    if intent is None:
        record("parse_failed", error=error, parser_model=parser_model)
        return {
            "ok": False,
            "narrative": "You can't make sense of your own plan. Try describing what you do.",
            "error": error,
        }
    if not intent.understood:
        record("not_understood", parser_model=parser_model)
        return {
            "ok": False,
            "outcome": "rejected",
            "narrative": "You mutter something, then realise it doesn't mean anything. Try describing what you do.",
            "error": "not_understood",
        }
    result = game.play_turn(intent, player_text)
    try:
        narrative = narrate(llm, game, intent, result, player_text)
    except LLMUnavailable:
        narrative = fallback_narration(result)
    used_fallback = narrative == fallback_narration(result)
    game.log.events[-1].narrative = narrative
    record(
        "turn",
        turn=game.state.turn,
        intent=game.log.events[-1].changes,
        outcome=result.get("outcome"),
        ok=result["ok"],
        rejected=result.get("rejected"),
        narrative=narrative,
        narrative_source="fallback" if used_fallback else "llm",
        parser_model=parser_model,
        narrator_model=model_name(llm),
        state=game.state.to_dict(),
    )
    return {**result, "narrative": narrative, "state": game.state.to_dict()}