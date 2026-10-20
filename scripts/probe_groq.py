from dotenv import load_dotenv
from survival.llm.groq_llm import GroqLLM

load_dotenv()
llm = GroqLLM()
reply = llm.generate(
    [{"role": "user", "content": 'Reply with only this JSON: {"a": 1}'}],
    temperature=0.1,
    max_tokens=300,
)
print(repr(reply))