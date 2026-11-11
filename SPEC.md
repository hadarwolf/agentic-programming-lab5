# SPEC: Save/load (Hadar's branch)

This spec is for the coding agent working on the `save-load` branch. Read `NOTES.md` for the
team decisions this builds on. Ely builds undo on a separate `undo` branch at the same time,
and both branches merge into `main` afterwards.

## Starting point
- Branch from the latest `main` on `team`, the same commit Ely branches `undo` from:
  `git pull team main && git switch -c save-load`.
- Install the dev tools: `pip install -r requirements-dev.txt` (pytest, pytest-cov, ruff, mypy).
- `Session.moves` in `session.py` is the replayable history: a list of `(source, target)` tuples
  that `play()` appends to.
- `Session._rebuild(moves)` resets to a new game with the **same opponent** and replays `moves`
  through `play()`. It accepts lists as well as tuples, so JSON data can go straight in.
  Use it for loading. Don't set `position` or `notation` by hand.

## Requirements
Saving writes the game to a file. Loading it in a **fresh** `Session` (as after a server
restart) must restore all of these:
- the board and the side to move
- the move notation shown in the sidebar
- the opponent mode (`"human"` or `"computer"`)
- the history needed for undo (`moves`), so undo works on moves made before the save

## Design

### File format (JSON)
```json
{"version": 1, "opponent": "computer", "moves": [["e2", "e4"], ["d7", "d5"]], "redo": []}
```
- Always write `"redo": []` for now. Redo is built together later, and will fill it in.
- Store only the moves, never the board. The board, turn and notation are rebuilt by replay.
  After `feature/promotion` is merged, a move can have 3 items (`[src, dst, "Q"]`). Because
  replay passes each move through, keep the code free of any assumption that a move has
  exactly 2 items.

### `session.py`
- `Session.save(path)`: write the JSON above.
- `Session.load(path)`: read the file, check it, then `_rebuild` from it after setting `opponent`.
  - **Load is atomic.** Build and check the game in a separate `Session` first, then copy its
    state into `self`. If anything fails, `self` stays exactly as it was.
  - Raise `ValueError` with a clear message for every failure:
    - a missing or unreadable file: catch `OSError` and re-raise it as `ValueError`
    - bad JSON
    - an unknown `version`
    - an `opponent` that isn't `human` or `computer`
    - `moves` that aren't a list of lists of strings
    - an illegal move during replay (`move()` already raises `ValueError`)

    The server turns `ValueError` and `TypeError` into an HTTP 400 with the message, and
    anything else would crash the request.
- `dispatch`: add `"save"` and `"load"` actions. Both use `self.save_path`, which defaults to
  `"chess.save.json"`. `*.save.json` is already in `.gitignore`. Both return `self.view()` like
  the other actions.
- Keep the changes to `dispatch` and `__init__` small and grouped together, since Ely's undo
  branch edits the same places and we will merge them.
- Do **not** implement undo or redo, and don't change `play()` or `_rebuild()`.

### Front end
- `static/index.html`: add `Save game` and `Load game` buttons inside `#controls`, using
  `data-action="save"` and `data-action="load"`. The existing click handler in `static/app.js`
  already sends `{action: button.dataset.action}`.
- `static/app.js`: after a successful `load`, call `computerReply()`, in case the loaded game
  has the computer to move. Show a short status message such as "Game saved" or "Game loaded"
  in `#message`.
- Keep all game logic in Python. The browser only sends actions.

## Tests (`tests/test_save_load.py`)
Use pytest's `tmp_path` and set `session.save_path` there, so tests never touch the real
file. At minimum, cover:
1. **Round trip into a fresh session:** play some moves including a capture, save, then load
   into a **new** `Session()`. Check that `board`, `turn`, `moves` (notation), `opponent` and
   `session.moves` all match the original.
2. **Opponent mode is restored:** save a `Session("computer")` game, load it into a fresh
   `Session()` (default `human`), and check that the opponent is `"computer"`.
3. **Promotion setup round trip:** run the `promotion-setup` action, save, load, and check
   that `view()` is equal. `promotion-setup` starts a two-player game.
4. **Empty game:** saving a new game and loading it gives a new game.
5. **Through `dispatch`:** the `save` action, then the `load` action, works and returns the view.
6. **Bad input leaves the session unchanged:** a missing file, invalid JSON, a wrong version, a
   bad opponent, or an illegal move list each raise `ValueError`, and `session.view()` stays the
   same as before the load.
7. **The file is plain JSON** with `version`, `opponent`, `moves` and `redo`.

## Checks before pushing
```sh
python -m pytest --cov --cov-report=term-missing
ruff check tests/test_save_load.py
ruff format --check tests/test_save_load.py
```
Run ruff on any new module too, and `mypy --strict` on new modules only, since the starter
code has no type hints. Also try it by hand: `python3 server.py`, play against the computer,
save, stop the server with Ctrl+C, start it again, load, and check the board, sidebar and opponent.

Then commit and run `git push -u team save-load`.

## After this branch (for context)
1. Merge `undo` and `save-load` into `main` and add combined tests: undo after load, and save
   after undo.
2. Merge `feature/captured-pieces`, then `feature/promotion`, testing after each one. Check that
   promotion choices survive save/load.
3. Build redo together. It will fill in the `"redo"` key.
