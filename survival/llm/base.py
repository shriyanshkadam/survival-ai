class LLM:
    def generate(self, messages, temperature = 0.7, max_tokens=400):
        raise NotImplementedError("subclasses must implement generate")
        