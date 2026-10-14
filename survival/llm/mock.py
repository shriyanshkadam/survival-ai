from survival.llm.base import  LLM

class MockLLM(LLM):
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def generate(self, messages, temperature=0.7, max_tokens=400):
        self.calls.append({
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        })
        if not self.responses:
            raise RuntimeError("MockLLM ran out of scripted responses")
        return self.responses.pop(0)
        