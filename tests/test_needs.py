import random

from survival.engine.needs import upkeep
from survival.engine.rules import Intent, resolve
from survival.engine.state import GameState

SNOW_NIGHT = {"setting": "snowy valley", "start_hour": 22}
SNOW_DAY = {"setting": "snowy valley", "start_hour": 12}
DESERT_DAY = {"setting": "desert highway", "start_hour": 12}
FOREST_DAY = {"setting": "dense forest", "start_hour": 12}


def test_heat_raises_thirst():
    hot = upkeep(GameState(temp=95), DESERT_DAY, 60)["water"]
    calm = upkeep(GameState(temp=50), DESERT_DAY, 60)["water"]
    assert hot < calm


def test_cold_raises_hunger():
    cold = upkeep(GameState(temp=10), SNOW_NIGHT, 60)["food"]
    calm = upkeep(GameState(temp=50), SNOW_NIGHT, 60)["food"]
    assert cold < calm


def test_resting_recovers_sanity_when_safe():
    assert upkeep(GameState(sanity=50), FOREST_DAY, 120, "rest")["sanity"] == 4


def test_no_sanity_recovery_with_an_acute_injury():
    s = GameState(sanity=50, injury_info={"cut": {
        "phase": "acute", "effects": [], "stabilize": {"by": [], "hours": 1}, "since": 0}})
    assert upkeep(s, FOREST_DAY, 120, "rest")["sanity"] == 0

def test_cold_night_pulls_temp_down():
    d = upkeep(GameState(), SNOW_NIGHT, 120)
    assert d["temp"] < -10


def test_blanket_keeps_you_warmer():
    cold = upkeep(GameState(), SNOW_NIGHT, 240)["temp"]
    wrapped = upkeep(GameState(inventory=["space blanket"]), SNOW_NIGHT, 240)["temp"]
    assert wrapped > cold


def test_empty_water_costs_health():
    s = GameState(water=0)
    assert upkeep(s, SNOW_NIGHT, 60)["health"] == -5


def test_freezing_costs_health():
    assert upkeep(GameState(temp=0), SNOW_NIGHT, 60)["health"] <= -7

def test_eating_snow_gives_water_and_costs_temp():
    intent = Intent(description="eat snow", ingests="snow", minutes=30)
    for seed in range(30):
        s = GameState(water=50, temp=50)
        r = resolve(s, intent, random.Random(seed), SNOW_DAY)
        if r["outcome"] == "success":
            assert s.water > 50
            assert s.temp < 45
            return
    assert False

def test_eating_carried_item_restores_food():
    s = GameState(food=50, inventory=["energy bar"], item_sizes={"energy bar": 0.5})
    intent = Intent(description="eat", consumes=["energy bar"], ingests="energy bar", minutes=60)
    r = resolve(s, intent, random.Random(1), SNOW_DAY)
    assert r["ok"]
    assert s.food == 72.0


def test_unknown_thing_is_rejected():
    intent = Intent(description="eat pizza", ingests="pizza")
    r = resolve(GameState(), intent, random.Random(1), SNOW_DAY)
    assert r["outcome"] == "rejected"


def test_nothing_to_find_in_desert():
    env = {"setting": "desert highway", "start_hour": 12}
    r = resolve(GameState(), Intent(description="find berries", ingests="berries"), random.Random(1), env)
    assert r["outcome"] == "rejected"


def test_eating_a_rock_hurts():
    s = GameState(sanity=60)
    resolve(s, Intent(description="eat rock", ingests="rock"), random.Random(1), SNOW_DAY)
    assert "broken tooth" in s.injuries
    assert s.sanity == 55


def test_no_environment_means_no_drain():
    s = GameState()
    resolve(s, Intent(description="wait", minutes=60), random.Random(1))
    assert s.food == 100


def test_insects_map_to_grubs():
    from survival.engine.items import match_key
    assert match_key("some insects") == "grubs"
    assert match_key("licorice") is None