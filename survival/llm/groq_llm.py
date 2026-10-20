import os

import requests

from survival.llm.base import LLM, LLMUnavailable

API_URL = "https://api.groq.com/openai/v1/chat/completions"


class GroqLLM(LLM):
    def __init__(self, api_key=None, model=None, timeout=30):
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        self.model = model or os.environ.get("GROQ_MODEL", "openai/gpt-oss-20b")
        self.timeout = timeout
        if not self.api_key:
            raise ValueError("GROQ_API_KEY is not set")

    def generate(self, messages, temperature=0.7, max_tokens=400):
        try:
            response = requests.post(
                API_URL,
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens + 1000,
                    "reasoning_effort": "low",

                },
                timeout=self.timeout,
            )
        except requests.RequestException as e:
            raise LLMUnavailable(f"network error: {e}")
        if response.status_code == 429 or response.status_code >= 500:
            raise LLMUnavailable(f"provider busy ({response.status_code})")
        if response.status_code != 200:
            raise RuntimeError(f"Groq error {response.status_code}: {response.text[:200]}")
        return response.json()["choices"][0]["message"]["content"]