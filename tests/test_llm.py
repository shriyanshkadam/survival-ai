import pytest
from survival.llm.mock import MockLLM

def test_returns_scripted_responce_in_order():
    llm = MockLLM(["first", "second"])
    assert llm.generate([{"role": "user", "content": "hi"}]) == "first"
    assert llm.generate([{"role": "user", "content": "again"}]) == "second"


def test_records_what_it_was_asked():
    llm = MockLLM(["ok"])
    llm.generate([{"role": "user", "content": "hi"}], temperature=0.2)
    assert llm.calls[0]["temperature"] == 0.2
    assert llm.calls[0]["messages"][0]["content"] == "hi"

def test_running_out_of_responses_is_an_error():
    llm = MockLLM([])
    with pytest.raises(RuntimeError):
        llm.generate([{"role": "user", "content": "hi"}])