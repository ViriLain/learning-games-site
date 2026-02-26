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

Puzzle Worksheets — a Flask web app that generates printable math puzzle worksheets. Two puzzle types:

- **Symbol Grid**: Players see a grid of symbols (★, ♦, ♠, etc.), each mapped to a hidden numeric value. Row/column sum hints let the player deduce each symbol's value.
- **KenKen**: Players fill an NxN grid with numbers 1..N (Latin square rules). Cages group adjacent cells with an arithmetic operation and target value as clues.

## Commands

```bash
# Run the dev server (default port 8080)
python -m symbol_grid.app            # or: python symbol_grid/app.py -p 5000

# Run all tests
pytest

# Run a single test file or test
pytest tests/test_puzzle.py
pytest tests/test_kenken_puzzle.py::TestGenerateKenKen::test_puzzle_is_uniquely_solvable

# Install (editable dev install with test deps)
pip install -e ".[dev]"
```

No formatter or linter is configured yet — flag this if making substantial changes.

## Architecture

All code lives under `symbol_grid/` (the package name predates KenKen — rename when a third puzzle type arrives).

### Routing (`app.py`)

| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Landing page — puzzle type picker |
| `/symbol-grid` | GET | Symbol Grid form |
| `/symbol-grid/generate` | POST | Generate Symbol Grid worksheet |
| `/kenken` | GET | KenKen form |
| `/kenken/generate` | POST | Generate KenKen worksheet |

### Symbol Grid

- **`puzzle.py`** — Pure logic. `generate_puzzle()` builds a random grid, assigns symbol values, constructs a coefficient matrix (numpy), and greedily selects a solvable subset of row/column sum hints. Key invariant: the hint subset's coefficient matrix must have rank ≥ `num_symbols`.
- **`config.py`** — Symbol characters, CSS colors, `DifficultyPreset` dataclass, four presets (Easy → Expert).

### KenKen

- **`kenken_puzzle.py`** — Pure logic. `generate_kenken()` orchestrates: (1) generate a random Latin square, (2) partition into connected cages, (3) assign operations and compute targets, (4) validate uniqueness via backtracking solver. Retries if not uniquely solvable.
- **`kenken_config.py`** — `KenKenPreset` dataclass, four presets controlling grid size (3-6), max cage size, and allowed operations.
- **Solver**: constraint-propagation + backtracking. Pure Python, no numpy. Used for uniqueness validation during generation.

### Templates & Static

Jinja2 templates in `symbol_grid/templates/`, one CSS file in `symbol_grid/static/`. KenKen cage borders are rendered via CSS classes (`cage-top`, `cage-right`, etc.) computed server-side by `_build_cage_borders()`.

## Key Concepts

- **Coefficient matrix** (Symbol Grid): `(2 * grid_size) × num_symbols` matrix. Full rank = uniquely solvable.
- **`hint_fraction`** (Symbol Grid): controls difficulty. `1.0` = all hints, `0.0` = minimal hints.
- **Latin square** (KenKen): NxN grid where each row and column contains 1..N exactly once.
- **Cage** (KenKen): connected group of cells with a target number and operation (+, −, ×, ÷). Single-cell cages show just the value. 3+ cell cages use only + or ×.
- **Puzzle counts**: 1, 2, or 4 puzzles per worksheet (both puzzle types).

## Testing

Tests use pytest with Flask's `test_client`. Test files:
- `test_puzzle.py` — Symbol Grid generation logic and coefficient matrix
- `test_app.py` — Landing page, Symbol Grid routes, presets, custom params, error handling
- `test_kenken_puzzle.py` — Latin square, cage partitioning, operation assignment, solver, full generation, config
- `test_kenken_app.py` — KenKen routes, presets, worksheet rendering

Tests are deterministic in assertion (random puzzles are validated structurally, not against fixed output).

## Dependencies

Python ≥ 3.11. Runtime: Flask ≥ 3.0, numpy ≥ 1.26. Dev: pytest ≥ 8.0. No lockfile exists.
