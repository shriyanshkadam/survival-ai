from survival.engine.clock import hour_at, phase_of_day


def test_hour_wraps_past_midnight():
    assert hour_at(23, 120) == 1.0

def test_phases():
    assert phase_of_day(6) == "dawn"
    assert phase_of_day(12) == "day"
    assert phase_of_day(18) == "dusk"
    assert phase_of_day(2) == "night"