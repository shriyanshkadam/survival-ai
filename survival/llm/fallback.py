import time
from survival.llm.base import LLM, LLMUnavailable

BASE_COOLDOWN= 60
MAX_COOLDOWN= 900
BROKEN_COOLDOWN= 1800

class FallbackLLM(LLM):
    def __init__(self, providers, clock= time.monotonic):
        self.providers= providers
        self.clock = clock
        self.blocked_until= [0.0] * len(providers)
        self.failures= [0] * len(providers)
        self.last_used= None

    def generate(self, messages, temperature=0.7, max_tokens=400):
        for i, llm in enumerate(self.providers):
            if self.clock() < self.blocked_until[i]:
                continue
            try:
                text= llm.generate(messages, temperature, max_tokens)
            except LLMUnavailable:
                self.failures[i] += 1
                wait = min(BASE_COOLDOWN * 2 ** (self.failures[i] - 1), MAX_COOLDOWN)
                self.blocked_until[i] = self.clock() + wait
                continue
            except RuntimeError:
                self.blocked_until[i] = self.clock() + BROKEN_COOLDOWN
                continue
            self.failures[i] = 0
            self.last_used = getattr(llm, "name", type(llm).__name__)
            return text
        raise LLMUnavailable("all providers are busy")
