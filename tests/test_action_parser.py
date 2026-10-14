import json

from survival.engine.state import GameState
from survival.llm.mock import MockLLM
from survival.pipeline.action_parser import parse_action

GOOD = json.dumps({
    "description": "fill the bottle",
    "requires": [],
    "consumes": ["empty bottle"],
    "produces": ["full bottle"],
    "new_item_sizes": {"full bottle": "small"},
    "risk": "low",
    "harm": "minor",
    "injury": "",
})


def test_valid_json_becomes_intent():
    llm = MockLLM([GOOD])
    intent, error = parse_action(llm, "fill the bottle", GameState())
    assert error is None
    assert intent.consumes == ["empty bottle"]
    assert intent.risk == "low"


def test_fenced_json_is_accepted():
    fence = "`" * 3
    llm = MockLLM([f"{fence}json\n{GOOD}\n{fence}"])
    intent, error = parse_action(llm, "fill the bottle", GameState())
    assert error is None


def test_bad_output_is_retried_once():
    llm = MockLLM(["sorry, I can't do that", GOOD])
    intent, error = parse_action(llm, "fill the bottle", GameState())
    assert error is None
    assert len(llm.calls) == 2


def test_gives_up_after_retries():
    llm = MockLLM(["nope", "still nope"])
    intent, error = parse_action(llm, "fill the bottle", GameState())
    assert intent is None
    assert error is not None
    assert len(llm.calls) == 2


def test_unknown_fields_are_ignored():
    sneaky = json.dumps({"description": "heal", "health_delta": 999})
    llm = MockLLM([sneaky])
    intent, error = parse_action(llm, "heal myself", GameState())
    assert error is None
    assert not hasattr(intent, "health_delta")


def test_wrong_types_are_rejected():
    bad = json.dumps({"description": "x", "requires": "rope"})
    llm = MockLLM([bad, bad])
    intent, error = parse_action(llm, "use rope", GameState())
    assert intent is None
    assert "requires" in error


def test_prompt_has_low_temperature_and_inventory():
    llm = MockLLM([GOOD])
    state = GameState(inventory=["empty bottle"])
    parse_action(llm, "fill the bottle", state)
    call = llm.calls[0]
    assert call["temperature"] <= 0.2
    assert "empty bottle" in call["messages"][1]["content"]