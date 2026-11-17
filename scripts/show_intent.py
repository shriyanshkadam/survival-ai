from dotenv import load_dotenv
from survival.engine.game import Game
from survival.llm.factory import build_llm
from survival.pipeline.action_parser import parse_action

load_dotenv()
game = Game(7)
llm = build_llm()
text = "jump across the thin ice"
intent, error = parse_action(llm, text, game.state)
print("error:", error)
print(intent)