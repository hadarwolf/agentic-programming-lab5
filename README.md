# ♟️ Chess: Testing New Features

**Agentic Programming · Lab 5: Testing New Features**
*Hadar Wolf & Ely Grunfeld*

A local two-player (or player-vs-computer) chess game in Python with a browser UI. We started from the course's [chess workshop](https://github.com/avivz/aicode-lab05-chess) starter. Working on separate branches with coding agents, we added **undo, save/load and redo**, merged two supplied feature branches (**captured pieces** and **pawn promotion**), and covered every combination of features with tests.

✅ **112 tests pass** · `ruff check` clean · `ruff format` clean · `mypy --strict` clean

## What we built

| Feature | Notes |
|---|---|
| **Replayable history** | `Session.moves` is the single source of truth. Undo, redo, load and promotion all rebuild the position by replaying moves (`Session._rebuild`), so derived state like captured pieces stays correct. |
| **Undo** | Against the computer, one undo takes back the computer's reply and your move. In a two-player game it takes back one move. With no moves, it does nothing. |
| **Save / load** | A JSON file (`*.save.json`) stores the opponent type, the moves and the redo history. Loading into a fresh session restores everything, including undo and redo. |
| **Redo** | Replays exactly the moves that undo removed, including the computer's reply and any promotion choice. A new move clears redo. |
| **Captured pieces + promotion** | The supplied branches, merged in order and then tested together with undo and save/load. |
| **Checks** | The position became a typed dataclass. ruff and mypy are configured, the computer's tie-breaks are seeded so tests are deterministic, and [`CLAUDE.md`](CLAUDE.md) tells agents to run all four checks. |

Team decisions are written down in [`NOTES.md`](NOTES.md), and the save/load spec is in [`SPEC.md`](SPEC.md).

## Run

Requires Python 3.10+.

```sh
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
python server.py                   # open http://127.0.0.1:8000
```

## Checks

```sh
python -m pytest -q --cov=. --cov-report=term-missing
ruff check .
ruff format --check .
mypy --strict .
```

## How we worked

- One feature = one branch = its own tests. The merge order was undo and save/load, then captured pieces, then promotion, then redo.
- After every merge we ran all the checks and added a test of the features *together* (for example `test_undo_save_load.py` and `test_promotion_combined.py`).
- Our working plan and checklists are in [`docs/lab05-plan.md`](docs/lab05-plan.md).
- There are two agent-made reviews: [`docs/code-review.md`](docs/code-review.md) covers everything merged into `main`, and [`lab05-review.md`](lab05-review.md) is the lab review of `777b904`.
- The original assignment and the starter's README are in [`docs/ASSIGNMENT.md`](docs/ASSIGNMENT.md).

## Files

- `game.py`: board, moves, check, checkmate, stalemate (castling and en passant aren't supported)
- `session.py`: game actions, history (undo, redo, save/load), opponent, notation, sidebar
- `captured.py`: captured-pieces tracking
- `computer.py`: a computer opponent that looks one move ahead
- `server.py`: HTTP actions plus static files
- `static/`: the browser UI
- `tests/`: 112 tests, including combined-feature tests

---

Part of my **Agentic Programming** labs (HUJI, AICODE 67723):
[Lab 1 · CTF Arena](https://github.com/hadarwolf/agentic-programming-lab1) · [Lab 2 · LLM failure modes](https://github.com/hadarwolf/agentic-programming-lab2) · [Lab 3 · Coin Dash with several agents](https://github.com/hadarwolf/agentic-programming-lab3) · [Lab 4 · Traffic monitor spec](https://github.com/hadarwolf/agentic-programming-lab4) · **Lab 5 · Chess: testing new features** · [Lab 6 · Binary search explainer video](https://github.com/hadarwolf/agentic-programming-lab6)
