"""Counts for the captured-pieces sidebar."""

from collections import Counter
from collections.abc import Iterable

from game import Position, new_position


def missing_pieces(position: Position, promoted: Iterable[str] = ()) -> list[str]:
    """Pieces captured so far. promoted lists the pieces pawns became, such as "wQ"."""
    expected = Counter(new_position().board.values())
    for piece in promoted:
        # The pawn was not captured; it became this piece.
        expected[piece[0] + "P"] -= 1
        expected[piece] += 1
    current = Counter(position.board.values())
    return sorted((expected - current).elements())
