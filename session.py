"""Application actions and information shown beside the board."""

import json

from computer import choose_move
from game import (
    legal_moves,
    move,
    new_position,
    status,
    winner,
)


# Legal from the standard starting position under this game's rules.
# Next move: b7-a8, capturing a rook and reaching the last rank.
PROMOTION_SETUP = [
    ("a2", "a4"), ("h7", "h5"),
    ("a4", "a5"), ("h5", "h4"),
    ("a5", "a6"), ("h4", "h3"),
    ("a6", "b7"), ("h3", "g2"),
]


SAVE_VERSION = 1


class Session:
    save_path = "chess.save.json"  # Used by the "save" and "load" actions.

    def __init__(self, opponent="human"):
        if opponent not in ("human", "computer"):
            raise ValueError("Unknown opponent")
        self.position = new_position()
        self.notation = []
        self.moves = []  # Replayable history: one (source, target) tuple per move.
        self.opponent = opponent

    def play(self, source, target):
        label = move(self.position, source, target)
        self.notation.append(label)
        self.moves.append((source, target))
        self.after_move()

    def _rebuild(self, moves):
        """Reset to a new game with the same opponent, then replay moves through play()."""
        moves = [tuple(m) for m in moves]
        self.__init__(self.opponent)
        for m in moves:
            self.play(*m)

    def save(self, path):
        """Write the game as JSON. Only the moves are stored; load rebuilds the rest."""
        data = {
            "version": SAVE_VERSION,
            "opponent": self.opponent,
            "moves": [list(m) for m in self.moves],
            "redo": [],
        }
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file)

    def load(self, path):
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
            raise ValueError("Save file must contain a JSON object")  # noqa: TRY004
        version = data.get("version")
        if type(version) is not int or version != SAVE_VERSION:
            raise ValueError(f"Unsupported save file version: {version!r}")
        opponent = data.get("opponent")
        if opponent not in ("human", "computer"):
            raise ValueError(f"Unknown opponent in save file: {opponent!r}")
        moves = data.get("moves")
        if not isinstance(moves, list) or not all(
            isinstance(m, list) and m and all(isinstance(part, str) for part in m)
            for m in moves
        ):
            raise ValueError("Save file moves must be a list of lists of strings")
        # Build the game in a separate session, so self is untouched if replay fails.
        loaded = type(self)(opponent)
        try:
            loaded._rebuild(moves)
        except (ValueError, TypeError) as error:
            bad = moves[len(loaded.moves)]
            raise ValueError(
                f"Save file move {len(loaded.moves) + 1} ({'-'.join(bad)}) is illegal: {error}"
            ) from error
        self.__dict__.update(loaded.__dict__)

    def after_move(self):
        pass

    def view(self):
        return {
            "board": self.position[0],
            "turn": self.position[1],
            "moves": self.notation,
            "opponent": self.opponent,
            "status": status(self.position),
            "winner": winner(self.position),
            **self.sidebar(),
        }

    def computer_to_move(self):
        return (self.opponent == "computer" and self.position[1] == "b"
                and status(self.position) not in ("checkmate", "stalemate"))

    def sidebar(self):
        return {}

    def dispatch(self, action):
        command = action.get("action")
        if command == "move":
            if self.computer_to_move():
                raise ValueError("Wait for the computer's move")
            self.play(action.get("source"), action.get("target"))
        elif command == "computer-move":
            if not self.computer_to_move():
                raise ValueError("It is not the computer's turn")
            self.play(*choose_move(self.position))
        elif command == "legal":
            return {"targets": legal_moves(self.position, action.get("source"))}
        elif command == "new":
            self.__init__(action.get("opponent", "human"))
        elif command == "promotion-setup":
            self.__init__()
            for source, target in PROMOTION_SETUP:
                self.play(source, target)
        elif command == "save":
            self.save(self.save_path)
        elif command == "load":
            self.load(self.save_path)
        else:
            raise ValueError("Unknown action")
        return self.view()
