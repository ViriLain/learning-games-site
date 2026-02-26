import pytest

from symbol_grid.kenken_puzzle import generate_latin_square, partition_into_cages


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
