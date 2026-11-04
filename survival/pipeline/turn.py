import time

from survival.llm.base import LLMUnavailable
from survival.pipeline.action_parser import parse_action
from survival.pipeline.narrator import fallback_narration, narrate


def model_name(llm):
    return getattr(llm, "last_used", None)


def play_text(game, llm, player_text, logger=None):
    started = time.monotonic()

    def record(kind, **fields):
        if logger:
            logger.write({"kind": kind, "input": player_text,
                          "seconds": round(time.monotonic() - started, 2), **fields})

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