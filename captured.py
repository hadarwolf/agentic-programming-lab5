"""Counts for the captured-pieces sidebar."""
from collections import Counter

from game import new_position


def missing_pieces(position, promoted=()):
    """Pieces captured so far. promoted lists the pieces pawns became, such as "wQ"."""
    expected = Counter(new_position()[0].values())
    for piece in promoted:
        # The pawn was not captured; it became this piece.
        expected[piece[0] + "P"] -= 1
        expected[piece] += 1
    current = Counter(position[0].values())
    return sorted((expected - current).elements())
