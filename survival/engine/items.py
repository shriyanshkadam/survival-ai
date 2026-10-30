import re

from survival.engine.balance import INGEST_ALIASES, INGEST_PROFILES


def _has(word, name):
    return re.search(rf"\b{re.escape(word)}s?\b", name) is not None


def match_key(name):
    name = name.strip().lower()
    for key in INGEST_PROFILES:
        if _has(key, name):
            return key
    for word, key in INGEST_ALIASES.items():
        if _has(word, name):
            return key
    return None