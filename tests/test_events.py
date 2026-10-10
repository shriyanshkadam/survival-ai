from survival.engine.state import GameState
from survival.engine.events import Event, EventLog

def play(state, log, changes, text=""):
    before = state.to_dict()
    result = state.apply(**changes)
    log.add(Event(
        turn = state.turn,
        player_input= text,
        changes= changes,
        ok= result["ok"],
        rejected= result["rejected"],
        state_before= before,
        state_after= state.to_dict(),
    ))


def test_last_return_most_recent_events():
    state, log = GameState(), EventLog()
    for _ in range(5):
        play(state, log, {"health_delta": -1})
    assert [e.turn for e in log.last(2)] == [4,5]


def test_save_and_load_round_trip(tmp_path):
    state, log = GameState(), EventLog()
    play(state, log, {"health_delta": -20}, "fell of a ledge")
    play(state, log, {"add_items": ["rusty knife"]}, "found a rusty knife")
    path = tmp_path / "game.jsonl"
    log.save(path)
    assert EventLog.load(path).to_list() == log.to_list()


def test_replaying_log_produces_final_state():
    state, log = GameState(), EventLog()
    play(state, log, {"health_delta": -20})
    play(state, log, {"add_items": ["Rusty Knife"]})
    play(state, log, {"remove_items": ["Stick"]}) #Should be Rejected

    replay = GameState()
    for e in log.events:
        replay.apply(**e.changes)
    assert replay.to_dict() == log.events[-1].state_after
