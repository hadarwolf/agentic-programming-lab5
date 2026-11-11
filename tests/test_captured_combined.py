"""The captured-pieces sidebar working with undo and save/load."""

from pathlib import Path

from session import Session

TWO_CAPTURES = [("e2", "e4"), ("d7", "d5"), ("e4", "d5"), ("d8", "d5")]


def play_all(session: Session, moves: list[tuple[str, str]]) -> None:
    for source, target in moves:
        session.play(source, target)


def test_undo_removes_a_capture_from_the_sidebar() -> None:
    session = Session()
    play_all(session, TWO_CAPTURES)
    assert session.view()["captured"] == ["bP", "wP"]
    session.dispatch({"action": "undo"})
    assert session.view()["captured"] == ["bP"]
    session.dispatch({"action": "undo"})
    assert session.view()["captured"] == []


def test_undo_against_the_computer_updates_the_sidebar() -> None:
    session = Session("computer")
    play_all(session, TWO_CAPTURES)
    session.dispatch({"action": "undo"})
    assert session.view()["captured"] == []


def test_load_restores_the_sidebar_in_a_fresh_session(tmp_path: Path) -> None:
    session = Session()
    play_all(session, TWO_CAPTURES)
    session.save_path = str(tmp_path / "game.save.json")
    session.dispatch({"action": "save"})
    fresh = Session()
    fresh.save_path = session.save_path
    view = fresh.dispatch({"action": "load"})
    assert view["captured"] == ["bP", "wP"]


def test_new_game_clears_the_sidebar() -> None:
    session = Session()
    play_all(session, TWO_CAPTURES)
    view = session.dispatch({"action": "new"})
    assert view["captured"] == []
