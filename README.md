# Survival AI
An LLM-based survival simulator, where the AI generates a scenario and narrates the consequences of your choices, while a backend tracks health, sanity, inventory and injuries to keep everything realistic.

**STATUS** in development (started on 09/oct/2026, rebuild of an earlier prototype.)


## Idea 
In this game, the user is given a survival situation, the main goal of the user is to escape that situation without dying
To mitigate context window decay and long-term retention limits inherent in AI models, state management is handled directly by the backend engine rather than the AI. The backend operates as a deterministic state machine, holding ground-truth values to ensure consistency and prevent state drift across long sessions.



## Playtesting Objectives:
1) Adversarial Security: Attempt prompt injection and jailbreak techniques to test guardrail limits.

2) Output Redundancy: Monitor for repetitive phrasing, recycled scenarios, or response loops.

3) Context Alignment: Verify that AI outputs strictly adhere to the constraints of the current scenario.

4) Feedback Integrity: Validate the accuracy and correctness of end-of-session feedback.

5) Softlock Prevention: Test edge cases to ensure scenario progression remains possible and softlocks are avoided.

## Run it
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m pytest
```

## Earlier prototype
v0 (single-file prototype, Llama-3 + LoRA + RAG): [Will Add later]

## Design decisions
See [DECISIONS.md](DECISIONS.md).