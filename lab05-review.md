# Lab 5 review

Commit reviewed: 777b904 · Reviewer: Claude Code, Opus 5.5 · Unmerged branches: none

## Highlights

- Redo was never built. No commit adds it, `session.py:76` writes an always-empty `"redo": []`, and NOTES.md still lists it as "Redo (planned)". Building it, with tests, is the first thing to do.
- The checks were installed but never configured or run to green. `pyproject.toml` has no `[tool.ruff]` or `[tool.mypy]` section, `ruff format --check` would reformat 7 files, and `mypy --strict` reports 414 errors. There is no CLAUDE.md or AGENTS.md naming the checks.
- Well done: one replayable history (`Session.moves` plus `_rebuild`, b5b2341) that undo, load and promotion all share. The decision is written down in NOTES.md before the features were built.
- Well done: tests of features together, in a separate commit after each merge (5d9748e, cbfb3d1, 777b904).
- Game state: the position is still the starter's 2-item list `[board, side]` (`game.py:18`). Everything the features added lives on `Session`. Saving stores only the moves and rebuilds the rest, so nothing is lost.

## At a glance

| Check | Result |
| --- | --- |
| Tests | 91 passed, 0 failed, in 22.75 s |
| Coverage | 93% total; lowest: server.py 0% |
| `ruff check` | 2 findings |
| `ruff format --check` | 7 files would change |
| `mypy --strict` | 414 errors in 15 files |
| Game state | list or tuple of 2 items (2 in the starter) |
| Game state restructured in the lab | no |
| Instruction file | none |

## The week's practices

1. ⚠️ **Tests for each feature:** `test_undo.py`, `test_save_load.py`, `test_captured.py` and `test_promotion.py` exist. Redo has no tests because it does not exist.
2. ✅ **Tests of features together:** `test_undo_save_load.py:23` tests undo after a load, `test_captured_combined.py:13` tests undo after a capture, and `test_promotion_combined.py:31` tests a promotion surviving save and load.
3. ✅ **Assertions that check results:** there is no `print(` in `tests/`, and the spot-checked tests assert on the view, the turn and the move counts (`test_computer.py:41-48`).
4. ⚠️ **Fast and repeatable:** the suite takes 22.75 s, and one test alone takes 7.40 s (`test_ties_vary_with_the_random_source`). The opponent takes an `rng` (`computer.py:34`), but session-level computer tests use the unseeded module `random`.
5. not checked **Bugs became tests:** the history has no fix commits to inspect.
6. ✅ **No weakened tests:** `git log -p -- tests/ | grep -E '^-\s*assert'` returns nothing.
7. ✅ **Coverage:** 93%. `server.py` is at 0%, and every other module is at 97% or higher.
8. ❌ **Linted beyond the defaults:** there is no Ruff section in `pyproject.toml`. Ruff still enables extra rules (TRY004, from a configuration outside the repo). It reports 2 findings, and there is 1 `# noqa` (`session.py:94`).
9. ❌ **Formatted:** 7 files would be reformatted.
10. ❌ **Type-checked:** 414 errors. There are 2 uses of `Any` (`tests/test_save_load.py`) and 0 `# type: ignore`. `session.py` has no annotations at all, although NOTES.md says new modules would be strict.
11. ⚠️ **From the start or at the end:** the tools were added early, in `requirements-dev.txt` at b5b2341. Configuration and annotations never arrived.
12. ❌ **Checks in the instruction file:** there is no CLAUDE.md or AGENTS.md, and no `.claude/settings.json` hook. NOTES.md lists the commands, but agents do not read it automatically.

## The game state

The position is a list read by position, `[board, side]`. It has 2 items, as in the starter (`game.py:18`), and `copy_position` copies both. The features put their data on `Session` instead: `notation`, `moves`, `captured` and `opponent`. `save` writes only `opponent` and `moves`, and `load` rebuilds the rest through `_rebuild`, so notation and captured pieces are restored. The structure was not restructured during the lab: the log for `game.py` and `session.py` shows growth only.

## Other findings

- `Session.__init__` is called on a live object for undo and new game (`session.py:53` and `session.py:157`). It works, but any attribute added later must also be reset there, or it will leak across games.
- Save and load handle files well. They use JSON, not `pickle`, with a fixed `save_path` that the browser cannot set. A malformed save leaves the game unchanged (`session.py:111-119`), and this is tested (`test_save_load.py:146`).
- The imports in `session.py:5-6` are unsorted (I001). This is one of the 2 Ruff findings, and `ruff check --fix` would fix it.
