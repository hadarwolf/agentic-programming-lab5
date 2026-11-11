"""Undo and save/load working together."""

from pathlib import Path

from game import new_position
from session import Session

GAME = [("e2", "e4"), ("d7", "d5"), ("e4", "d5"), ("g8", "f6")]


def play_all(session: Session, moves: list[tuple[str, str]]) -> None:
    for source, target in moves:
        session.play(source, target)


def saved(tmp_path: Path, session: Session) -> Session:
    session.save_path = str(tmp_path / "game.save.json")
    session.dispatch({"action": "save"})
    fresh = Session()
    fresh.save_path = session.save_path
    fresh.dispatch({"action": "load"})
    return fresh


def test_undo_after_load_reaches_moves_made_before_the_save(tmp_path: Path) -> None:
    original = Session()
    play_all(original, GAME)
    loaded = saved(tmp_path, original)
    for _ in GAME:
        loaded.dispatch({"action": "undo"})
    assert loaded.position == new_position()
    assert loaded.notation == []


def test_undo_after_load_restores_a_capture(tmp_path: Path) -> None:
    original = Session()
    play_all(original, GAME[:3])
    loaded = saved(tmp_path, original)
    loaded.dispatch({"action": "undo"})
    assert loaded.position.board["d5"] == "bP"
    assert loaded.notation == ["e2-e4", "d7-d5"]


def test_save_after_undo_stores_the_undone_game(tmp_path: Path) -> None:
    original = Session()
    play_all(original, GAME)
    original.dispatch({"action": "undo"})
    original.dispatch({"action": "undo"})
    loaded = saved(tmp_path, original)
    assert loaded.moves == GAME[:2]
    assert loaded.view() == original.view()


def test_loaded_computer_game_still_undoes_two_moves(tmp_path: Path) -> None:
    original = Session("computer")
    play_all(original, GAME)
    loaded = saved(tmp_path, original)
    assert loaded.opponent == "computer"
    loaded.dispatch({"action": "undo"})
    assert loaded.moves == GAME[:2]
    assert loaded.position.turn == "w"


def test_load_replaces_an_undo_history(tmp_path: Path) -> None:
    first = Session()
    play_all(first, GAME[:1])
    first.save_path = str(tmp_path / "game.save.json")
    first.dispatch({"action": "save"})
    other = Session()
    play_all(other, GAME)
    other.save_path = first.save_path
    other.dispatch({"action": "load"})
    other.dispatch({"action": "undo"})
    other.dispatch({"action": "undo"})
    assert other.position == new_position()
