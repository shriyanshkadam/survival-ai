from dotenv import load_dotenv

from survival.engine.game import Game
from survival.llm.groq_llm import GroqLLM
from survival.pipeline.turn import play_text

load_dotenv()
game = Game(seed=1)
llm = GroqLLM()

s = game.scenario
print(f"{s.character} | {s.setting} | {s.cause}")
print(game.state.to_dict())

while True:
    text = input("> ")
    if text.lower() == "quit":
        break
    out = play_text(game, llm, text)
    print(out["narrative"])
    st = game.state
    print(f"health {st.health} | sanity {st.sanity} | {st.injuries} | {st.inventory}")
    if st.phase.value != "playing":
        print("GAME OVER")
        break