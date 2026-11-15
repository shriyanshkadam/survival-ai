import os

import requests
from dotenv import load_dotenv

import survival.llm.factory as f

load_dotenv()
entries = getattr(f, "PROVIDERS", None)
if entries is None:
    entries = [e for role in f.ROLES.values() for e in role]

seen = set()
for name, url, key_var, model, extra, padding in entries:
    if (name, model) in seen:
        continue
    seen.add((name, model))
    key = os.environ.get(key_var)
    if not key:
        print(f"{name}: no key set ({key_var})")
        continue
    try:
        r = requests.post(
            url.rstrip("/") + "/chat/completions",
            headers={"Authorization": "Bearer " + key},
            json={"model": model, "messages": [{"role": "user", "content": "Reply with the word ok."}],
                  "max_tokens": 20 + padding, **extra},
            timeout=60,
        )
    except requests.RequestException as e:
        print(f"{name}: network error {e}")
        continue
    print(f"{name} ({model}): {r.status_code}  {r.text[:160]!r}")
    kept = {k: v for k, v in r.headers.items() if k.lower().startswith(("retry-after", "x-ratelimit"))}
    if kept:
        print("   ", kept)