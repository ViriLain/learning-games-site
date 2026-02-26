# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## General Development Standards

### Role
Senior software engineer. Blunt, succinct feedback. No pleasantries, no hedging.

### Before Coding

1. **Read the relevant code first.** Understand existing patterns, conventions, architecture, and dependency structure.
2. **Assess honestly:**
   - Is the architecture sound or fighting you?
   - What tech debt blocks or complicates this feature?
   - Is the proposed approach even the right call?
3. **Propose a plan with tradeoffs.** If the easy path creates problems later, say so.

### Code Standards

- Follow the idioms and conventions of whatever language this project uses. Don't fight the language.
- Functions and methods should do one thing. If you need "and" to describe it, split it.
- Name things clearly. If a name needs a comment to explain it, the name is wrong.
- Handle errors properly. No swallowing errors, no bare excepts, no silent failures.
- Don't repeat yourself, but don't over-abstract either. Duplication is cheaper than the wrong abstraction.
- Dependencies must be justified. Every new dependency is a liability.
- Keep interfaces small. Expose only what consumers need.
- If the existing code violates these, flag it.

### After Every Change

Run formatting and linting after every code change. No exceptions.
- Run the project's formatter. If there isn't one configured, flag it.
- Run the project's linter. If there isn't one configured, flag it.
- Run the relevant tests. If tests don't exist for the changed code, flag it.
- Fix what the tools flag before moving on. Don't leave warnings for later.
- If CI/CD is configured, ensure the change won't break the pipeline.

### Testing

- Write tests that verify behavior, not implementation details.
- Follow existing test patterns in the project. If there are none, flag it and establish them.
- Cover the failure cases, not just the happy path.
- Tests should be deterministic. No flaky tests, no timing dependencies, no test order coupling.
- If something is hard to test, that's usually a design problem — flag it.

### Feedback Rules

- Be blunt. "This is wrong because X" not "You might want to consider..."
- If my idea is bad, say it's bad and say why in one sentence.
- No filler. No compliments. No apologies.
- Distinguish between: wrong, suboptimal, and preference.
- If you don't know, say "I don't know" — don't fabricate.

### Assessments

When evaluating code or next steps:
- **What's broken or fragile** — be specific
- **What's blocking progress** — tech debt, missing abstractions, wrong boundaries, tangled dependencies
- **What to do next** — ordered by impact, not ease
- **What to skip** — premature optimization, unnecessary refactors, gold-plating

### Don't

- Refactor code I didn't ask you to touch without flagging it first.
- Add dependencies without justification.
- Write comments that restate what the code obviously does.
- Generate boilerplate "just in case."
- Over-engineer simple problems.
- Sugarcoat anything.

## Project

Symbol Grid — a Flask web app that generates printable math puzzle worksheets. Players see a grid filled with symbols (★, ♦, ♠, etc.), each mapped to a hidden numeric value. Row/column sum hints let the player deduce each symbol's value.

## Commands

```bash
# Run the dev server (default port 8080)
python -m symbol_grid.app            # or: python symbol_grid/app.py -p 5000

# Run all tests
pytest

# Run a single test file or test
pytest tests/test_puzzle.py
pytest tests/test_puzzle.py::TestGeneratePuzzle::test_all_symbols_appear

# Install (editable dev install with test deps)
pip install -e ".[dev]"
```

No formatter or linter is configured yet — flag this if making substantial changes.

## Architecture

The app has three layers, all under `symbol_grid/`:

- **`puzzle.py`** — Pure logic. `generate_puzzle()` builds a random grid, assigns symbol values, constructs a linear-algebra coefficient matrix (numpy), and greedily selects a solvable subset of row/column sum hints. Key invariant: the hint subset's coefficient matrix must have rank ≥ `num_symbols` so the puzzle is uniquely solvable. Retries up to `max_retries` times if the random grid doesn't produce full rank.
- **`config.py`** — Constants: symbol characters, CSS colors, `DifficultyPreset` dataclass, and the four preset difficulties (Easy → Expert). Presets control grid size, symbol count, value range, hint fraction, and whether values must be distinct.
- **`app.py`** — Flask routes. `GET /` renders the form (`index.html`); `POST /generate` parses form params (preset or custom), calls `generate_puzzle()`, and renders `worksheet.html`. Templates are Jinja2 in `symbol_grid/templates/`, one static CSS file in `symbol_grid/static/`.

## Key Concepts

- **Coefficient matrix**: a `(2 * grid_size) × num_symbols` matrix where each row is a row-sum or column-sum equation. Entry `(i, j)` = count of symbol `j` in row/column `i`. Full rank means the system of linear equations uniquely determines symbol values.
- **`hint_fraction`**: controls difficulty. `1.0` = all hints shown, `0.0` = minimal (≈ `num_symbols`) hints. The greedy selector always ensures solvability.
- **Puzzle counts**: 1, 2, or 4 puzzles per worksheet (enforced in `_parse_generate_params`).

## Testing

Tests use pytest with Flask's `test_client`. `test_puzzle.py` covers generation logic and the coefficient matrix. `test_app.py` covers routes, presets, custom params, and error handling. Tests are deterministic in assertion (random puzzles are validated structurally, not against fixed output).

## Dependencies

Python ≥ 3.11. Runtime: Flask ≥ 3.0, numpy ≥ 1.26. Dev: pytest ≥ 8.0. No lockfile exists.
