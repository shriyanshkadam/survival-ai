import random

from survival.engine.rules import Intent, resolve
from survival.engine.state import GameState, Phase


class FixedRNG:
    #A fake number generator that returns the number tester choose

    def __init__(self, roll, damage):
        self.roll = roll
        self.damage = damage

    def random(self):
        return self.roll

    def randint(self, low, high):
        return self.damage


def test_missing_required_item_is_rejected():
    s = GameState()
    intent = Intent(description="Fill up a bottle", requires=["bottle"])
    result = resolve(s, intent, FixedRNG(0.99, 0))
    assert result["ok"] is False
    assert s.turn == 0

def test_unknown_risk_level_is_rejected():
    s = GameState()
    intent = Intent(description="walk", risk="super")
    result = resolve(s, intent, FixedRNG(0.99,0))
    assert result["ok"] is False

def test_actions_consumes_and_produces():
    s = GameState(inventory=["stick"], item_sizes={"stick": 1})
    intent= Intent(
        description =" Sharpen the stick",
        consumes = ["stick"],
        produces= ["Sharp stick"],
        new_item_sizes={"Sharp stick": "small"},
    )

    result= resolve(s, intent, FixedRNG(0.99,0))
    assert result["outcome"] == "success"
    assert s.inventory == ["Sharp stick"]

def test_failed_roll_hurts_and_adds_injury():
    s = GameState()
    intent = Intent(
        description= "Climb Cliff",
        risk = "high",
        harm = "major",
        injury = "broken leg",
    )
    result = resolve(s, intent, FixedRNG(0,30))
    assert result["outcome"] == "failure"
    assert s.health ==  70
    assert "broken leg" in s.injuries

def test_lethal_damage_can_kill_at_any_health():
    s = GameState(health = 80)
    intent = Intent(
        description = "fought a bear",
        risk = "high",
        harm="lethal",
        injury = "blood loss",

    )
    result = resolve(s, intent, FixedRNG(0,80))
    assert s.phase == Phase.DEAD

def test_same_action_gives_same_outcome():
    intent = Intent(
        description = "slipped on mud",
        risk = "low",
        harm = "minor",
        injury= "minor back pain",
    )

    a, b = GameState(), GameState()
    resolve(a, intent, random.Random(7))
    resolve(b, intent, random.Random(7))
    assert a.to_dict() == b.to_dict()

def test_damage_stays_in_severity_range():
    intent= Intent(
        description="slip",
        risk="high",
        harm="minor",
        injury = "bruise",
    )

    for seed in range(200):
        s = GameState()
        result = resolve(s, intent, random.Random(seed))
        if result["outcome"] == "failure":
            assert 90<= s.health <= 99
