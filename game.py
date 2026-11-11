"""Movement rules for the lab's chess variant.

Check, checkmate and stalemate follow standard chess. There is no castling and no
en passant.
"""

from dataclasses import dataclass, field

# A square such as "e4" mapped to a piece such as "wP" (side, then kind).
Board = dict[str, str]


@dataclass
class Position:
    """The board and the side to move ("w" or "b")."""

    board: Board = field(default_factory=dict)
    turn: str = "w"

    def copy(self) -> "Position":
        return Position(dict(self.board), self.turn)


FILES = "abcdefgh"
BACK_ROW = "RNBQKBNR"


def new_position() -> Position:
    board: Board = {}
    for file, piece in zip(FILES, BACK_ROW, strict=True):
        board[file + "1"] = "w" + piece
        board[file + "2"] = "wP"
        board[file + "7"] = "bP"
        board[file + "8"] = "b" + piece
    return Position(board, "w")


def copy_position(position: Position) -> Position:
    """Copy the board and side to move."""
    return position.copy()


def coordinates(square: str) -> tuple[int, int]:
    if not isinstance(square, str) or len(square) != 2:
        raise ValueError("Expected a square such as e2")
    if square[0] not in FILES or square[1] not in "12345678":
        raise ValueError("Square is outside the board")
    return FILES.index(square[0]), int(square[1]) - 1


def other(side: str) -> str:
    return "b" if side == "w" else "w"


def in_check(board: Board, side: str) -> bool:
    king = next((square for square, piece in board.items() if piece == side + "K"), None)
    return king is not None and any(
        king in reachable(board, square) for square, piece in board.items() if piece[0] != side
    )


def status(position: Position) -> str | None:
    """Return "check", "checkmate", "stalemate", or None for the side to move."""
    board, turn = position.board, position.turn
    check = in_check(board, turn)
    if any(legal_moves(position, square) for square, piece in board.items() if piece[0] == turn):
        return "check" if check else None
    return "checkmate" if check else "stalemate"


def winner(position: Position) -> str | None:
    if status(position) == "checkmate":
        return "White" if position.turn == "b" else "Black"
    return None


def legal_moves(position: Position, source: str) -> list[str]:
    """Moves for the side to move that do not leave its own king in check."""
    coordinates(source)
    board, turn = position.board, position.turn
    piece = board.get(source)
    if not piece or piece[0] != turn:
        return []
    targets = []
    for target in reachable(board, source):
        trial = board.copy()
        trial[target] = trial.pop(source)
        if not in_check(trial, turn):
            targets.append(target)
    return targets


def reachable(board: Board, source: str) -> list[str]:
    """Squares the piece on source attacks or can move to, ignoring check."""
    piece = board[source]
    turn = piece[0]
    x, y = coordinates(source)
    targets = []
    for tx in range(8):
        for ty in range(8):
            target = FILES[tx] + str(ty + 1)
            occupant = board.get(target)
            if target == source or (occupant and occupant[0] == turn):
                continue
            dx, dy = tx - x, ty - y
            kind = piece[1]
            allowed = False
            if kind == "P":
                direction = 1 if turn == "w" else -1
                home = 1 if turn == "w" else 6
                allowed = (
                    (dx == 0 and dy == direction and not occupant)
                    or (
                        dx == 0
                        and dy == 2 * direction
                        and y == home
                        and not occupant
                        and FILES[x] + str(y + direction + 1) not in board
                    )
                    or (abs(dx) == 1 and dy == direction and bool(occupant))
                )
            elif kind == "N":
                allowed = (abs(dx), abs(dy)) in ((1, 2), (2, 1))
            elif kind == "K":
                allowed = max(abs(dx), abs(dy)) == 1
            else:
                diagonal = abs(dx) == abs(dy)
                straight = dx == 0 or dy == 0
                allowed = (
                    (kind == "B" and diagonal)
                    or (kind == "R" and straight)
                    or (kind == "Q" and (diagonal or straight))
                )
                if allowed:
                    sx = (dx > 0) - (dx < 0)
                    sy = (dy > 0) - (dy < 0)
                    for step in range(1, max(abs(dx), abs(dy))):
                        intermediate = FILES[x + step * sx] + str(y + step * sy + 1)
                        if intermediate in board:
                            allowed = False
                            break
            if allowed:
                targets.append(target)
    return targets


PROMOTION_PIECES = ("Q", "R", "B", "N")


def promotes(position: Position, source: str, target: str) -> bool:
    piece: str | None = position.board.get(source)
    return piece is not None and piece[1] == "P" and target[1] in "18"


def move(position: Position, source: str, target: str, promotion: str | None = None) -> str:
    """Apply a move in place. Return a short move label.

    A pawn reaching the last rank needs promotion: "Q", "R", "B" or "N".
    """
    coordinates(target)
    if target not in legal_moves(position, source):
        raise ValueError("That move is not allowed")
    promoting = promotes(position, source, target)
    if promoting and promotion not in PROMOTION_PIECES:
        raise ValueError("Choose a queen, rook, bishop or knight to promote to")
    if not promoting and promotion is not None:
        raise ValueError("Only a pawn reaching the last rank promotes")
    board: Board = position.board
    piece = board.pop(source)
    captured = target in board
    chosen = ""
    if promoting and promotion is not None:
        piece = piece[0] + promotion
        chosen = "=" + promotion
    board[target] = piece
    position.turn = other(position.turn)
    suffix = {"check": "+", "checkmate": "#"}.get(status(position) or "", "")
    return source + ("x" if captured else "-") + target + chosen + suffix
