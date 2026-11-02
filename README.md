# Survival AI
An LLM-based survival simulator, where the engine rolls a scenario and LLM narrates the scenario, while a backend tracks health, sanity, food, water, warmth, clock, inventory and injuries to keep everything realistic.
The workflow is: LLM proposes and the engine validates and rolls all the numbers.

**STATUS** in development (started on 09/oct/2026, rebuild of an earlier prototype), Currently only runs locally
**CURRENT VERSION** 0.0.0

## Idea 
In this game, the user is given a survival situation, the main goal of the user is to escape that situation without dying
To mitigate context window decay and long-term retention limits inherent in AI models, state management is handled directly by the backend engine rather than the AI. The backend operates as a deterministic state machine, holding ground-truth values to ensure consistency and prevent state drift across long sessions.


## Features
- Please refer to [CHANGELOG.md](CHANGELOG.md) with all the updates and v0.0.0's features.

## Playtesting Objectives(PLANNED):
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
copy .env.example .env
```
Put your own API key in `.env` (never commit it). Then:
```
python -m pytest
python -m uvicorn survival.web.app:app --reload
```
Open http://127.0.0.1:8000


## Earlier prototype
v0 (single-file prototype, Llama-3 + LoRA + RAG): [Will Add later]

## Design decisions
See [DECISIONS.md](DECISIONS.md).


## DEVELOPER NOTE
scenario_data.py currently has few scenario block, will add many more later.
Game will be deployed on hugging face, once the last major update completing the game loop is added.

## TOOLS USED
In this project, I used Claude(Sonnet 5.5) as a pair programmer and a tutor, though I still have full comprehension of the codebase, and all the creative and architectural decisions were made by me. Claude was only used for complex code assistance.