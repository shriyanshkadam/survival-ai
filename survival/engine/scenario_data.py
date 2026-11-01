

CHARACTERS= {
    "lost hiker":{
        "gear": "big bag",
        "items": {"water bottle": "small", "matchbox": "tiny", "survival knife":"medium","space blanket": "medium", "energy bar": "tiny"}
    },
    "stranded roadtripper":{
        "gear": "small bag",
        "items": {"water bottle": "small", "mobile phone": "tiny", "blanket": "medium"}
    },
    "jungle camper":{
        "gear": "big bag",
        "items": {"water bottle": "small", "bear spray": "small", "lighter": "tiny", "portable tent": "large"}
    },
}

SETTINGS= ["dense forest", "desert highway", "mountain ridge", "snowy valley", "frozen lake shore", "remote island"]

CAUSES= ["wandered off-trail", "vehicle breakdown", "sudden storm", "fall during hike", "plane crash"]

START_INJURIES = {
    "minor": ["bruised ribs", "sprained wrist", "scratched forearms"],
    "moderate": ["deep thigh cut", "twisted ankle"],
    "major": ["broken forearm", "concussion"],
}

CAUSE_HOURS_OUT = {
    "wandered off-trail": (2, 10),
    "vehicle breakdown": (1, 6),
    "sudden storm": (1, 5),
    "fall during hike": (2, 8),
    "plane crash": (0, 2),
}

CAUSE_WARMTH_HIT = {"sudden storm": 25, "plane crash": 10, "fall during hike": 5}

CHARACTER_SETTINGS = {
    "lost hiker": ["dense forest", "mountain ridge", "snowy valley", "frozen lake shore"],
    "stranded roadtripper": ["desert highway", "mountain ridge", "snowy valley", "dense forest"],
    "jungle camper": ["dense forest", "remote island"],
}

CHARACTER_CAUSES = {
    "lost hiker": ["wandered off-trail", "sudden storm", "fall during hike"],
    "stranded roadtripper": ["vehicle breakdown", "sudden storm"],
    "jungle camper": ["wandered off-trail", "sudden storm", "fall during hike", "plane crash"],
}