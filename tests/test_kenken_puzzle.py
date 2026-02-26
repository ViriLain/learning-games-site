import pytest

from symbol_grid.kenken_puzzle import (
    generate_latin_square,
    partition_into_cages,
    assign_cage_operations,
    Cage,
)


class TestGenerateLatinSquare:
    @pytest.mark.parametrize("size", [3, 4, 5, 6])
    def test_correct_dimensions(self, size):
        grid = generate_latin_square(size)
        assert len(grid) == size
        assert all(len(row) == size for row in grid)

    @pytest.mark.parametrize("size", [3, 4, 5, 6])
    def test_rows_are_permutations(self, size):
        grid = generate_latin_square(size)
        expected = set(range(1, size + 1))
        for row in grid:
            assert set(row) == expected

    @pytest.mark.parametrize("size", [3, 4, 5, 6])
    def test_columns_are_permutations(self, size):
        grid = generate_latin_square(size)
        expected = set(range(1, size + 1))
        for c in range(size):
            col = [grid[r][c] for r in range(size)]
            assert set(col) == expected


class TestPartitionIntoCages:
    def test_all_cells_covered(self):
        cells = partition_into_cages(4, max_cage_size=3)
        all_cells = set()
        for cage_cells in cells:
            all_cells.update(cage_cells)
        expected = {(r, c) for r in range(4) for c in range(4)}
        assert all_cells == expected

    def test_no_overlapping_cells(self):
        cells = partition_into_cages(5, max_cage_size=4)
        all_cells = []
        for cage_cells in cells:
            all_cells.extend(cage_cells)
        assert len(all_cells) == len(set(all_cells))

    def test_cages_respect_max_size(self):
        for max_size in [2, 3, 4]:
            cells = partition_into_cages(5, max_cage_size=max_size)
            for cage_cells in cells:
                assert len(cage_cells) <= max_size

    def test_cages_are_connected(self):
        """Each cage's cells must be orthogonally connected."""
        cells = partition_into_cages(5, max_cage_size=4)
        for cage_cells in cells:
            if len(cage_cells) <= 1:
                continue
            cell_set = set(cage_cells)
            # BFS from first cell
            visited = {cage_cells[0]}
            queue = [cage_cells[0]]
            while queue:
                r, c = queue.pop()
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nb = (r + dr, c + dc)
                    if nb in cell_set and nb not in visited:
                        visited.add(nb)
                        queue.append(nb)
            assert visited == cell_set

    def test_at_least_some_multi_cell_cages(self):
        cells = partition_into_cages(4, max_cage_size=3)
        multi = [c for c in cells if len(c) > 1]
        assert len(multi) > 0


class TestAssignCageOperations:
    def _make_grid(self):
        """Fixed 3x3 Latin square for deterministic tests."""
        return [
            [1, 2, 3],
            [2, 3, 1],
            [3, 1, 2],
        ]

    def test_single_cell_cage_has_no_operation(self):
        grid = self._make_grid()
        cage_cells = [[(0, 0)]]
        cages = assign_cage_operations(grid, cage_cells, ["+"])
        assert cages[0].operation == ""
        assert cages[0].target == 1  # grid[0][0]

    def test_two_cell_addition(self):
        grid = self._make_grid()
        cage_cells = [[(0, 0), (0, 1)]]
        cages = assign_cage_operations(grid, cage_cells, ["+"])
        assert cages[0].operation == "+"
        assert cages[0].target == 3  # 1 + 2

    def test_two_cell_subtraction(self):
        grid = self._make_grid()
        cage_cells = [[(0, 0), (0, 1)]]
        cages = assign_cage_operations(grid, cage_cells, ["-"])
        assert cages[0].operation == "-"
        assert cages[0].target == 1  # |1 - 2| = 1

    def test_two_cell_multiplication(self):
        grid = self._make_grid()
        cage_cells = [[(0, 0), (0, 1)]]
        cages = assign_cage_operations(grid, cage_cells, ["×"])
        assert cages[0].operation == "×"
        assert cages[0].target == 2  # 1 * 2

    def test_two_cell_division(self):
        grid = self._make_grid()
        # cells (0,0)=1 and (0,1)=2 — 2/1 = 2, valid
        cage_cells = [[(0, 0), (0, 1)]]
        cages = assign_cage_operations(grid, cage_cells, ["÷"])
        assert cages[0].operation == "÷"
        assert cages[0].target == 2  # 2 / 1

    def test_three_cell_cage_only_plus_or_times(self):
        grid = self._make_grid()
        cage_cells = [[(0, 0), (0, 1), (0, 2)]]
        cages = assign_cage_operations(grid, cage_cells, ["+", "-", "×", "÷"])
        assert cages[0].operation in ("+", "×")

    def test_division_falls_back_when_not_divisible(self):
        grid = [[2, 3], [3, 2]]
        cage_cells = [[(0, 0), (0, 1)]]  # values 2, 3 — not evenly divisible
        # Only allow ÷; should fall back to another operation
        cages = assign_cage_operations(grid, cage_cells, ["÷"])
        assert cages[0].operation in ("+", "-", "×")

    def test_cage_cells_preserved(self):
        grid = self._make_grid()
        cage_cells = [[(1, 0), (1, 1)]]
        cages = assign_cage_operations(grid, cage_cells, ["+"])
        assert set(cages[0].cells) == {(1, 0), (1, 1)}
