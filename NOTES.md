# Team decisions (Ely and Hadar)

## History
- `Session.moves` is the single source of history: one tuple per move, `(source, target)`.
  After `feature/promotion` is merged it becomes `(source, target, promotion)`.
- `Session._rebuild(moves)` starts a new game with the same opponent and replays the moves
  through `play()`, so `after_move()` hooks (such as the captured-pieces sidebar) stay correct.
- Undo, load, and later redo all use `_rebuild` rather than editing the board by hand.

## Undo
- Against the computer, one undo takes back the computer's reply and your move, so it is
  your turn again. If your move ended the game, so the computer never replied, undo takes
  back only that one move.
- In a two-player game, one undo takes back one move.
- With no moves, undo does nothing.

## Save/load
- File format (JSON): `{"version": 1, "opponent": "human" | "computer", "moves": [[src, dst], ...], "redo": [...]}`.
  `redo` is reserved for the redo feature, so that redo works after a load.
- Save file name ends in `.save.json` (already ignored by git), e.g. `chess.save.json`.
- Load restores into a fresh `Session` with `_rebuild`, which also restores the history undo needs.

## Redo (planned)
- Redo replays exactly the moves undo removed, including the computer's reply and any
  promotion choice. A new move clears the redo history. A new game clears undo and redo history.

## Checks
- `ruff check` and `ruff format --check` on everything we write.
- `mypy --strict` on new modules only. The starter code has no type hints.
- `python -m pytest --cov --cov-report=term-missing`.

## Merge order
`undo` and `save-load` into `main`, then `feature/captured-pieces`, then `feature/promotion`, then redo.
