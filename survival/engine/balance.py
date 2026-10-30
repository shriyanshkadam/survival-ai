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

# an item whose name contains the word cuts warmth loss by that fraction
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

