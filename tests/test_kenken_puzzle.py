import pytest

from symbol_grid.kenken_puzzle import generate_latin_square


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
