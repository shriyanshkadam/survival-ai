Decision 1: Rejected actions do not cost a turn, because anyone can make innocent mistakes and they should not be punished for them.

Decision 2: Repeated attempts to jailbreak will be caught by a detector looking for active security bypasses, whereas repeated innocent mistakes will only trigger hints on how the interface works (Hints part will be implemented at the final stage of development).

Decision 3: To prevent inconsistencies, base ranges for capacity are given to different types of storage, to be evaluated by the LLM.

Decision 4: To prevent unrealistic damage based on injuries, specific ranges are set for each injury type according to its severity. The LLM evaluates the injury type, and a random amount of damage corresponding to that severity is dealt to the player.

Decision 5: To bypass rate limits for now, multiple fallback LLMs have been added.

Decision 6: To keep track of elapsed in-game time, a clock module has been added, which will be crucial later down the line, this clock is base of a major part of the game.

Decision 7: To make survival mechanics more realistic, three core attributes have been added: food, water, and warmth.

Decision 8 (Major Decision): To keep the LLM dynamic and ready for every situation that varies per session—since it is impossible to hardcode every possible event in a dictionary—another LLM pipeline with a RAG backend will be added. If an event occurs that is not in the existing dictionary, the RAG-backed LLM will fetch factual data, create a cached JSON logging the scenario, pass it through the engine, and let the narrator LLM generate the story. This keeps the project flexible for any scenario within the constraints of the starting scenario, making each playthrough unique (Yet to be implemented).

Decision 9: Make text bolder and larger for better visibility in bright sky times(like day)

Decision 10: Overhaul the GUI for better aesthetics and more visually appealing