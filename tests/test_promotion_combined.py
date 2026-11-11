"""Promotion working with move history, undo, save/load and the captured-pieces sidebar."""

import json
from pathlib import Path

from captured import missing_pieces
from game import new_position
from session import Session


def promoted_session(tmp_path: Path) -> Session:
    """Promotion setup, then White plays b7xa8=N and Black plays g2xh1=R."""
    session = Session()
    session.save_path = str(tmp_path / "game.save.json")
    session.dispatch({"action": "promotion-setup"})
    session.dispatch(
        {"action": "move", "source": "b7", "target": "a8", "promotion": "N"}
    )
    session.dispatch(
        {"action": "move", "source": "g2", "target": "h1", "promotion": "R"}
    )
    return session


def test_history_records_the_promotion_choice(tmp_path: Path) -> None:
    session = promoted_session(tmp_path)
    assert session.moves[-2:] == [("b7", "a8", "N"), ("g2", "h1", "R")]
    assert session.notation[-2:] == ["b7xa8=N", "g2xh1=R"]


def test_promotion_choice_survives_save_and_load(tmp_path: Path) -> None:
    original = promoted_session(tmp_path)
    original.dispatch({"action": "save"})
    with open(original.save_path, encoding="utf-8") as file:
        assert json.load(file)["moves"][-1] == ["g2", "h1", "R"]

    restored = Session()
    restored.load(original.save_path)

    assert restored.view() == original.view()
    assert restored.position[0]["a8"] == "wN"
    assert restored.position[0]["h1"] == "bR"
    assert restored.moves == original.moves


def test_undo_keeps_earlier_promotion_and_removes_later_one(tmp_path: Path) -> None:
    session = promoted_session(tmp_path)
    session.dispatch({"action": "undo"})
    assert session.position[0]["a8"] == "wN"
    assert session.position[0]["g2"] == "bP"
    session.dispatch({"action": "undo"})
    assert session.position[0]["b7"] == "wP"
    assert session.position[0]["a8"] == "bR"


def test_promoted_pawn_is_not_shown_as_captured(tmp_path: Path) -> None:
    session = Session()
    session.dispatch({"action": "promotion-setup"})
    before = session.view()["captured"]
    assert before == ["bP", "wP"]
    session.dispatch(
        {"action": "move", "source": "b7", "target": "a8", "promotion": "Q"}
    )
    assert session.view()["captured"] == ["bP", "bR", "wP"]
    session.dispatch(
        {"action": "move", "source": "g2", "target": "h1", "promotion": "Q"}
    )
    assert session.view()["captured"] == ["bP", "bR", "wP", "wR"]


def test_captured_queen_still_shown_after_promoting_to_a_queen() -> None:
    # White's original queen was captured, then the a-pawn took the a8 rook and became
    # a queen: the board has one white queen, as at the start, but two pieces were lost.
    board = new_position()[0]
    del board["d1"], board["a2"]
    board["a8"] = "wQ"
    assert missing_pieces([board, "b"], ["wQ"]) == ["bR", "wQ"]


def test_computer_promotion_is_replayable() -> None:
    session = Session("computer")
    session.dispatch({"action": "promotion-setup"})
    # promotion-setup starts a two-player game; switch to the computer for Black's reply.
    session.opponent = "computer"
    session.dispatch(
        {"action": "move", "source": "b7", "target": "a8", "promotion": "Q"}
    )
    session.dispatch({"action": "computer-move"})
    rebuilt = Session("computer")
    rebuilt._rebuild(session.moves)
    assert rebuilt.view() == session.view()
