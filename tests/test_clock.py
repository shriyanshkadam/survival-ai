from survival.engine.clock import hour_at, phase_of_day


def test_hour_wraps_past_midnight():
    assert hour_at(23, 120) == 1.0

def test_phases():
    assert phase_of_day(6) == "dawn"
    assert phase_of_day(12) == "day"
    assert phase_of_day(18) == "dusk"
    assert phase_of_day(2) == "night"

def test_sky_phase_splits_the_day():
    from survival.engine.clock import sky_phase
    assert sky_phase(9) == "morning"
    assert sky_phase(14) == "afternoon"
    assert sky_phase(2) == "night"