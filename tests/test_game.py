from survival.engine.game import Game
from survival.engine.rules import Intent

def test_same_seed_same_game():
    intents = [
        Intent(description="cross stream", risk = "medium", harm="moderate", injury="sprain"),
        Intent(description="climb rock", risk="high", harm="major", injury="broken arm"),
    ]
    a,b = Game(seed=1), Game(seed=1)
    for intent in intents:
        a.play_turn(intent)
        b.play_turn(intent)

    assert a.state.to_dict() == b.state.to_dict()

def test_rejected_turns_are_logged_too():
    g = Game(seed=2)
    g.play_turn(Intent(description="put up tent", requires=["tent"]))
    assert g.state.turn == 0
    g.play_turn(Intent(description="rest"))
    assert g.state.turn == 1
    assert len(g.log.events) == 2
    assert g.log.events[0].ok is False
    assert g.log.events[0].outcome == "rejected"

def test_replaying_the_log_reproduces_the_game():
    intents = [
        Intent(description="cross stream", risk="medium", harm="moderate", injury="sprain"),
        Intent(description="climb rock", risk="high", harm="major", injury="broken arm"),
        Intent(description="rest"),
    ]
    original = Game(seed=3)
    for intent in intents:
        original.play_turn(intent)

    replay = Game(seed=3)
    for event in original.log.events:
        replay.play_turn(Intent(**event.changes))
    assert replay.state.to_dict() == original.state.to_dict()