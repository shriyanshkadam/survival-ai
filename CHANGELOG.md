# Update log

## v0.0.1
**DEBUGGING FEATURE:**
- Session transcript logging: A tool for debugging that creates a transcript file in the `data\logs` folder (off by default).
- Added `/api/version`, which shows the running version

**GUI FEATURES:**
- Better text visibility: Increased font size and font boldness.
- Overhauled skies: split day time into two morning and afternooon(NOTE: This change is visual only). Also added new sky backgrounds and background elements for each sky.


## v0.0.0
**First playable version with:**
- Engine: holds the game rules, validates every change and generates the numbers that the LLM uses to narrate the scenario
- Clock: Logs the time, Crucial for website sky gradient interface and future update
- LLM system: To prevent LLM free limits, multiple fallback LLMs are put in place to create a loop for a smooth scenario flow, all LLMs run on an OpenAI compatible format
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


