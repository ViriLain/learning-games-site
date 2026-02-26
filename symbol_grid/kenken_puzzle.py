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


def partition_into_cages(
    size: int, max_cage_size: int
) -> list[list[tuple[int, int]]]:
    """Partition an NxN grid into connected cages of random sizes."""
    cells = [(r, c) for r in range(size) for c in range(size)]
    random.shuffle(cells)

    assigned: set[tuple[int, int]] = set()
    cages: list[list[tuple[int, int]]] = []

    for cell in cells:
        if cell in assigned:
            continue
        # Grow a cage from this cell
        cage_size = random.randint(1, max_cage_size)
        cage = [cell]
        assigned.add(cell)

        while len(cage) < cage_size:
            # Find unassigned neighbors of current cage
            neighbors: set[tuple[int, int]] = set()
            for r, c in cage:
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nb = (r + dr, c + dc)
                    if (
                        0 <= nb[0] < size
                        and 0 <= nb[1] < size
                        and nb not in assigned
                    ):
                        neighbors.add(nb)
            if not neighbors:
                break
            chosen = random.choice(list(neighbors))
            cage.append(chosen)
            assigned.add(chosen)

        cages.append(cage)

    return cages


def assign_cage_operations(
    grid: list[list[int]],
    cage_cells_list: list[list[tuple[int, int]]],
    allowed_operations: list[str],
) -> list[Cage]:
    """Assign an operation and compute the target for each cage."""
    cages = []
    for cells in cage_cells_list:
        values = [grid[r][c] for r, c in cells]

        if len(cells) == 1:
            cages.append(Cage(cells=tuple(cells), target=values[0], operation=""))
            continue

        operation, target = _pick_operation(values, cells, allowed_operations)
        cages.append(Cage(cells=tuple(cells), target=target, operation=operation))

    return cages


def _pick_operation(
    values: list[int],
    cells: list[tuple[int, int]],
    allowed_operations: list[str],
) -> tuple[str, int]:
    """Pick a valid operation for a cage and compute its target."""
    # For 3+ cell cages, only + and × are valid
    if len(values) > 2:
        ops = [op for op in allowed_operations if op in ("+", "×")]
        if not ops:
            ops = ["+"]
    else:
        ops = list(allowed_operations)

    random.shuffle(ops)

    for op in ops:
        result = _try_operation(op, values)
        if result is not None:
            return op, result

    # Fallback: addition always works
    return "+", sum(values)


def _try_operation(op: str, values: list[int]) -> int | None:
    """Try to apply an operation. Returns target or None if invalid."""
    if op == "+":
        return sum(values)
    elif op == "×":
        result = 1
        for v in values:
            result *= v
        return result
    elif op == "-":
        if len(values) != 2:
            return None
        return abs(values[0] - values[1])
    elif op == "÷":
        if len(values) != 2:
            return None
        big, small = max(values), min(values)
        if small == 0 or big % small != 0:
            return None
        return big // small
    return None
