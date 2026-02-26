import numpy as np
import pytest

from symbol_grid.puzzle import (
    Puzzle,
    PuzzleGenerationError,
    _build_coefficient_matrix,
    _has_full_rank,
    generate_puzzle,
    validate_params,
)


class TestValidateParams:
    def test_too_few_symbols(self):
        with pytest.raises(ValueError, match="num_symbols must be >= 2"):
            validate_params(3, 1, 1, 5, 1.0, True)

    def test_too_many_symbols_for_equations(self):
        with pytest.raises(ValueError, match="exceeds max equations"):
            validate_params(3, 7, 1, 10, 1.0, True)

    def test_too_many_symbols_for_grid(self):
        # grid_size=1: 2 symbols > 1 cell, but 2 <= 2*1 equations
        with pytest.raises(ValueError, match="exceeds grid cells"):
            validate_params(1, 2, 1, 10, 1.0, True)

    def test_value_range_too_small(self):
        with pytest.raises(ValueError, match="at least 2 values"):
            validate_params(3, 2, 5, 5, 1.0, True)

    def test_distinct_values_range_too_small(self):
        with pytest.raises(ValueError, match="too small"):
            validate_params(3, 3, 1, 2, 1.0, True)

    def test_bad_hint_fraction(self):
        with pytest.raises(ValueError, match="hint_fraction"):
            validate_params(3, 3, 1, 5, 1.5, True)

    def test_valid_params(self):
        validate_params(3, 3, 1, 5, 1.0, True)  # should not raise


class TestGeneratePuzzle:
    @pytest.mark.parametrize(
        "grid_size,num_symbols,vmin,vmax,hint_frac,distinct",
        [
            (3, 3, 1, 5, 1.0, True),    # Easy
            (4, 4, 1, 10, 0.75, True),   # Medium
            (5, 6, 1, 15, 0.6, False),   # Hard
            (5, 7, 1, 20, 0.0, False),   # Expert (minimal hints)
            (3, 2, 1, 5, 1.0, True),     # Minimal symbols
        ],
    )
    def test_generates_valid_puzzle(
        self, grid_size, num_symbols, vmin, vmax, hint_frac, distinct
    ):
        puzzle = generate_puzzle(grid_size, num_symbols, vmin, vmax, hint_frac, distinct)

        assert puzzle.grid_size == grid_size
        assert puzzle.num_symbols == num_symbols
        assert len(puzzle.grid) == grid_size
        assert all(len(row) == grid_size for row in puzzle.grid)

    def test_all_symbols_appear(self):
        puzzle = generate_puzzle(4, 4, 1, 10, 1.0, True)
        flat = [cell for row in puzzle.grid for cell in row]
        for sym in range(puzzle.num_symbols):
            assert sym in flat, f"Symbol {sym} not in grid"

    def test_values_in_range(self):
        puzzle = generate_puzzle(3, 3, 1, 5, 1.0, True)
        for v in puzzle.symbol_values:
            assert 1 <= v <= 5

    def test_distinct_values_unique(self):
        puzzle = generate_puzzle(3, 3, 1, 10, 1.0, True)
        assert len(set(puzzle.symbol_values)) == puzzle.num_symbols

    def test_hints_are_correct_sums(self):
        puzzle = generate_puzzle(4, 4, 1, 10, 1.0, True)
        for hint in puzzle.hints:
            if hint.axis == "row":
                row = puzzle.grid[hint.index]
                expected = sum(puzzle.symbol_values[s] for s in row)
            else:
                expected = sum(
                    puzzle.symbol_values[puzzle.grid[r][hint.index]]
                    for r in range(puzzle.grid_size)
                )
            assert hint.total == expected, (
                f"{hint.axis} {hint.index}: expected {expected}, got {hint.total}"
            )

    def test_solvable_with_hints(self):
        """The hint subset must have sufficient rank to determine all symbol values."""
        puzzle = generate_puzzle(4, 4, 1, 10, 0.75, True)
        full_matrix = _build_coefficient_matrix(puzzle.grid, puzzle.num_symbols)

        # Build index set of revealed hints
        hint_indices = []
        for hint in puzzle.hints:
            if hint.axis == "row":
                hint_indices.append(hint.index)
            else:
                hint_indices.append(puzzle.grid_size + hint.index)

        sub_matrix = full_matrix[hint_indices]
        assert _has_full_rank(sub_matrix, puzzle.num_symbols)

    def test_minimal_hints_still_solvable(self):
        puzzle = generate_puzzle(5, 7, 1, 20, 0.0, False)
        full_matrix = _build_coefficient_matrix(puzzle.grid, puzzle.num_symbols)

        hint_indices = []
        for hint in puzzle.hints:
            if hint.axis == "row":
                hint_indices.append(hint.index)
            else:
                hint_indices.append(puzzle.grid_size + hint.index)

        sub_matrix = full_matrix[hint_indices]
        assert _has_full_rank(sub_matrix, puzzle.num_symbols)
        # Minimal hints should be close to num_symbols
        assert len(puzzle.hints) <= puzzle.num_symbols + 2

    def test_all_hints_for_fraction_1(self):
        puzzle = generate_puzzle(3, 3, 1, 5, 1.0, True)
        assert len(puzzle.hints) == 2 * puzzle.grid_size


class TestCoefficientMatrix:
    def test_shape(self):
        grid = [[0, 1], [1, 0]]
        m = _build_coefficient_matrix(grid, 2)
        assert m.shape == (4, 2)

    def test_row_counts(self):
        grid = [[0, 0, 1], [1, 1, 0], [0, 1, 0]]
        m = _build_coefficient_matrix(grid, 2)
        # Row 0: sym0 appears 2x, sym1 appears 1x
        assert m[0, 0] == 2
        assert m[0, 1] == 1
