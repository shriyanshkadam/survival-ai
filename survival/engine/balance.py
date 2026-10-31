HAND_CAPACITY  = 2
MIN_START_HEALTH = 30
START_SANITY = (55,95)
MAX_START_INJURIES = 4
START_INJURY_WEIGHTS =  {"minor": 5, "moderate": 3, "major": 1}
DEFAULT_MINUTES = 30
MIN_MINUTES = 5
MAX_MINUTES = 480

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
    "certain": 1.0,
}

START_NEEDS= (70, 100)
FOOD_DRAIN = 3
WATER_DRAIN= 5

WARMTH_DRAIN = {
    "dense forest":      {"dawn": 3, "day": 1, "dusk": 3, "night": 5},
    "desert highway":    {"dawn": 2, "day": 0, "dusk": 1, "night": 4},
    "mountain ridge":    {"dawn": 6, "day": 3, "dusk": 6, "night": 10},
    "snowy valley":      {"dawn": 8, "day": 5, "dusk": 8, "night": 12},
    "frozen lake shore": {"dawn": 8, "day": 5, "dusk": 8, "night": 12},
    "remote island":     {"dawn": 2, "day": 0, "dusk": 2, "night": 4},
}

HEAT_THIRST_MULT = {
    "desert highway": {"dawn": 1.2, "day": 2.0, "dusk": 1.5, "night": 1.0},
    "remote island": {"day": 1.5},
}
COLD_THRESHOLD = 6
COLD_FOOD_MULT = 1.5

WARMTH_PROTECTION = {"blanket": 0.4, "tent": 0.5, "jacket": 0.3, "coat": 0.3}

STARVATION_HEALTH_PER_HOUR = {"food": 2, "water": 5, "warmth": 8}

RESTORABLE_NEEDS = ("food", "water")
RESTORE_AMOUNTS = {"small": 10, "medium": 25, "large": 45}

INGEST_PROFILES = {
    "energy bar": {"food": 25},
    "water": {"water": 35},
    "snow": {"water": 8, "warmth": -15},
    "ice": {"water": 8, "warmth": -12},
    "berries": {"food": 8, "water": 3},
    "grubs": {"food": 8},
    "fish": {"food": 20},
    "leaves": {"food": 3},
    "bark": {"food": 2, "sanity": -2},
    "mushroom": {"food": 8, "health": -8},
    "seawater": {"water": -10, "health": -5},
    "dirt": {"sanity": -4},
    "rock": {"sanity": -5, "injury": ("broken tooth", "minor")},
}
INGEST_ALIASES = {
    "insect": "grubs", "bug": "grubs", "larva": "grubs", "larvae": "grubs",
    "worm": "grubs", "beetle": "grubs", "ant": "grubs", "cricket": "grubs",
    "grasshopper": "grubs", "berry": "berries", "fruit": "berries",
}

FINDABLE = {
    "dense forest": ("berries", "grubs", "water", "fish", "leaves", "mushroom", "bark"),
    "desert highway": (),
    "mountain ridge": ("snow", "ice", "grubs"),
    "snowy valley": ("snow", "ice"),
    "frozen lake shore": ("snow", "ice", "fish", "water"),
    "remote island": ("berries", "fish", "water", "seawater", "grubs", "leaves"),
}

FORAGE_MISS_CHANCE = 0.4
ALWAYS_AVAILABLE = ("rock", "dirt")

INJURY_HOOKS = {
    "health_per_hour": (0.0, 8.0),
    "sanity_per_hour": (0.0, 3.0),
    "forage_miss": (0.0, 0.3),
    "fail_bonus": (0.0, 0.3),
    "action_minutes_mult": (1.0, 2.0),
    "food_drain_mult": (1.0, 2.0),
    "water_drain_mult": (1.0, 2.0),
    "warmth_drain_mult": (1.0, 2.0),
}

INJURY_BUDGET = {"minor": 0.4, "moderate": 1.0, "major": 2.0, "critical": 3.0}
MAX_INJURY_EFFECTS = 4

INJURY_TAGS = ("climb", "travel", "hands", "forage", "fire", "craft", "fight")
INJURY_TREATMENTS = ("bandage", "splint", "pressure", "clean", "rest", "warm", "cool")

DEFAULT_STABILIZE_HOURS = {"minor": 12, "moderate": 36, "major": 72, "critical": 96}

DEFAULT_INJURY_EFFECTS = {
    "minor": [{"hook": "fail_bonus", "value": 0.03}],
    "moderate": [
        {"hook": "fail_bonus", "value": 0.08},
        {"hook": "action_minutes_mult", "value": 1.15},
    ],
    "major": [
        {"hook": "health_per_hour", "value": 2},
        {"hook": "fail_bonus", "value": 0.15},
        {"hook": "action_minutes_mult", "value": 1.3},
    ],
    "critical": [
        {"hook": "health_per_hour", "value": 5},
        {"hook": "fail_bonus", "value": 0.25},
        {"hook": "action_minutes_mult", "value": 1.5},
    ],
}

KNOWN_INJURIES = {
    "bruised ribs": {
        "tier": "minor",
        "effects": [
            {"hook": "fail_bonus", "value": 0.05},
            {"hook": "action_minutes_mult", "value": 1.1},
        ],
        "stabilize": {"by": ["rest"], "hours": 12},
    },
    "sprained wrist": {
        "tier": "minor",
        "effects": [{"hook": "fail_bonus", "value": 0.08, "tags": ["hands", "craft"]}],
        "stabilize": {"by": ["splint", "bandage", "rest"], "hours": 24},
    },
    "scratched forearms": {
        "tier": "minor",
        "effects": [
            {"hook": "health_per_hour", "value": 0.5},
            {"hook": "fail_bonus", "value": 0.03, "tags": ["hands"]},
        ],
        "stabilize": {"by": ["clean", "bandage"], "hours": 12},
    },
    "deep thigh cut": {
        "tier": "moderate",
        "effects": [
            {"hook": "health_per_hour", "value": 3},
            {"hook": "action_minutes_mult", "value": 1.2},
            {"hook": "fail_bonus", "value": 0.05, "tags": ["travel", "climb"]},
        ],
        "stabilize": {"by": ["bandage", "pressure"], "hours": 48},
    },
    "twisted ankle": {
        "tier": "moderate",
        "effects": [
            {"hook": "action_minutes_mult", "value": 1.3},
            {"hook": "fail_bonus", "value": 0.12, "tags": ["travel", "climb"]},
            {"hook": "forage_miss", "value": 0.08},
        ],
        "stabilize": {"by": ["splint", "bandage", "rest"], "hours": 36},
    },
    "broken forearm": {
        "tier": "major",
        "effects": [
            {"hook": "health_per_hour", "value": 2},
            {"hook": "fail_bonus", "value": 0.2, "tags": ["hands", "climb", "craft"]},
            {"hook": "sanity_per_hour", "value": 0.5},
        ],
        "stabilize": {"by": ["splint"], "hours": 72},
    },
    "concussion": {
        "tier": "major",
        "effects": [
            {"hook": "fail_bonus", "value": 0.2},
            {"hook": "action_minutes_mult", "value": 1.3},
            {"hook": "sanity_per_hour", "value": 1},
        ],
        "stabilize": {"by": ["rest"], "hours": 24},
    },
}

MAX_TOTAL_BLEED = 12.0
MAX_DRAIN_MULT = 3.0
MAX_ACTION_FAIL_BONUS = 0.5
MAX_ACTION_FORAGE_MISS = 0.5
MAX_ACTION_MINUTES_MULT = 2.5