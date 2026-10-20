class LLMUnavailable(Exception):
    """Provider is busy or unreachable. Safe to retry later."""

class LLM:
    def generate(self, messages, temperature = 0.7, max_tokens=400):
        raise NotImplementedError("subclasses must implement generate")
        