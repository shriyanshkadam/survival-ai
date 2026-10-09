from survival.engine.state import GameState, Phase
import json

#Testing basics rule of StateMachine

def test_health_cannot_exceed_100():
    s = GameState()
    s.apply(health_delta=50)
    assert s.health == 100

def test_health_cannot_go_below_0():
    s = GameState()
    s.apply(health_delta=-500)
    assert s.health == 0

def test_removing_basic_item_is_rejected():
    s = GameState()
    result = s.apply(remove_items=["rope"])
    assert len(result["rejected"]) == 1

def test_death_blocks_further_changes():
    s = GameState()
    s.apply(health_delta=-500)
    assert s.phase == Phase.DEAD
    result = s.apply(health_delta=50)
    assert result["ok"] is False
    assert s.health == 0

# More basic tests for reworked state

def test_rejected_action_changes_nothing_costs_no_turn():
    s = GameState()
    result = s.apply(health_delta=-20, remove_items=["rope"])
    assert result["ok"] is False
    assert s.health == 100
    assert s.turn == 0

def test_removing_same_item_twice_with_one_copy_is_rejected():
    s = GameState(inventory=["rope"])
    result = s.apply(remove_items=["rope", "rope"])
    assert result["ok"] is False
    assert s.inventory == ["rope"]


def test_round_trip_preserves_state():
    s = GameState(inventory=["rope"], injuries=["broken arm"])
    s.apply(health_delta= -20)
    copy = GameState.from_dict(s.to_dict())
    assert copy == s

def test_to_dict_is_json_safe():
    s = GameState()
    json.dumps(s.to_dict())


def test_to_dict_returns_copy():
    s = GameState(inventory=["rope"])
    d = s.to_dict()
    d["inventory"].append("knife")
    assert s.inventory == ["rope"]