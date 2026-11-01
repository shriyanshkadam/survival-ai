import random
from survival.engine.balance import MIN_START_HEALTH, START_SANITY
from survival.engine.scenario import roll_scenario
from survival.engine.state import Phase

def test_same_seed_gives_same_scenario():
    assert roll_scenario(random.Random(5)) == roll_scenario(random.Random(5))

def test_different_seeds_give_variety():
    scenarios= [roll_scenario(random.Random(i)) for i in range(100)]
    seen =  {(s.character, s.setting, s.cause) for s in scenarios}
    assert len(seen) > 10

def test_every_scenario_has_legal_start():
    low, high = START_SANITY
    for seed in range(500):
        s = roll_scenario(random.Random(seed)).state
        assert MIN_START_HEALTH <= s.health <= 100
        assert low <= s.sanity <= high
        assert s.used_space() <= s.capacity
        assert all(item in s.item_sizes for item in s.inventory)
        assert s.phase == Phase.PLAYING
        assert s.turn == 0

def test_start_hour_in_range():
    import random
    sc = roll_scenario(random.Random(1))
    assert 0 <= sc.start_hour <= 23

def test_start_needs_vary():
    import random
    seen = set()
    for seed in range(30):
        sc = roll_scenario(random.Random(seed))
        assert 0 <= sc.state.food <= 100
        seen.add((sc.state.food, sc.state.water))
    assert len(seen) > 5

def test_start_injuries_have_profiles():
    import random
    for seed in range(50):
        s = roll_scenario(random.Random(seed)).state
        for name in s.injuries:
            assert name in s.injury_info

def test_character_matches_setting_and_cause():
    from survival.engine.scenario_data import CHARACTER_CAUSES, CHARACTER_SETTINGS
    for seed in range(100):
        sc = roll_scenario(random.Random(seed))
        assert sc.setting in CHARACTER_SETTINGS[sc.character]
        assert sc.cause in CHARACTER_CAUSES[sc.character]