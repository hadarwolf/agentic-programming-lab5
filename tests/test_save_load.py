import json
from pathlib import Path
from typing import Any

import pytest

from session import Session

CAPTURE_GAME = [("e2", "e4"), ("d7", "d5"), ("e4", "d5"), ("d8", "d5")]


def make_session(tmp_path: Path, opponent: str = "human") -> Session:
    session = Session(opponent)
    session.save_path = str(tmp_path / "game.save.json")
    return session


def play_all(session: Session, moves: list[tuple[str, str]]) -> None:
    for source, target in moves:
        session.dispatch({"action": "move", "source": source, "target": target})


def test_round_trip_into_fresh_session(tmp_path: Path) -> None:
    original = make_session(tmp_path)
    play_all(original, CAPTURE_GAME)
    assert any("x" in label for label in original.notation)
    original.save(original.save_path)

    restored = Session()
    restored.load(original.save_path)

    assert restored.view() == original.view()
    assert restored.position == original.position
    assert restored.notation == original.notation
    assert restored.opponent == original.opponent
    assert restored.moves == original.moves


def test_opponent_mode_is_restored(tmp_path: Path) -> None:
    original = make_session(tmp_path, "computer")
    play_all(original, [("e2", "e4")])
    original.dispatch({"action": "computer-move"})
    original.save(original.save_path)

    restored = Session()
    restored.load(original.save_path)

    assert restored.opponent == "computer"
    assert restored.moves == original.moves
    assert restored.view() == original.view()


def test_promotion_setup_round_trip(tmp_path: Path) -> None:
    original = make_session(tmp_path)
    original.dispatch({"action": "promotion-setup"})
    original.save(original.save_path)

    restored = Session("computer")
    restored.load(original.save_path)

    assert restored.view() == original.view()
    assert restored.opponent == "human"


def test_empty_game_round_trip(tmp_path: Path) -> None:
    original = make_session(tmp_path)
    original.save(original.save_path)

    restored = Session()
    play_all(restored, [("e2", "e4")])
    restored.load(original.save_path)

    assert restored.view() == Session().view()
    assert restored.moves == []


def test_save_and_load_through_dispatch(tmp_path: Path) -> None:
    session = make_session(tmp_path)
    play_all(session, CAPTURE_GAME)
    saved_view = session.dispatch({"action": "save"})
    assert saved_view == session.view()

    session.dispatch({"action": "new", "opponent": "computer"})
    loaded_view = session.dispatch({"action": "load"})

    assert loaded_view["board"] == saved_view["board"]
    assert loaded_view == saved_view
    assert session.save_path == str(tmp_path / "game.save.json")


def test_loaded_game_continues(tmp_path: Path) -> None:
    original = make_session(tmp_path)
    play_all(original, CAPTURE_GAME)
    original.save(original.save_path)

    restored = Session()
    restored.load(original.save_path)
    play_all(restored, [("b1", "c3")])

    assert restored.moves == CAPTURE_GAME + [("b1", "c3")]


def test_loaded_checkmate_is_over(tmp_path: Path) -> None:
    original = make_session(tmp_path)
    play_all(original, [("f2", "f3"), ("e7", "e5"), ("g2", "g4"), ("d8", "h4")])
    original.save(original.save_path)

    restored = Session()
    restored.load(original.save_path)

    assert restored.view()["status"] == "checkmate"
    assert restored.view()["winner"] == "Black"


def write(tmp_path: Path, content: Any) -> str:
    path = tmp_path / "bad.save.json"
    path.write_text(content if isinstance(content, str) else json.dumps(content))
    return str(path)


GOOD: dict[str, Any] = {
    "version": 1,
    "opponent": "human",
    "moves": [["e2", "e4"]],
    "redo": [],
}


@pytest.mark.parametrize(
    "content",
    [
        "not json {",
        json.dumps([1, 2, 3]),
        {**GOOD, "version": 2},
        {**GOOD, "version": True},
        {key: value for key, value in GOOD.items() if key != "version"},
        {**GOOD, "opponent": "robot"},
        {**GOOD, "moves": "e2e4"},
        {**GOOD, "moves": [["e2", 4]]},
        {**GOOD, "moves": [[]]},
        {**GOOD, "moves": [["e2", "e5"]]},
        {**GOOD, "moves": [["e2", "e4"], ["e7", "e5"], ["z9", "a1"]]},
        {**GOOD, "moves": [["e2"]]},
    ],
)
def test_bad_input_leaves_session_unchanged(tmp_path: Path, content: Any) -> None:
    session = make_session(tmp_path, "computer")
    play_all(session, [("d2", "d4")])
    session.dispatch({"action": "computer-move"})
    before = session.view()
    moves_before = list(session.moves)

    with pytest.raises(ValueError):
        session.load(write(tmp_path, content))

    assert session.view() == before
    assert session.moves == moves_before
    assert session.opponent == "computer"


def test_missing_file_leaves_session_unchanged(tmp_path: Path) -> None:
    session = make_session(tmp_path)
    play_all(session, [("e2", "e4")])
    before = session.view()

    with pytest.raises(ValueError, match="Could not read save file"):
        session.dispatch({"action": "load"})

    assert session.view() == before


def test_illegal_move_message_names_the_move(tmp_path: Path) -> None:
    session = Session()
    bad = {**GOOD, "moves": [["e2", "e4"], ["e7", "e4"]]}
    with pytest.raises(ValueError, match=r"move 2 \(e7-e4\)"):
        session.load(write(tmp_path, bad))


def test_file_is_plain_json(tmp_path: Path) -> None:
    session = make_session(tmp_path, "computer")
    play_all(session, [("e2", "e4")])
    session.dispatch({"action": "save"})

    with open(session.save_path, encoding="utf-8") as file:
        data = json.load(file)

    assert data == {
        "version": 1,
        "opponent": "computer",
        "moves": [["e2", "e4"]],
        "redo": [],
    }
