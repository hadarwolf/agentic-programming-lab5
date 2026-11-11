"""A computer opponent that looks one move ahead."""

import random
from collections.abc import Iterator

from game import PROMOTION_PIECES, Position, legal_moves, move, promotes, status

# (source, target) or (source, target, promotion).
Move = tuple[str, ...]

VALUES = {"P": 1, "N": 3, "B": 3, "R": 5, "Q": 9, "K": 0}
CHECKMATE = 1000


def candidate_moves(position: Position) -> Iterator[Move]:
    for source, piece in sorted(position.board.items()):
        if piece[0] == position.turn:
            for target in legal_moves(position, source):
                if promotes(position, source, target):
                    for kind in PROMOTION_PIECES:
                        yield (source, target, kind)
                else:
                    yield (source, target)


def evaluate(position: Position, side: str) -> int:
    """Score a position for side: material, unless the game is over."""
    result = status(position)
    if result == "checkmate":
        return CHECKMATE if position.turn != side else -CHECKMATE
    if result == "stalemate":
        return 0
    return sum(
        VALUES[piece[1]] * (1 if piece[0] == side else -1) for piece in position.board.values()
    )


def choose_move(position: Position, rng: random.Random | None = None) -> Move | None:
    """Return the move with the best score after it, or None if there is no move.

    Ties are broken with rng, or with the random module when rng is None.
    """
    side = position.turn
    best: list[Move] = []
    best_score: int | None = None
    for candidate in candidate_moves(position):
        trial = position.copy()
        move(trial, *candidate)
        score = evaluate(trial, side)
        if best_score is None or score > best_score:
            best, best_score = [candidate], score
        elif score == best_score:
            best.append(candidate)
    if not best:
        return None
    return rng.choice(best) if rng is not None else random.choice(best)
