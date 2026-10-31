import random

from survival.engine.balance import INJURY_BUDGET, INJURY_HOOKS
from survival.engine.injuries import (
    action_modifiers, can_treat, drain_modifiers, make_info, validate_effects,
)
from survival.engine.needs import upkeep
from survival.engine.rules import Intent, resolve
from survival.engine.state import GameState


def with_injury(name, tier):
    return GameState(injuries=[name], injury_info={name: make_info(name, tier, 0)})


def total_strength(effects):
    total = 0
    for e in effects:
        low, high = INJURY_HOOKS[e["hook"]]
        total += (e["value"] - low) / (high - low)
    return total


def test_unknown_hooks_dropped_and_values_clipped():
    eff = validate_effects(
        [{"hook": "teleport", "value": 5}, {"hook": "fail_bonus", "value": 9}], "major")
    assert [e["hook"] for e in eff] == ["fail_bonus"]
    assert eff[0]["value"] <= 0.3


def test_minor_injury_cannot_be_overpowered():
    eff = validate_effects(
        [{"hook": "health_per_hour", "value": 8}, {"hook": "fail_bonus", "value": 0.3}], "minor")
    assert total_strength(eff) <= INJURY_BUDGET["minor"] + 0.01


def test_garbage_effects_are_ignored():
    assert validate_effects("not a list", "minor") == []
    assert validate_effects([{"hook": "fail_bonus", "value": "abc"}, 5, None], "minor") == []


def test_known_injury_ignores_llm_proposal():
    info = make_info("deep thigh cut", "minor", 0, proposed=[{"hook": "fail_bonus", "value": 0.3}])
    assert info["tier"] == "moderate"
    assert any(e["hook"] == "health_per_hour" for e in info["effects"])


def test_unknown_injury_gets_default_by_tier():
    info = make_info("sea urchin sting", "major", 0)
    assert any(e["hook"] == "health_per_hour" for e in info["effects"])


def test_unknown_injury_uses_valid_proposal():
    info = make_info("jellyfish sting", "minor", 0,
                     proposed=[{"hook": "sanity_per_hour", "value": 0.5}])
    assert info["effects"][0]["hook"] == "sanity_per_hour"


def test_bleeding_drains_health_over_time():
    s = with_injury("deep thigh cut", "moderate")
    assert upkeep(s, None, 120)["health"] == -6
    resolve(s, Intent(description="wait", minutes=120), random.Random(1))
    assert s.health < 100


def test_treatment_stops_bleeding():
    s = GameState(inventory=["space blanket"], item_sizes={"space blanket": 3},
                  injuries=["deep thigh cut"],
                  injury_info={"deep thigh cut": make_info("deep thigh cut", "moderate", 0)})
    intent = Intent(description="bandage the cut", requires=["space blanket"],
                    treats="deep thigh cut", treatment="bandage")
    r = resolve(s, intent, random.Random(1))
    assert r["ok"]
    assert s.injury_info["deep thigh cut"]["phase"] == "stabilized"
    assert drain_modifiers(s)["health_per_hour"] == 0
    assert action_modifiers(s, [])["minutes_mult"] > 1.0


def test_wrong_treatment_is_rejected():
    s = with_injury("deep thigh cut", "moderate")
    intent = Intent(description="splint it", treats="deep thigh cut", treatment="splint")
    assert resolve(s, intent, random.Random(1))["outcome"] == "rejected"
    assert can_treat(s, "deep thigh cut", "bandage")


def test_cannot_treat_an_injury_you_do_not_have():
    intent = Intent(description="bandage", treats="broken arm", treatment="bandage")
    assert resolve(GameState(), intent, random.Random(1))["outcome"] == "rejected"


def test_fail_bonus_only_for_matching_tags():
    s = with_injury("twisted ankle", "moderate")
    assert action_modifiers(s, ["travel"])["fail_bonus"] > 0
    assert action_modifiers(s, ["fire"])["fail_bonus"] == 0


def test_injury_stabilizes_with_time():
    s = with_injury("bruised ribs", "minor")
    s.apply(minutes=13 * 60)
    assert s.injury_info["bruised ribs"]["phase"] == "stabilized"


def test_failed_action_creates_injury_with_profile():
    intent = Intent(description="jump off a rock", risk="certain", harm="moderate",
                    injury="twisted ankle")
    s = GameState()
    r = resolve(s, intent, random.Random(1))
    assert r["outcome"] == "failure"
    assert "twisted ankle" in s.injuries
    assert s.injury_info["twisted ankle"]["phase"] == "acute"


def test_injury_info_survives_save_and_load():
    s = with_injury("concussion", "major")
    assert GameState.from_dict(s.to_dict()).injury_info == s.injury_info