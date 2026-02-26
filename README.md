# Puzzle Worksheets

A Flask web app that generates printable math puzzle worksheets. Two puzzle types:

**Symbol Grid** — A grid filled with symbols (★, ♦, ♠, etc.), each mapped to a hidden numeric value. Row and column sum hints let the player deduce each symbol's value.

**KenKen** — Fill an NxN grid with numbers 1..N so each row and column contains every number exactly once. Cages group adjacent cells with an arithmetic clue (e.g., "12+", "2÷").

Both puzzle types support four difficulty presets (Easy through Expert), 1/2/4 puzzles per page, and optional answer keys.

## Setup

Requires Python 3.11+.

```bash
pip install -e ".[dev]"
```

## Usage

```bash
python3 -m symbol_grid.app
```

Open `http://localhost:8080`. Pick a puzzle type, choose a difficulty, and print the worksheet.

Use `-p` to change the port:

```bash
python3 -m symbol_grid.app -p 5000
```

## Tests

```bash
pytest
```

## How It Works

### Symbol Grid

Generates a random grid of symbols, assigns each symbol a numeric value, then builds a system of linear equations from row/column sums. A greedy algorithm selects a solvable subset of hints ensuring the coefficient matrix has full rank (unique solution). Uses numpy for linear algebra.

### KenKen

Generates a random Latin square, partitions it into connected cages, assigns arithmetic operations (+, −, ×, ÷) with computed targets, then validates uniqueness via a constraint-propagation backtracking solver. Retries if the puzzle has multiple solutions. Pure Python — no numpy.

### Difficulty

| Preset | Symbol Grid | KenKen |
|--------|------------|--------|
| Easy | 3×3, 3 symbols, all hints | 3×3, addition only, small cages |
| Medium | 4×4, 4 symbols, 75% hints | 4×4, addition & subtraction |
| Hard | 5×5, 6 symbols, 60% hints | 5×5, add/subtract/multiply, larger cages |
| Expert | 5×5, 7 symbols, minimal hints | 6×6, all four operations |
