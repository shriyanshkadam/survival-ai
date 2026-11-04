import json

from survival.engine.game import Game
from survival.llm.base import LLM, LLMUnavailable
from survival.llm.mock import MockLLM
from survival.pipeline.session_log import SessionLogger
from survival.pipeline.turn import play_text


class Down(LLM):
    def generate(self, messages, temperature=0.7, max_tokens=400):
        raise LLMUnavailable("down")


def read(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_logger_off_writes_nothing(tmp_path):
    logger = SessionLogger("abc", Game(seed=1), enabled=False, directory=tmp_path)
    logger.write({"kind": "x"})
    assert list(tmp_path.iterdir()) == []


def test_header_and_turn_are_logged(tmp_path):
    game = Game(seed=1)
    logger = SessionLogger("abc", game, enabled=True, directory=tmp_path)
    llm = MockLLM([json.dumps({"description": "rest"}), "You catch your breath."])
    play_text(game, llm, "rest", logger)
    lines = read(logger.path)
    assert lines[0]["kind"] == "header"
    assert lines[0]["seed"] == 1
    assert lines[1]["kind"] == "turn"
    assert lines[1]["input"] == "rest"
    assert lines[1]["narrative"] == "You catch your breath."


def test_parse_failure_is_logged(tmp_path):
    game = Game(seed=1)
    logger = SessionLogger("abc", game, enabled=True, directory=tmp_path)
    play_text(game, MockLLM(["nonsense", "nonsense"]), "asdf", logger)
    assert read(logger.path)[1]["kind"] == "parse_failed"


def test_outage_is_logged(tmp_path):
    game = Game(seed=1)
    logger = SessionLogger("abc", game, enabled=True, directory=tmp_path)
    play_text(game, Down(), "rest", logger)
    assert read(logger.path)[1]["kind"] == "llm_unavailable"


def test_unwritable_folder_does_not_crash(tmp_path):
    blocker = tmp_path / "blocked"
    blocker.write_text("x")
    logger = SessionLogger("abc", Game(seed=1), enabled=True, directory=blocker)
    logger.write({"kind": "x"})
    assert logger.enabled is False