"""Application actions and information shown beside the board."""

import json
from typing import Any

from captured import missing_pieces
from computer import Move, choose_move
from game import (
    legal_moves,
    move,
    new_position,
    promotes,
    status,
    winner,
)

# Legal from the standard starting position under this game's rules.
# Next move: b7-a8, capturing a rook and reaching the last rank.
PROMOTION_SETUP: list[Move] = [
    ("a2", "a4"),
    ("h7", "h5"),
    ("a4", "a5"),
    ("h5", "h4"),
    ("a5", "a6"),
    ("h4", "h3"),
    ("a6", "b7"),
    ("h3", "g2"),
]

SAVE_VERSION = 1
OPPONENTS = ("human", "computer")


def _is_move(value: object) -> bool:
    """A move as JSON: a non-empty list of strings."""
    return isinstance(value, list) and bool(value) and all(isinstance(part, str) for part in value)


def _square(action: dict[str, Any], key: str) -> str:
    """The square an action names under key, such as "e2"."""
    value = action.get(key)
    if not isinstance(value, str):
        raise ValueError("Expected a square such as e2")
    return value


class Session:
    save_path = "chess.save.json"  # Used by the "save" and "load" actions.

    def __init__(self, opponent: str = "human") -> None:
        self.new_game(opponent)

    def new_game(self, opponent: str = "human") -> None:
        """Start again from the initial position, with no undo or redo history."""
        if opponent not in OPPONENTS:
            raise ValueError("Unknown opponent")
        self.opponent = opponent
        # Each item is the moves one undo removed, in play order; the last is redone first.
        self.redo_moves: list[list[Move]] = []
        self._reset()

    def _reset(self) -> None:
        """Clear the board and the move history; keep the opponent and redo history."""
        self.position = new_position()
        self.notation: list[str] = []
        self.moves: list[Move] = []  # Replayable history: (source, target[, promotion]).
        self.captured: list[str] = []

    def _apply(self, source: str, target: str, promotion: str | None = None) -> None:
        label = move(self.position, source, target, promotion)
        self.notation.append(label)
        # A promotion is stored as a third item, so replay makes the same choice.
        self.moves.append((source, target) if promotion is None else (source, target, promotion))
        self.after_move()

    def play(self, source: str, target: str, promotion: str | None = None) -> None:
        """Make a new move. A new move clears the redo history."""
        self._apply(source, target, promotion)
        self.redo_moves.clear()

    def _rebuild(self, moves: list[Move] | list[list[str]]) -> None:
        """Reset to a new game with the same opponent, then replay moves.

        The redo history is kept, so undo can add to it.
        """
        replay = [tuple(m) for m in moves]
        self._reset()
        for m in replay:
            self._apply(*m)

    def undo(self) -> None:
        """Take back the last move; against the computer, also its reply.

        Against the computer, one undo returns to the player's turn: it removes the
        computer's reply and the player's move. If the player's move ended the game,
        so there was no reply, it removes only that move. With no moves it does nothing.
        """
        if not self.moves:
            return
        count = 1
        if self.opponent == "computer" and self.position.turn == "w" and len(self.moves) >= 2:
            count = 2
        removed = self.moves[-count:]
        self._rebuild(self.moves[:-count])
        self.redo_moves.append(removed)

    def redo(self) -> None:
        """Replay the moves the last undo removed. With nothing undone it does nothing."""
        if not self.redo_moves:
            return
        for m in self.redo_moves.pop():
            self._apply(*m)

    def save(self, path: str) -> None:
        """Write the game as JSON. Only moves are stored; load rebuilds the rest."""
        data = {
            "version": SAVE_VERSION,
            "opponent": self.opponent,
            "moves": [list(m) for m in self.moves],
            "redo": [[list(m) for m in group] for group in self.redo_moves],
        }
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file)

    def load(self, path: str) -> None:
        """Replace this game with the one saved at path. On any error, nothing changes."""
        try:
            with open(path, encoding="utf-8") as file:
                text = file.read()
        except OSError as error:
            reason = error.strerror or error
            raise ValueError(f"Could not read save file {path}: {reason}") from error
        try:
            data = json.loads(text)
        except json.JSONDecodeError as error:
            raise ValueError(f"Save file is not valid JSON: {error.msg}") from error
        if not isinstance(data, dict):
            raise ValueError("Save file must contain a JSON object")
        version = data.get("version")
        if type(version) is not int or version != SAVE_VERSION:
            raise ValueError(f"Unsupported save file version: {version!r}")
        opponent = data.get("opponent")
        if opponent not in OPPONENTS:
            raise ValueError(f"Unknown opponent in save file: {opponent!r}")
        moves = data.get("moves")
        if not isinstance(moves, list) or not all(_is_move(m) for m in moves):
            raise ValueError("Save file moves must be a list of lists of strings")
        redo = data.get("redo", [])
        if not isinstance(redo, list) or not all(
            isinstance(group, list) and group and all(_is_move(m) for m in group) for group in redo
        ):
            raise ValueError("Save file redo must be a list of lists of moves")
        # Build the game in a separate session, so self is untouched if replay fails.
        loaded = type(self)(opponent)
        try:
            loaded._rebuild(moves)
        except (ValueError, TypeError) as error:
            bad = moves[len(loaded.moves)]
            raise ValueError(
                f"Save file move {len(loaded.moves) + 1} ({'-'.join(bad)}) is illegal: {error}"
            ) from error
        # Every redo must be playable later: replay them all, last saved first.
        probe = type(self)(opponent)
        try:
            probe._rebuild(moves + [m for group in reversed(redo) for m in group])
        except (ValueError, TypeError) as error:
            raise ValueError(f"Save file redo moves are illegal: {error}") from error
        loaded.redo_moves = [[tuple(m) for m in group] for group in redo]
        self.__dict__.update(loaded.__dict__)

    def after_move(self) -> None:
        # Every game starts from the initial position with White to move, so a
        # move's index tells which side made it.
        promoted = ["wb"[i % 2] + m[2] for i, m in enumerate(self.moves) if len(m) > 2]
        self.captured = missing_pieces(self.position, promoted)

    def view(self) -> dict[str, Any]:
        return {
            "board": self.position.board,
            "turn": self.position.turn,
            "moves": self.notation,
            "opponent": self.opponent,
            "status": status(self.position),
            "winner": winner(self.position),
            "can_redo": bool(self.redo_moves),
            **self.sidebar(),
        }

    def computer_to_move(self) -> bool:
        return (
            self.opponent == "computer"
            and self.position.turn == "b"
            and status(self.position) not in ("checkmate", "stalemate")
        )

    def sidebar(self) -> dict[str, Any]:
        return {"captured": self.captured}

    def dispatch(self, action: dict[str, Any]) -> dict[str, Any]:
        command = action.get("action")
        if command == "move":
            if self.computer_to_move():
                raise ValueError("Wait for the computer's move")
            promotion = action.get("promotion")
            if promotion is not None and not isinstance(promotion, str):
                raise ValueError("Choose a queen, rook, bishop or knight to promote to")
            self.play(_square(action, "source"), _square(action, "target"), promotion)
        elif command == "computer-move":
            if not self.computer_to_move():
                raise ValueError("It is not the computer's turn")
            reply = choose_move(self.position)
            if reply is None:
                raise ValueError("The computer has no move")
            self.play(*reply)
        elif command == "legal":
            source = _square(action, "source")
            targets = legal_moves(self.position, source)
            return {
                "targets": targets,
                "promotions": [t for t in targets if promotes(self.position, source, t)],
            }
        elif command == "undo":
            self.undo()
        elif command == "redo":
            self.redo()
        elif command == "new":
            self.new_game(action.get("opponent", "human"))
        elif command == "promotion-setup":
            self.new_game()
            for source, target in PROMOTION_SETUP:
                self.play(source, target)
        elif command == "save":
            self.save(self.save_path)
        elif command == "load":
            self.load(self.save_path)
        else:
            raise ValueError("Unknown action")
        return self.view()
