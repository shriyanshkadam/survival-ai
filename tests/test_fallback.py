import pytest

from survival.llm.base import LLM, LLMUnavailable
from survival.llm.fallback import FallbackLLM


class Fake(LLM):
    def __init__(self, name, fail=False):
        self.name = name
        self.fail = fail
        self.calls = 0

    def generate(self, messages, temperature=0.7, max_tokens=400):
        self.calls += 1
        if self.fail:
            raise LLMUnavailable("busy")
        return self.name


def test_uses_first_provider():
    a, b = Fake("a"), Fake("b")
    llm = FallbackLLM([a, b])
    assert llm.generate([]) == "a"
    assert b.calls == 0


def test_falls_back_when_first_is_busy():
    a, b = Fake("a", fail=True), Fake("b")
    llm = FallbackLLM([a, b])
    assert llm.generate([]) == "b"
    assert llm.last_used == "b"


def test_busy_provider_is_skipped_then_returns():
    t = [0.0]
    a, b = Fake("a", fail=True), Fake("b")
    llm = FallbackLLM([a, b], clock=lambda: t[0])
    llm.generate([])
    llm.generate([])
    assert a.calls == 1
    a.fail = False
    t[0] = 61
    assert llm.generate([]) == "a"


def test_all_busy_raises():
    llm = FallbackLLM([Fake("a", fail=True), Fake("b", fail=True)])
    with pytest.raises(LLMUnavailable):
        llm.generate([])