# Team decisions (Ely and Hadar)

## History
- `Session.moves` is the single source of history: one tuple per move, `(source, target)`.
  After `feature/promotion` is merged it becomes `(source, target, promotion)`.
- `Session._rebuild(moves)` starts a new game with the same opponent and replays the moves
  through `play()`, so `after_move()` hooks (such as the captured-pieces sidebar) stay correct.
- Undo and load use `_rebuild`, and redo uses `_apply`, rather than editing the board by hand.
- `game.Position` is a dataclass (`board`, `turn`), no longer a `[board, side]` list.

## Undo
- Against the computer, one undo takes back the computer's reply and your move, so it is
  your turn again. If your move ended the game, so the computer never replied, undo takes
  back only that one move.
- In a two-player game, one undo takes back one move.
- With no moves, undo does nothing.

## Save/load
- File format (JSON): `{"version": 1, "opponent": "human" | "computer", "moves": [[src, dst], ...], "redo": [[[src, dst], ...], ...]}`.
  `redo` holds one group of moves per undo, oldest first, so redo works after a load.
  Load checks that the redo moves are legal too.
- Save file name ends in `.save.json` (already ignored by git), e.g. `chess.save.json`.
- Load restores into a fresh `Session` with `_rebuild`, which also restores the history undo needs.

## Redo
- Redo replays exactly the moves undo removed, including the computer's reply and any
  promotion choice. A new move clears the redo history. A new game clears undo and redo history.

## Checks
- `ruff check` and `ruff format --check` on everything we write.
- `mypy --strict .` on everything, tests included.
- `python -m pytest --cov=. --cov-report=term-missing`.
- The exact commands are in CLAUDE.md.

## Merge order
`undo` and `save-load` into `main`, then `feature/captured-pieces`, then `feature/promotion`, then redo.
