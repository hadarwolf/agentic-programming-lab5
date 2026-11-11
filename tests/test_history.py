from session import PROMOTION_SETUP, Session


def test_play_records_replayable_moves() -> None:
    session = Session()
    session.dispatch({"action": "move", "source": "e2", "target": "e4"})
    session.dispatch({"action": "move", "source": "d7", "target": "d5"})
    assert session.moves == [("e2", "e4"), ("d7", "d5")]


def test_new_game_clears_history() -> None:
    session = Session()
    session.dispatch({"action": "move", "source": "e2", "target": "e4"})
    session.dispatch({"action": "new", "opponent": "computer"})
    assert session.moves == []


def test_rebuild_reproduces_the_game() -> None:
    played = Session()
    played.dispatch({"action": "promotion-setup"})
    rebuilt = Session()
    rebuilt._rebuild(played.moves)
    assert rebuilt.view() == played.view()
    assert rebuilt.moves == played.moves


def test_rebuild_accepts_json_lists_and_keeps_opponent() -> None:
    session = Session("computer")
    session._rebuild([list(m) for m in PROMOTION_SETUP[:2]])
    assert session.opponent == "computer"
    assert session.moves == list(PROMOTION_SETUP[:2])
    assert session.notation == ["a2-a4", "h7-h5"]


def test_rebuild_to_empty_is_a_new_game() -> None:
    session = Session()
    session.dispatch({"action": "move", "source": "e2", "target": "e4"})
    session._rebuild([])
    assert session.view() == Session().view()
