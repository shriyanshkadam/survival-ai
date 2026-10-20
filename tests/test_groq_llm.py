import pytest

from survival.llm import groq_llm
from survival.llm.base import LLMUnavailable


class FakeResponse:
    def __init__(self, status_code, data=None):
        self.status_code = status_code
        self._data = data or {}
        self.text = str(data)

    def json(self):
        return self._data


def make(monkeypatch, response):
    monkeypatch.setattr(groq_llm.requests, "post", lambda *a, **k: response)
    return groq_llm.GroqLLM(api_key="test-key")


MSG = [{"role": "user", "content": "hi"}]


def test_returns_message_text(monkeypatch):
    ok = FakeResponse(200, {"choices": [{"message": {"content": "hello"}}]})
    assert make(monkeypatch, ok).generate(MSG) == "hello"


def test_rate_limit_becomes_unavailable(monkeypatch):
    with pytest.raises(LLMUnavailable):
        make(monkeypatch, FakeResponse(429)).generate(MSG)


def test_bad_key_is_a_real_error(monkeypatch):
    with pytest.raises(RuntimeError):
        make(monkeypatch, FakeResponse(401)).generate(MSG)


def test_missing_key_is_rejected(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    with pytest.raises(ValueError):
        groq_llm.GroqLLM()