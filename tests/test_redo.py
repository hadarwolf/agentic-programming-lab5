"""Redo, alone and with undo, the computer opponent, promotion, captures and save/load."""

import json
from pathlib import Path

import pytest

from game import new_position
from session import Session

OPENING = [("e2", "e4"), ("d7", "d5"), ("e4", "d5")]  # Ends with a capture.


def play_all(session: Session, moves: list[tuple[str, str]]) -> None:
    for source, target in moves:
        session.dispatch({"action": "move", "source": source, "target": target})


def test_redo_replays_an_undone_move() -> None:
    session = Session()
    play_all(session, OPENING)
    played = session.view()
    session.dispatch({"action": "undo"})
    view = session.dispatch({"action": "redo"})
    assert view == played
    assert session.moves == OPENING


def test_redo_steps_forward_in_order() -> None:
    session = Session()
    play_all(session, OPENING)
    for _ in OPENING:
        session.undo()
    assert session.position == new_position()
    session.redo()
    assert session.moves == OPENING[:1]
    session.redo()
    assert session.moves == OPENING[:2]


def test_redo_with_nothing_undone_does_nothing() -> None:
    session = Session()
    play_all(session, OPENING[:1])
    before = session.view()
    assert before["can_redo"] is False
    assert session.dispatch({"action": "redo"}) == before


def test_new_move_clears_redo() -> None:
    session = Session()
    play_all(session, OPENING)
    session.undo()
    assert session.view()["can_redo"] is True
    play_all(session, [("b1", "c3")])
    assert session.view()["can_redo"] is False
    session.redo()
    assert session.moves == [*OPENING[:2], ("b1", "c3")]


def test_new_game_clears_redo() -> None:
    session = Session()
    play_all(session, OPENING)
    session.undo()
    session.dispatch({"action": "new", "opponent": "computer"})
    assert session.redo_moves == []
    assert session.view()["can_redo"] is False


def test_redo_restores_the_capture_in_the_sidebar() -> None:
    session = Session()
    play_all(session, OPENING)
    assert session.captured == ["bP"]
    session.undo()
    assert session.captured == []
    session.redo()
    assert session.captured == ["bP"]


def test_redo_against_the_computer_replays_the_move_and_the_reply() -> None:
    session = Session("computer")
    play_all(session, [("e2", "e4")])
    session.dispatch({"action": "computer-move"})
    played = list(session.moves)
    session.undo()
    assert session.moves == []
    session.redo()
    assert session.moves == played
    assert session.position.turn == "w"
    assert not session.computer_to_move()


def test_redo_repeats_the_promotion_choice() -> None:
    session = Session()
    session.dispatch({"action": "promotion-setup"})
    session.dispatch({"action": "move", "source": "b7", "target": "a8", "promotion": "N"})
    session.undo()
    session.redo()
    assert session.position.board["a8"] == "wN"
    assert session.moves[-1] == ("b7", "a8", "N")
    assert session.notation[-1] == "b7xa8=N"


def test_redo_history_survives_save_and_load(tmp_path: Path) -> None:
    original = Session("computer")
    original.save_path = str(tmp_path / "game.save.json")
    play_all(original, [("e2", "e4")])
    original.dispatch({"action": "computer-move"})
    played = list(original.moves)
    original.undo()
    original.dispatch({"action": "save"})

    restored = Session()
    restored.load(original.save_path)
    assert restored.view() == original.view()
    restored.redo()
    assert restored.moves == played


def test_redo_is_saved_as_groups_of_moves(tmp_path: Path) -> None:
    session = Session()
    play_all(session, OPENING)
    session.undo()
    session.undo()
    path = str(tmp_path / "game.save.json")
    session.save(path)
    with open(path, encoding="utf-8") as file:
        data = json.load(file)
    assert data["moves"] == [["e2", "e4"]]
    assert data["redo"] == [[["e4", "d5"]], [["d7", "d5"]]]


@pytest.mark.parametrize(
    "redo",
    [
        "e2e4",
        [[]],
        [["e7", "e5"]],
        [[["e7", 5]]],
        [[["e2", "e4"]]],  # Not legal after the saved moves: White already moved.
    ],
)
def test_bad_redo_in_a_save_file_leaves_session_unchanged(tmp_path: Path, redo: object) -> None:
    path = tmp_path / "bad.save.json"
    data = {"version": 1, "opponent": "human", "moves": [["e2", "e4"]], "redo": redo}
    path.write_text(json.dumps(data))
    session = Session()
    play_all(session, OPENING)
    before = session.view()
    with pytest.raises(ValueError, match="Save file redo"):
        session.load(str(path))
    assert session.view() == before
