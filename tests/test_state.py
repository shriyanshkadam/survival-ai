from survival.engine.state import GameState, Phase

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