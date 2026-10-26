from survival.engine.game import Game
from survival.engine.rules import Intent
from survival.llm.mock import MockLLM
from survival.pipeline.narrator import narrate, narrate_opening


def make():
    game = Game(seed=1)
    intent = Intent(description="rest")
    result = game.play_turn(intent, "rest a bit")
    return game, intent, result


def test_narration_comes_from_the_llm():
    game, intent, result = make()
    llm = MockLLM(["You sit and listen to the wind."])
    assert narrate(llm, game, intent, result, "rest a bit") == "You sit and listen to the wind."


def test_high_temperature_and_outcome_in_prompt():
    game, intent, result = make()
    llm = MockLLM(["ok"])
    narrate(llm, game, intent, result, "rest a bit")
    call = llm.calls[0]
    assert call["temperature"] >= 0.4
    assert "success" in call["messages"][1]["content"]


def test_empty_narration_falls_back():
    game, intent, result = make()
    llm = MockLLM(["   "])
    assert narrate(llm, game, intent, result, "rest a bit") != ""


def test_low_sanity_changes_the_style_prompt():
    game, intent, result = make()
    game.state.sanity = 10
    llm = MockLLM(["ok"])
    narrate(llm, game, intent, result, "rest")
    assert "fragmented" in llm.calls[0]["messages"][0]["content"]

def test_opening_uses_llm_text():
    game = Game(seed=1)
    assert narrate_opening(MockLLM(["You wake up cold."]), game) == "You wake up cold."