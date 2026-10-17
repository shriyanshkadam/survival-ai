import json

from survival.engine.game import Game
from survival.llm.mock import MockLLM
from survival.pipeline.turn import play_text


def test_full_turn_with_mock_llm():
    game = Game(seed=1)
    llm = MockLLM([json.dumps({"description": "rest"}), "You catch your breath."])
    out = play_text(game, llm, "rest")
    assert out["narrative"] == "You catch your breath."
    assert game.log.events[-1].narrative == "You catch your breath."
    assert game.state.turn == 1


def test_unparseable_input_costs_no_turn():
    game = Game(seed=1)
    llm = MockLLM(["nope", "still nope"])
    out = play_text(game, llm, "asdf")
    assert out["ok"] is False
    assert game.state.turn == 0
    assert len(game.log.events) == 0