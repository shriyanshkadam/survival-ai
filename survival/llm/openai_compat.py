import requests
from survival.llm.base import LLM, LLMUnavailable

class OpenAICompatLLM(LLM):
    def __init__(self, name, base_url, api_key, model, extra=None, token_padding=0, timeout=20):
        if not api_key:
            raise ValueError(f"{name}: API key is not set")
        self.name=  name
        self.url= base_url.rstrip("/") + "/chat/completions"
        self.api_key= api_key
        self.model= model
        self.extra= extra or {}
        self.token_padding= token_padding
        self.timeout= timeout

    def generate(self, messages, temperature=0.7, max_tokens=400):
        payload= {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens + self.token_padding,
            **self.extra,
        }

        try:
            response= requests.post(
                self.url,
                headers= {"Authorization": f"Bearer {self.api_key}"},
                json= payload,
                timeout=self.timeout,
            )

        except requests.RequestException as e:
            raise LLMUnavailable(f"{self.name}: network error: {e}")
        if response.status_code == 429 or response.status_code >= 500:
            raise LLMUnavailable(f"{self.name}: provider busy ({response.status_code})")
        if response.status_code != 200:
            raise RuntimeError(f"{self.name} error {response.status_code}: {response.text[:200]}")
        try:
            return response.json()["choices"][0]["message"]["content"] or ""
        except (KeyError, IndexError, ValueError):
            raise LLMUnavailable(f"{self.name}: unreadable reply")