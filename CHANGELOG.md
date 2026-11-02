# Update log

## v0.0.0
First playable version with:
- Engine: holds the game rules, validates every change and generates the numbers that the LLM uses to narrate the scenario
- Clock: Logs the time, Crucial for website sky gradient interface and future update
- LLM system: To prevent LLM free limits, multiple fallback LLMs are put in place to create a loop for a smooth scenario flow, all LLMs run on a OpenAI compatible format
- Needs: For realistic difficulty, health, sanity, food, water, warmth are added
- Injuries: For debuffs and punishment for mistakes and a baseline caution
- Inventory: It stores items, It has limited storage based on the character preset
- Items: useful objects that take up inventory space based on their size
- Eating and drinking: consuming items changes your needs
- Scenario: rolls a scenario based on current 3 scenario presets, it contains multiple scenario blocks for scenarios, containing starting injuries, items in inventory and inventory space
- Balance list: it contains every single list based on which engine gives numbers
- Website: a story log, a HUD for your vitals and a clock-based sky gradient
- MockLLM: A deterministic LLM for replicable tests for bugtesting.
- Tests: contains tests for the engine, parser, narrator and fallback chain. Runs on pytest
