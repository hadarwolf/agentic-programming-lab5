from game import new_position
from session import Session

SCHOLARS_MATE = [
    ("e2", "e4"),
    ("e7", "e5"),
    ("f1", "c4"),
    ("b8", "c6"),
    ("d1", "h5"),
    ("g8", "f6"),
    ("h5", "f7"),
]


def play_all(session: Session, moves: list[tuple[str, str]]) -> None:
    for source, target in moves:
        session.play(source, target)


def test_undo_restores_a_captured_piece_turn_and_notation() -> None:
    session = Session()
    play_all(session, [("e2", "e4"), ("d7", "d5"), ("e4", "d5")])
    assert session.position.board["d5"] == "wP"
    session.dispatch({"action": "undo"})
    assert session.position.board["d5"] == "bP"
    assert session.position.board["e4"] == "wP"
    assert session.position.turn == "w"
    assert session.notation == ["e2-e4", "d7-d5"]
    assert session.moves == [("e2", "e4"), ("d7", "d5")]


def test_two_player_undo_takes_back_one_move_at_a_time() -> None:
    session = Session()
    play_all(session, [("e2", "e4"), ("e7", "e5")])
    session.undo()
    assert session.position.turn == "b"
    assert session.notation == ["e2-e4"]
    session.undo()
    assert session.position == new_position()
    assert session.notation == []


def test_repeated_undo_stops_at_the_start() -> None:
    session = Session()
    play_all(session, [("e2", "e4")])
    for _ in range(3):
        view = session.dispatch({"action": "undo"})
    assert session.position == new_position()
    assert view["moves"] == []
    assert view["turn"] == "w"


def test_undo_on_a_new_game_does_nothing() -> None:
    session = Session()
    before = session.view()
    session.dispatch({"action": "undo"})
    assert session.view() == before


def test_undo_against_the_computer_takes_back_the_reply_and_the_move() -> None:
    session = Session("computer")
    session.dispatch({"action": "move", "source": "e2", "target": "e4"})
    session.dispatch({"action": "computer-move"})
    assert len(session.moves) == 2
    session.dispatch({"action": "undo"})
    assert session.position == new_position()
    assert session.notation == []
    assert session.position.turn == "w"


def test_undo_against_the_computer_keeps_earlier_moves() -> None:
    session = Session("computer")
    play_all(session, [("e2", "e4"), ("e7", "e5"), ("g1", "f3"), ("b8", "c6")])
    session.undo()
    assert session.moves == [("e2", "e4"), ("e7", "e5")]
    assert session.position.turn == "w"
    assert not session.computer_to_move()


def test_undo_after_the_player_checkmates_the_computer_takes_back_one_move() -> None:
    session = Session("computer")
    play_all(session, SCHOLARS_MATE)
    assert session.view()["status"] == "checkmate"
    session.undo()
    assert session.moves == SCHOLARS_MATE[:-1]
    assert session.position.turn == "w"
    assert session.view()["status"] is None


def test_undo_keeps_the_opponent() -> None:
    for opponent in ("human", "computer"):
        session = Session(opponent)
        play_all(session, [("e2", "e4"), ("e7", "e5")])
        session.undo()
        assert session.opponent == opponent


def test_undo_matches_a_game_that_never_made_the_move() -> None:
    undone = Session()
    play_all(undone, SCHOLARS_MATE)
    undone.undo()
    direct = Session()
    play_all(direct, SCHOLARS_MATE[:-1])
    # The only difference: the undone game can redo the move it took back.
    undone_view, direct_view = undone.view(), direct.view()
    assert undone_view.pop("can_redo") is True
    assert direct_view.pop("can_redo") is False
    assert undone_view == direct_view
