from dataclasses import dataclass, field
from survival.engine.balance import RISK_FAIL_CHANCE, INJURY_SEVERITY

@dataclass
class Intent:
    description: str
    requires: list[str] = field(default_factory=list)
    consumes: list[str] = field(default_factory=list)
    produces: list[str] = field(default_factory=list)
    new_item_sizes : dict[str, str] = field(default_factory=dict)
    risk: str ="none"
    harm: str = "minor"
    injury: str=""

def resolve(state, intent, rng):
    rejected = []
    for item in intent.requires:
        if item not in state.inventory:
            rejected.append(f"missing required item '{item}'")
    if intent.risk not in RISK_FAIL_CHANCE:
        rejected.append(f"unknown risk level'{intent.risk}'")
    if intent.harm not in INJURY_SEVERITY:
        rejected.append(f"unknown harm tier'{intent.harm}'")
    if rejected:
        return {"ok": False, "turn": state.turn, "rejected":rejected, "outcome": "rejected"}

    failed = rng.random() < RISK_FAIL_CHANCE[intent.risk]

    if failed:
        low, high = INJURY_SEVERITY[intent.harm]
        damage = rng.randint(low, high)
        injuries = [intent.injury] if intent.injury else []
        result = state.apply(health_delta=-damage, add_injuries= injuries)
    else:
        result = state.apply(
            remove_items= intent.consumes,
            add_items= intent.produces,
            new_item_sizes= intent.new_item_sizes,
        )

    if not result["ok"]:
        result["outcome"] = "rejected"
    else:
        result["outcome"] = "failure" if failed else "success"
    return result