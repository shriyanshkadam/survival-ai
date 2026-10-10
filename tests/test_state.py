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


def test_big_item_does_not_fit():
    s = GameState(capacity=4)
    result = s.apply(add_items=["spear"], new_item_sizes={"spear": "large"})
    assert result["ok"] is False
    assert s.inventory == []


def test_small_items_fit():
    s = GameState(capacity=2)
    result = s.apply(add_items=["stick", "stick"], new_item_sizes={"stick": "small"})
    assert result["ok"] is True


def test_swapping_at_full_capacity_is_allowed():
    s = GameState(capacity=1, inventory=["stick"], item_sizes={"stick": 1})
    result = s.apply(remove_items=["stick"], add_items=["pebble"],
                     new_item_sizes={"pebble": "tiny"})
    assert result["ok"] is True
    assert s.inventory == ["pebble"]

def test_unknown_item_without_size_is_rejected():
    s = GameState()
    result = s.apply(add_items=["rope"])
    assert result["ok"] is False


def test_declaring_a_size_registers_it():
    s = GameState()
    result = s.apply(add_items=["rope"], new_item_sizes={"rope": "small"})
    assert result["ok"] is True
    assert s.item_sizes == {"rope": 1}


def test_size_cannot_be_changed_once_set():
    s = GameState()
    s.apply(add_items=["rope"], new_item_sizes={"rope": "small"})
    result = s.apply(add_items=["rope"], new_item_sizes={"rope": "large"})
    assert result["ok"] is False


def test_round_trip_keeps_capacity_and_sizes():
    s = GameState(capacity=7)
    s.apply(add_items=["rope"], new_item_sizes={"rope": "small"})
    assert GameState.from_dict(s.to_dict()) == s