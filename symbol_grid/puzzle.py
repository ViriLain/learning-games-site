from __future__ import annotations

import random
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Hint:
    axis: str   # "row" or "col"
    index: int
    total: int


@dataclass(frozen=True)
class Puzzle:
    grid: list[list[int]]           # grid[row][col] = symbol index
    symbol_values: list[int]        # symbol_index -> numeric value
    hints: list[Hint]
    num_symbols: int
    value_min: int
    value_max: int

    @property
    def grid_size(self) -> int:
        return len(self.grid)


class PuzzleGenerationError(Exception):
    pass


def validate_params(
    grid_size: int,
    num_symbols: int,
    value_min: int,
    value_max: int,
    hint_fraction: float,
    distinct_values: bool,
) -> None:
    if num_symbols < 2:
        raise ValueError("num_symbols must be >= 2")
    if num_symbols > 2 * grid_size:
        raise ValueError(
            f"num_symbols ({num_symbols}) exceeds max equations (2 * {grid_size})"
        )
    if num_symbols > grid_size * grid_size:
        raise ValueError(
            f"num_symbols ({num_symbols}) exceeds grid cells ({grid_size * grid_size})"
        )
    value_range_size = value_max - value_min + 1
    if value_range_size < 2:
        raise ValueError("value range must contain at least 2 values")
    if distinct_values and value_range_size < num_symbols:
        raise ValueError(
            f"value range [{value_min}, {value_max}] too small for "
            f"{num_symbols} distinct values"
        )
    if not 0.0 <= hint_fraction <= 1.0:
        raise ValueError("hint_fraction must be in [0.0, 1.0]")


def _build_coefficient_matrix(
    grid: list[list[int]], num_symbols: int
) -> np.ndarray:
    """Build the coefficient matrix for all row and column sum equations.

    Each row of the matrix represents one equation (row-sum or col-sum).
    Each column represents a symbol. The entry is the count of that symbol
    in the corresponding row/column of the grid.
    """
    grid_size = len(grid)
    matrix = np.zeros((2 * grid_size, num_symbols), dtype=float)

    for r in range(grid_size):
        for c in range(grid_size):
            sym = grid[r][c]
            matrix[r][sym] += 1                    # row equations
            matrix[grid_size + c][sym] += 1        # col equations

    return matrix


def _has_full_rank(matrix: np.ndarray, num_symbols: int) -> bool:
    return int(np.linalg.matrix_rank(matrix)) >= num_symbols


def _select_hints(
    grid: list[list[int]],
    symbol_values: list[int],
    num_symbols: int,
    grid_size: int,
    hint_fraction: float,
) -> list[Hint]:
    """Select a subset of row/col sums as hints, ensuring solvability."""
    full_matrix = _build_coefficient_matrix(grid, num_symbols)

    # Compute all sums
    all_sums: list[tuple[str, int, int]] = []  # (axis, index, total)
    for r in range(grid_size):
        total = sum(symbol_values[grid[r][c]] for c in range(grid_size))
        all_sums.append(("row", r, total))
    for c in range(grid_size):
        total = sum(symbol_values[grid[r][c]] for r in range(grid_size))
        all_sums.append(("col", c, total))

    total_equations = len(all_sums)

    if hint_fraction >= 1.0:
        return [Hint(axis, idx, tot) for axis, idx, tot in all_sums]

    # Determine target hint count
    if hint_fraction <= 0.0:
        target = num_symbols  # minimal
    else:
        target = max(num_symbols, round(hint_fraction * total_equations))
    target = min(target, total_equations)

    # Greedily build a full-rank subset, then fill to target
    indices = list(range(total_equations))
    random.shuffle(indices)

    selected: list[int] = []
    remaining: list[int] = []

    # First pass: greedily pick equations to reach full rank
    for i in indices:
        candidate = selected + [i]
        sub_matrix = full_matrix[candidate]
        if int(np.linalg.matrix_rank(sub_matrix)) > len(selected):
            # This equation added rank — keep it
            selected.append(i)
            if len(selected) == num_symbols:
                break
        else:
            remaining.append(i)

    if not _has_full_rank(full_matrix[selected], num_symbols):
        # Shouldn't happen if grid was validated, but guard anyway
        raise PuzzleGenerationError("Could not find solvable hint subset")

    # Collect leftover indices not yet assigned
    used = set(selected)
    remaining = [i for i in indices if i not in used]
    random.shuffle(remaining)

    # Fill to target count
    while len(selected) < target and remaining:
        selected.append(remaining.pop())

    return [
        Hint(all_sums[i][0], all_sums[i][1], all_sums[i][2])
        for i in sorted(selected)
    ]


def generate_puzzle(
    grid_size: int,
    num_symbols: int,
    value_min: int,
    value_max: int,
    hint_fraction: float,
    distinct_values: bool,
    max_retries: int = 100,
) -> Puzzle:
    validate_params(
        grid_size, num_symbols, value_min, value_max, hint_fraction, distinct_values
    )

    value_pool = list(range(value_min, value_max + 1))
    cells = grid_size * grid_size

    for _ in range(max_retries):
        # 1. Pick symbol values
        if distinct_values:
            symbol_values = sorted(random.sample(value_pool, num_symbols))
        else:
            symbol_values = [random.choice(value_pool) for _ in range(num_symbols)]
            if len(set(symbol_values)) < 2:
                # Ensure at least 2 unique values
                while len(set(symbol_values)) < 2:
                    symbol_values[random.randrange(num_symbols)] = random.choice(
                        value_pool
                    )

        # 2. Fill grid — every symbol appears at least once
        flat = list(range(num_symbols))  # one of each
        flat += [random.randrange(num_symbols) for _ in range(cells - num_symbols)]
        random.shuffle(flat)
        grid = [flat[r * grid_size : (r + 1) * grid_size] for r in range(grid_size)]

        # 3. Check full coefficient matrix rank
        full_matrix = _build_coefficient_matrix(grid, num_symbols)
        if not _has_full_rank(full_matrix, num_symbols):
            continue

        # 4. Select hints
        hints = _select_hints(
            grid, symbol_values, num_symbols, grid_size, hint_fraction
        )

        return Puzzle(
            grid=grid,
            symbol_values=symbol_values,
            hints=hints,
            num_symbols=num_symbols,
            value_min=value_min,
            value_max=value_max,
        )

    raise PuzzleGenerationError(
        f"Failed to generate solvable puzzle after {max_retries} retries"
    )
