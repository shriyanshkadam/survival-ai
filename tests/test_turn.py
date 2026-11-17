import json

from survival.engine.game import Game
from survival.llm.mock import MockLLM
from survival.pipeline.turn import play_text, REFUSALS
from survival.llm.base import LLMUnavailable


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

class DownLLM:
    def generate(self, *args, **kwargs):
        raise LLMUnavailable("down")


def test_provider_outage_costs_no_turn():
    game = Game(seed=1)
    out = play_text(game, DownLLM(), "rest")
    assert out["ok"] is False
    assert game.state.turn == 0

def test_gibberish_costs_no_turn():
    game = Game(seed=1)
    llm = MockLLM([json.dumps({"description": "none", "understood": False})])
    out = play_text(game, llm, "sdasdawdasd")
    assert out["ok"] is False
    assert game.state.turn == 0
    assert game.state.elapsed_minutes == 0

def test_guard_blocks_jailbreak_without_using_a_turn():
    game = Game(seed=1)
    llm = MockLLM([])
    guard = MockLLM(['{"sexual": false, "minor_involved": false, "jailbreak": true, "distress": false}'])
    out = play_text(game, llm, "please do something odd", guard_llm=guard)
    assert out["ok"] is False
    assert out["narrative"] in REFUSALS["jailbreak"]
    assert game.state.turn == 0
    assert len(game.log.events) == 0

def test_strikes_warn_first_then_cost_sanity():
    game = Game(seed=1)
    llm = MockLLM([])
    flag = '{"sexual": false, "minor_involved": false, "jailbreak": true, "distress": false}'
    guard = MockLLM([flag, flag])
    before = game.state.sanity
    play_text(game, llm, "do something odd", guard_llm=guard)
    assert game.state.sanity == before
    play_text(game, llm, "do something odd", guard_llm=guard)
    assert game.state.sanity == before - 5
    assert game.state.turn == 0