HAND_CAPACITY  = 2
MIN_START_HEALTH = 30
START_SANITY = (55,95)
MAX_START_INJURIES = 4
START_INJURY_WEIGHTS =  {"minor": 5, "moderate": 3, "major": 1}

CARRY_CAPACITY = {
    "big bag": (8,12),
    "small bag": (4,8),
    "pouch": (1,4),
    "pocket": (1,3),
}

INJURY_SEVERITY = {
    "minor": (1,10),
    "moderate": (11,20),
    "major": (21,40),
    "critical": (41,99),
    "lethal": (100,100),
}

SIZE_CLASSES = {
    "tiny": 0.5,
    "small": 1,
    "medium": 3,
    "large": 5,
    "huge": 7,
}

RISK_FAIL_CHANCE = {
    "none": 0.0,
    "low": 0.1,
    "medium": 0.3,
    "high": 0.6,
}