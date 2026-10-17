from survival.pipeline.action_parser import parse_action
from survival.pipeline.narrator import narrate


def play_text(game, llm, player_text):
    intent, error = parse_action(llm, player_text, game.state)
    if intent is None:
        return {
            "ok": False,
            "narrative": "You can't make sense of your own plan. Try describing what you do.",
            "error": error,
        }
    result = game.play_turn(intent, player_text)
    narrative = narrate(llm, game, intent, result, player_text)
    game.log.events[-1].narrative = narrative
    return {**result, "narrative": narrative, "state": game.state.to_dict()}