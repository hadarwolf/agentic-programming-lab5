# Lab 5 plan: actions, prompts and checks

Project folder: `aicode-lab05-chess`

## Terminals to keep open (all in the project folder)

1. **Claude**: `claude` (come back later with `claude --continue` or `claude --resume`).
2. **Server**: `.venv\Scripts\Activate.ps1`, then `python server.py`, then open http://127.0.0.1:8000.
   Restart it (Ctrl+C, then run it again) after every change to Python code.
3. **Your own commands** (optional). Claude can run all git commands for you; just ask.

## Rules for the whole lab

- Pull `main` before starting any new branch.
- One feature = one branch = its own tests.
- Commit before switching branches. Don't switch branches while Claude is editing.
- Tell your partner before you push `main`.
- Never sit idle: while an agent works, review a branch, test in the browser, or start the next prompt in your other session.
- When Claude reports a conflict or a design choice, **you** decide.

## Standard checks (after every feature and every merge)

- [ ] `python -m pytest`: all tests pass, old and new
- [ ] `ruff check .`: no lint errors
- [ ] `ruff format --check .`: formatting is clean
- [ ] `mypy .`: no type errors
- [ ] Read the new tests: they assert the board, turn and move list, not just "no crash"
- [ ] Restart the server and play-test the feature in the browser
- [ ] Play-test the older features too: did anything break?

---

## 0. Start of the lab (~5 min)

- [ ] Sit with a **new** partner (not from Labs 1–4)
- [ ] Show the instructor: the game runs and `python -m pytest` passes (27 tests)
- [ ] Agree who is **Partner A** (merges, checks, redo) and who is **Partner B** (undo, then castling/en passant)

## 1. Phase 1: Get started (~15 min)

### 1.1 Shared repo
- [ ] Partner A: github.com → New repository → **Private**, **empty** (no README, .gitignore or license)
- [ ] Partner A: Settings → Collaborators → add Partner B; Partner B accepts the invite
- [ ] Both: `git remote add team https://github.com/<owner>/<repo>.git`
- [ ] Both: `git remote -v` shows `origin` and `team`
- [ ] Partner A: `git push team main`
- [ ] Both: push a test branch (`git switch -c test-<name>`, then `git push team test-<name>`), run `git fetch team` and `git branch -a`, and see the partner's branch. Then `git switch main`.

### 1.2 Understand the code (already done)
- [ ] Board and turn: `position = [board, turn]` in `game.py`. The board is a dict like `{"e2": "wP"}`.
- [ ] Move history: `Session.notation` in `session.py` (labels only, e.g. `"d4xe5+"`)
- [ ] Actions: `Session.dispatch` in `session.py`. The computer plays Black; the browser asks for its move after 500 ms.

### 1.3 Decisions (write these into CLAUDE.md later)
- [ ] Undo vs. computer: one undo removes the computer's reply **and** your move, so it's your turn again
- [ ] Undo before the computer replied: removes only your move
- [ ] Undo at the start: error, and the button is disabled
- [ ] Undo after checkmate or stalemate: allowed, and the game continues
- [ ] New game: clears undo and redo history

### 1.4 Checks: what exists, what's missing
- [ ] Exists: only pytest
- [ ] Missing: linter, formatter, type checker, instruction file
- [ ] Decision: add ruff (lint and format), mypy, and CLAUDE.md

## 2. Phase 2: Build and test (~50 min)

### 2.1 Partner A: set up checks (do first, merge early)
On `main`, give Claude **Prompt 1**.
- [ ] Look at the format diff Claude shows. If it changes a lot of `game.py` or `session.py`, do 2.2 **before** applying formatting.
- [ ] Review `CLAUDE.md`: commands correct? Undo decisions added?
- [ ] Merge with **Prompt G**, then tell Partner B to `git pull team main`

### 2.2 Partner A: merge the supplied branches
**Prompt A**
- [ ] Use promotion-setup in the browser, then promote, and check the captured pieces list
- [ ] Standard checks → commit, then push `main`
- [ ] If formatting was postponed: run `ruff format .` now, commit, push, and tell your partner

### 2.3 Partner B: undo (starts at the same time as 2.1)
`git switch main`, `git pull team main`, then **Prompt Undo**
- [ ] Browser tests: undo right after your move (inside the 500 ms), undo after the computer replies, undo after checkmate, undo on a new game
- [ ] Standard checks → commit, then `git push team feature/undo`
- [ ] Partner A reviews it (**Prompt F**), then merge (**Prompt G**)

### 2.4 Partner A: redo (after undo is in main)
**Prompt B**
- [ ] Browser tests: undo, then redo, gives the same board; a new move after undo makes redo disabled
- [ ] Standard checks → review (F) → merge (G)

### 2.5 Extra features (one each, in parallel)
- Partner B: **Prompt C** (castling)
- Partner A: **Prompt D** (en passant)
- Optional, if there's time: **Prompt E** (draw rules)
- [ ] Each one: browser test, standard checks, partner review (F), merge (G)
- [ ] **After the second merge:** run all tests, and play a game that uses undo + castling + en passant + promotion

## 3. Phase 3: Review and submit (last 20 min)

- [ ] **Prompt H** on `main`: final checks, CLAUDE.md up to date, commit, push
- [ ] Download `SKILL.md` into `.claude/skills/lab05-review/SKILL.md`. **Do not commit it.**
- [ ] Start a **fresh** session (`claude`, not `--continue`) and run `/lab05-review`
- [ ] While it runs, prepare for the discussion:
  - Practices you used: tests per feature, tests for features together, lint, format, types, CLAUDE.md
  - What the agent did without being asked
  - What you skipped and why
  - What to do better next time
- [ ] Read `lab05-review.md`, pick one claim, and check it against the code
- [ ] **Both partners** upload `lab05-review.md` to "Lab 5 report" on Moodle before the session ends

---

## Prompts

### Prompt 1: Checks setup
```text
On a new branch setup/checks (from main): add code-quality checks to this project.
- Add ruff and mypy to requirements-dev.txt and install them in .venv.
- Configure both in pyproject.toml (ruff: lint + format, sensible rule set; mypy: check the
  project's .py files, ignore .venv).
- Run ruff check, ruff format --check, and mypy; report what they find, fix lint/type issues
  without changing behaviour. Show me the ruff format diff size before applying formatting.
- Create CLAUDE.md with: how to activate .venv on Windows PowerShell, the exact check
  commands (python -m pytest, ruff check ., ruff format --check ., mypy .), the rule that
  all checks must pass before a task is called done, that every feature needs its own tests,
  and our undo decisions: against the computer one undo removes the computer's reply and the
  human's move; before the computer replies it removes only the human's move; undo at the
  start is an error; undo after checkmate/stalemate is allowed; a new game clears history.
- Run all checks and pytest at the end; all must pass. Do not commit.
```

### Prompt A: Merge the supplied branches
```text
Look at the branches origin/feature/captured-pieces and origin/feature/promotion.
For each one, explain briefly what it adds and which files it changes.
Then merge them into main one at a time. If there are conflicts, explain each one to me
and ask before choosing. After each merge run python -m pytest.
Then add tests in tests/test_integration.py for the features working together, e.g.
a promotion that also captures a piece shows up correctly in the captured pieces list.
Also check: how does the computer opponent choose a promotion piece? It should work and be tested.
Run all checks from CLAUDE.md; all must pass. Don't push; show me a summary.
```

### Prompt Undo
```text
Implement an Undo feature for this chess game on a new branch called feature/undo
(create it from main). Read game.py, session.py, server.py and static/app.js first.

Approach: a stack of snapshots in Session.
- Before every move (human or computer), push a snapshot: copy_position(self.position)
  plus a copy of self.notation (or its length).
- Undo pops snapshots and restores them.
- Add an "undo" branch to Session.dispatch. Do not change the rules in game.py.
- Keep the design so redo can be added later as a second stack (don't implement redo now).

Behaviour (these are our decisions):
- Two-player mode: one undo takes back exactly one move.
- Against the computer: one undo takes back the computer's reply AND the human's move
  before it, so it is White's (the human's) turn again.
- Against the computer, if the human has moved but the computer has not replied yet:
  undo takes back only the human's move. The browser must then not send a late
  "computer-move" request (app.js waits 500 ms before asking the computer to move),
  so handle that race in the frontend: cancel or skip the pending computer reply
  instead of showing an error.
- Start of the game / nothing to undo: raise ValueError("Nothing to undo"),
  and disable the Undo button in the UI when there is nothing to undo.
- After checkmate or stalemate: undo is allowed, and the game is no longer over
  (status/winner must reflect the restored position).
- Starting a new game ("new") or "promotion-setup" clears the undo history.
  After promotion-setup, undo may step back through the setup moves.
- view() should include a field such as "can_undo" so the UI knows when to enable the button.

UI: add an "Undo" button next to the existing new-game buttons in static/index.html,
wired up in static/app.js like the other data-action buttons.

Tests: add tests/test_undo.py using pytest, testing through Session.dispatch. Cover at least:
- undo at the very start raises an error and changes nothing
- one undo in two-player mode restores the exact previous board, turn and move list
- several undos in a row back to the start position, then one more fails
- undo of a capture brings the captured piece back
- against the computer: undo after the computer replied removes both moves
- against the computer: undo before the computer replied removes only the human's move,
  and a following "computer-move" is rejected cleanly
- undo after checkmate (e.g. fool's mate) clears checkmate and the winner
- "new" clears the undo history
- after undo, a new move works normally and can itself be undone
For the computer tests, make the computer's choice deterministic (pass or patch the rng).

When done: run all checks from CLAUDE.md and make sure everything passes (old and new tests),
then show me a short summary of what you changed and anything you were unsure about.
Do not commit; I will review first.
```

### Prompt B: Redo
```text
On a new branch feature/redo from main: add Redo, building on the existing undo snapshot stack.
Rules: redo re-applies exactly what the last undo took back (against the computer, an undo of
two moves is redone as two moves). Any new move or new game clears the redo history.
Nothing to redo -> ValueError("Nothing to redo") and the Redo button is disabled
(add "can_redo" to view()). Add a Redo button in the UI next to Undo.
Tests in tests/test_redo.py: redo after undo restores board/turn/moves exactly; undo-redo-undo
chains; redo is cleared after a new move; redo against the computer; redo with nothing to redo.
Run all checks from CLAUDE.md; all must pass. Don't commit.
```

### Prompt C: Castling
```text
On a new branch feature/castling from main: add castling (king side and queen side) to game.py.
Standard rules: king and that rook have never moved, squares between are empty, the king is not
in check, and does not pass through or land on an attacked square. Store whatever extra state
is needed (e.g. castling rights) so that copy_position, undo/redo snapshots and the computer
opponent keep working. The move label should be readable (e.g. O-O / O-O-O or e1-g1).
Tests in tests/test_castling.py: both sides for both colours; each illegal case
(moved king, moved rook, piece in between, in check, passing through check);
castling then undo restores king, rook and rights. Run all checks; all must pass. Don't commit.
```

### Prompt D: En passant
```text
On a new branch feature/en-passant from main: add en passant capture to game.py.
It is only allowed on the move immediately after the opponent's two-square pawn move.
Store the needed state (e.g. the en passant target square) in the position so copy_position,
undo/redo and the computer keep working. The captured pawn must be removed from the board
(and appear in captured pieces if that feature is merged).
Tests in tests/test_en_passant.py: capture works for both colours; not allowed one move later;
not allowed after a one-square pawn move; not allowed if it would leave own king in check;
undo after en passant restores the captured pawn. Run all checks; all must pass. Don't commit.
```

### Prompt E: Draw rules (optional)
```text
On a new branch feature/draws from main: add the missing draw conditions. Stalemate already ends
the game in a tie; add threefold repetition (use the position snapshots from undo), the
fifty-move rule, and insufficient material (K vs K, K+B vs K, K+N vs K). The game should end
as a draw with the reason shown in the UI, and moves after it should be rejected.
Tests for each rule, and that undo after a draw makes the game continue.
Run all checks; all must pass. Don't commit.
```

### Prompt F: Review your partner's branch
```text
Fetch team and review the branch team/<branch-name> against main. Check: does it do what
it claims, are the tests meaningful (do they assert the actual board/turn/moves), are edge
cases missing, does it break other features? Run all checks on it. List problems by severity.
Don't change any files.
```

### Prompt G: Merge a finished feature
```text
Commit the current work on <branch> with a clear message if it is not committed yet.
Then merge <branch> into main: first pull team/main, then merge, explain each conflict to me
before resolving it, run all checks from CLAUDE.md, and if everything passes push main to team.
```

### Prompt H: Before the final review
```text
Run all checks from CLAUDE.md on main and fix anything failing. Make sure every feature has its
own tests and there are tests for features together. Make sure CLAUDE.md is up to date with the
check commands and our design decisions (e.g. how undo works against the computer). Show me
what you changed, then commit on main and push to team.
```
