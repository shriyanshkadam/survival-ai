from survival.llm.base import LLMUnavailable
from survival.pipeline.action_parser import parse_action
from survival.pipeline.narrator import fallback_narration, narrate


def play_text(game, llm, player_text):
    try:
        intent, error = parse_action(llm, player_text, game.state)
    except LLMUnavailable:
        return {"ok": False, "error": "llm_unavailable",
                "narrative": "The simulator is resting. Try again in a minute."}
    if intent is None:
        return {
            "ok": False,
            "narrative": "You can't make sense of your own plan. Try describing what you do.",
            "error": error,
        }
    result = game.play_turn(intent, player_text)
    try:
        narrative = narrate(llm, game, intent, result, player_text)
    except LLMUnavailable:
        narrative = fallback_narration(result)
    game.log.events[-1].narrative = narrative
    return {**result, "narrative": narrative, "state": game.state.to_dict()}