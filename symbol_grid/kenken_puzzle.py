from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class Cage:
    cells: tuple[tuple[int, int], ...]  # (row, col) positions
    target: int
    operation: str  # "+", "-", "×", "÷", or "" for single-cell


@dataclass(frozen=True)
class KenKenPuzzle:
    size: int
    solution: list[list[int]]
    cages: list[Cage]


class KenKenGenerationError(Exception):
    pass


def generate_latin_square(size: int) -> list[list[int]]:
    """Generate a random Latin square of given size.

    Uses row-by-row generation with backtracking.
    Values are 1..size.
    """
    grid: list[list[int]] = []
    values = list(range(1, size + 1))

    def _fill(row: int) -> bool:
        if row == size:
            return True
        candidates = values[:]
        random.shuffle(candidates)
        perm = _find_valid_row(grid, row, size, candidates)
        if perm is None:
            return False
        grid.append(perm)
        if _fill(row + 1):
            return True
        grid.pop()
        return False

    for _ in range(100):
        grid.clear()
        if _fill(0):
            return grid

    raise KenKenGenerationError("Failed to generate Latin square")


def _find_valid_row(
    grid: list[list[int]], row: int, size: int, values: list[int]
) -> list[int] | None:
    """Find a valid permutation for the given row via backtracking."""
    used_in_col: list[set[int]] = [
        {grid[r][c] for r in range(row)} for c in range(size)
    ]
    result: list[int] = []
    used_in_row: set[int] = set()

    def _bt(col: int) -> bool:
        if col == size:
            return True
        for v in values:
            if v in used_in_row or v in used_in_col[col]:
                continue
            result.append(v)
            used_in_row.add(v)
            used_in_col[col].add(v)
            if _bt(col + 1):
                return True
            result.pop()
            used_in_row.discard(v)
            used_in_col[col].discard(v)
        return False

    if _bt(0):
        return result
    return None
