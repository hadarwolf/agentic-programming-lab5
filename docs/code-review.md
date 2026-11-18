# Code review: `45f06c1..main`

Scope: everything merged into `main` since the starter commit, which covers undo, save/load,
captured pieces and promotion (up to `777b904`). This review was made with Claude Code's
built-in `code-review` skill on 2026-11-11.

The reviewer could not run the tools itself. Afterwards they were run in the project venv:
- `pytest`: **91 passed**.
- `ruff format --check captured.py session.py`: **fails**, confirming finding 9.
- `mypy --strict captured.py`: **fails**, confirming finding 9.

The other findings come from reading the code and have not been reproduced.

## Summary

| # | Severity | File | Finding |
|---|----------|------|---------|
| 1 | High | `session.py` (`save`) | A failed save raises `OSError`, not `ValueError`, so the request crashes |
| 2 | Medium | `session.py` (`save`) | A failed save can leave the last good save empty or cut off |
| 3 | Medium | `session.py` (`load`) | Some bad files raise errors other than `ValueError` |
| 4 | Medium | `session.py` (`after_move`) | A promoted piece's colour is guessed from the move index |
| 5 | Low | `session.py` (`undo`) | Undo picks how many moves to take back from the turn, and replays the whole game |
| 6 | Low | `static/app.js` | Cancelling the promotion dialog drops the selection, and old promotion squares stay in memory |
| 7 | Low | `computer.py` | The loop variable `piece` reuses an outer name |
| 8 | Low | `session.py`, `app.js` | The lists of valid opponents and promotion pieces are kept in several places |
| 9 | Checks | `captured.py`, `session.py` | ruff format and `mypy --strict` fail (team rule in NOTES.md) |
| 10 | Low | `session.py` | `save_path` is relative to the server's working directory |

## Findings

### 1. A failed save is not turned into a `ValueError`
**`session.py`, `Session.save`.** `open()` and `json.dump()` can raise `OSError`, which is not
caught. The server only turns `ValueError` and `TypeError` into an HTTP 400, and SPEC.md asks for
a `ValueError` for every failure.

*Scenario:* the folder is read-only, or `chess.save.json` is locked or is a folder. A
`PermissionError` reaches `do_POST`, the connection is dropped, and the browser shows a general
fetch or JSON error instead of a clear message.

### 2. A save is not written atomically
**`session.py`, `Session.save`.** Opening the real file with mode `"w"` empties it first. A
failure part-way through leaves an empty or partial file in place of the last good save.

*Scenario:* the disk is full, or the process is killed during `json.dump`. The next load fails
with "not valid JSON" and the earlier game is lost. *Fix:* write to a temp file, then call
`os.replace`.

### 3. `load` lets some parsing and reading errors through
**`session.py`, `Session.load`.** Only `json.JSONDecodeError` is wrapped.

*Scenario:* a file with thousands of nested arrays makes `json.loads` raise `RecursionError`,
which crashes the request. A file that isn't UTF-8 raises a raw `UnicodeDecodeError` instead of
the "Could not read save file" message.

### 4. A promoted piece's colour is guessed from the move index
**`session.py`, `Session.after_move`.** `"wb"[i % 2]` only works while every history starts
from the initial position with White to move. It also goes through the whole history again
after every move, so rebuilding a game of n moves costs O(n²).

*Scenario:* if a later feature (custom start positions, or a redo or load path that adds a move
outside `play()`) starts with Black to move, the colour comes out wrong and the captured
sidebar shows pieces that weren't captured, or misses ones that were. *Fix:* in `play()`,
record the actual promoted piece (`board[target]`) when there is a promotion.

### 5. Undo picks how many moves to take back from the turn
**`session.py`, `Session.undo`.** Whether to remove one move or two depends on
`position[1] == "w"` and `len(moves) >= 2`, not on who made the last move. Each undo also
replays the whole game through `_rebuild`, and every replayed move runs a full `status()` scan.

*Scenario:* in long games, undo and load get slow on the single-threaded server. The
one-or-two rule would also break if the computer could ever play White.

### 6. Problems with the promotion dialog in the browser
**`static/app.js`, `clickSquare`.** If the dialog is cancelled with Esc, no move is sent, but
the selection is still cleared and `computerReply()` still runs. `promotions` is not reset
when a piece is deselected or in the controls handler.

*Scenario:* the player picks a pawn, opens the dialog and presses Esc. The selection disappears
with no message, so the player has to pick the pawn again. Old promotion squares stay in memory
after New game, Undo or Load until the next `legal` request.

### 7. A loop variable reuses an outer name
**`computer.py`, `candidate_moves`.** The inner `for piece in PROMOTION_PIECES` reuses the outer
`piece` from `board.items()`.

*Scenario:* after the first promotion candidate, `piece` holds `"Q"`/`"R"`/… instead of the
piece on the board. A later edit that reads `piece[0]` inside the target loop would quietly get
the wrong value. *Fix:* rename it to `choice`.

### 8. The lists of valid values are kept in several places
**`session.py`, `Session.load` and `__init__`, and `static/app.js`.** `("human", "computer")`
is checked in both `__init__` and `load`, and the promotion pieces are hard-coded as
`['Q','R','B','N']` in the JS dialog as well as `PROMOTION_PIECES` in `game.py`.

*Scenario:* adding an opponent mode or changing the promotion pieces means editing several
places. If one is missed, load rejects valid saves, or the dialog offers a piece that `move()`
rejects.

### 9. The team's checks fail on new code
**`captured.py`, `session.py`.** NOTES.md asks for `ruff format --check` on everything we write
and `mypy --strict` on new modules. Confirmed:
- `captured.py` needs a blank line after the docstring, and as a new module it has no type
  hints, so `mypy --strict` fails.
- `session.py` would be reformatted. The new lines that fail are the `self.moves.append(...)`
  line in `play`, the `undo` condition, and the `move`/`legal` lines in `dispatch`. The
  `PROMOTION_SETUP` list and `computer_to_move` are starter code and were already unformatted.

### 10. `save_path` depends on the working directory
**`session.py`, `Session.save_path`.** `"chess.save.json"` is relative, so the file goes
wherever the server was started from.

*Scenario:* the player saves, then restarts with `python3 /path/to/server.py` from a different
folder. Load game fails with "Could not read save file", and the save sits in a folder that
`.gitignore` may not cover.
