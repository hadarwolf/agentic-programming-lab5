# Chess game: instructions for coding agents

Team decisions (history, undo, redo, save format) are in NOTES.md. Read it before changing
`session.py`.

## Checks

Run all four before saying a change is done, and fix what they report. Don't weaken them:
no new `# noqa`, `# type: ignore` or `Any` without a comment saying why, and no deleted or
loosened assertions.

```
.venv/bin/python -m pytest -q --cov=. --cov-report=term-missing
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy --strict .
```

## Conventions

- Game state is `game.Position` (a dataclass: `board`, `turn`) plus the named fields of
  `session.Session`. Don't index it by number or turn it back into a list.
- History changes go through `Session._rebuild`, never by editing the board by hand.
- Every new feature gets a test, and a test with each feature it shares state with
  (undo, redo, save/load, captured pieces, promotion).
- Every bug fix comes with a test that fails before the fix.
- Tests must not depend on luck: the computer's tie-breaks are seeded in `tests/conftest.py`.
