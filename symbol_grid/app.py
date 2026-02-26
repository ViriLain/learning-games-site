from flask import Flask, render_template, request

from symbol_grid.config import (
    PRESETS,
    PRESET_DESCRIPTIONS,
    PRESET_ORDER,
    SYMBOLS,
    SYMBOL_CSS_COLORS,
)
from symbol_grid.kenken_config import (
    KENKEN_PRESETS,
    KENKEN_PRESET_DESCRIPTIONS,
    KENKEN_PRESET_ORDER,
)
from symbol_grid.kenken_puzzle import generate_kenken
from symbol_grid.puzzle import Puzzle, generate_puzzle

app = Flask(__name__)


# --- Landing ---

@app.route("/")
def landing():
    return render_template("landing.html")


# --- Symbol Grid ---

@app.route("/symbol-grid")
def symbol_grid_index():
    return render_template(
        "index.html",
        presets=PRESETS,
        preset_order=PRESET_ORDER,
        preset_descriptions=PRESET_DESCRIPTIONS,
    )


def _parse_symbol_grid_params(form: dict) -> tuple[dict, str | None]:
    """Extract and validate Symbol Grid puzzle params from form data."""
    preset_name = form.get("preset")
    if preset_name and preset_name in PRESETS:
        p = PRESETS[preset_name]
        params = dict(
            grid_size=p.grid_size,
            num_symbols=p.num_symbols,
            value_min=p.value_min,
            value_max=p.value_max,
            hint_fraction=p.hint_fraction,
            distinct_values=p.distinct_values,
        )
    else:
        try:
            params = dict(
                grid_size=int(form["grid_size"]),
                num_symbols=int(form["num_symbols"]),
                value_min=int(form["value_min"]),
                value_max=int(form["value_max"]),
                hint_fraction=float(form["hint_fraction"]),
                distinct_values=form.get("distinct_values") == "on",
            )
        except (KeyError, ValueError) as e:
            return {}, f"Invalid parameter: {e}"

    try:
        count = int(form.get("count", 1))
    except ValueError:
        return {}, "Invalid puzzle count"
    if count not in (1, 2, 4):
        return {}, "Puzzle count must be 1, 2, or 4"

    params["count"] = count
    params["show_answers"] = form.get("show_answers") == "on"
    return params, None


def _build_hint_lookup(puzzle: Puzzle) -> dict:
    """Build dicts mapping index -> total for row and column hints."""
    row_hints = {}
    col_hints = {}
    for hint in puzzle.hints:
        if hint.axis == "row":
            row_hints[hint.index] = hint.total
        else:
            col_hints[hint.index] = hint.total
    return {"row": row_hints, "col": col_hints}


@app.route("/symbol-grid/generate", methods=["POST"])
def symbol_grid_generate():
    params, error = _parse_symbol_grid_params(request.form)
    if error:
        return render_template(
            "index.html",
            presets=PRESETS,
            preset_order=PRESET_ORDER,
            preset_descriptions=PRESET_DESCRIPTIONS,
            error=error,
        )

    count = params.pop("count")
    show_answers = params.pop("show_answers")

    try:
        puzzles = [generate_puzzle(**params) for _ in range(count)]
    except (ValueError, Exception) as e:
        return render_template(
            "index.html",
            presets=PRESETS,
            preset_order=PRESET_ORDER,
            preset_descriptions=PRESET_DESCRIPTIONS,
            error=str(e),
        )

    puzzle_data = []
    for puzzle in puzzles:
        puzzle_data.append(
            {
                "puzzle": puzzle,
                "hints": _build_hint_lookup(puzzle),
                "symbols": SYMBOLS[: puzzle.num_symbols],
                "colors": SYMBOL_CSS_COLORS[: puzzle.num_symbols],
            }
        )

    return render_template(
        "worksheet.html",
        puzzle_data=puzzle_data,
        count=count,
        show_answers=show_answers,
        symbols=SYMBOLS,
        colors=SYMBOL_CSS_COLORS,
    )


# --- KenKen ---


@app.route("/kenken")
def kenken_index():
    return render_template(
        "kenken_index.html",
        presets=KENKEN_PRESETS,
        preset_order=KENKEN_PRESET_ORDER,
        preset_descriptions=KENKEN_PRESET_DESCRIPTIONS,
    )


def _parse_kenken_params(form: dict) -> tuple[dict, str | None]:
    """Extract and validate KenKen puzzle params from form data."""
    preset_name = form.get("preset")
    if preset_name and preset_name in KENKEN_PRESETS:
        p = KENKEN_PRESETS[preset_name]
        params = dict(
            size=p.grid_size,
            max_cage_size=p.max_cage_size,
            allowed_operations=list(p.operations),
        )
    else:
        return {}, "Invalid preset"

    try:
        count = int(form.get("count", 1))
    except ValueError:
        return {}, "Invalid puzzle count"
    if count not in (1, 2, 4):
        return {}, "Puzzle count must be 1, 2, or 4"

    params["count"] = count
    params["show_answers"] = form.get("show_answers") == "on"
    return params, None


def _build_cage_borders(puzzle) -> list[list[set]]:
    """Compute cage border info for each cell.

    Returns a 2D list where each entry is a set of border sides
    ('top', 'right', 'bottom', 'left') that are cage boundaries.
    """
    size = puzzle.size
    cell_to_cage: dict[tuple[int, int], int] = {}
    for cage_idx, cage in enumerate(puzzle.cages):
        for cell in cage.cells:
            cell_to_cage[cell] = cage_idx

    borders: list[list[set]] = [[set() for _ in range(size)] for _ in range(size)]
    for r in range(size):
        for c in range(size):
            cage_id = cell_to_cage[(r, c)]
            if r == 0 or cell_to_cage[(r - 1, c)] != cage_id:
                borders[r][c].add("top")
            if r == size - 1 or cell_to_cage[(r + 1, c)] != cage_id:
                borders[r][c].add("bottom")
            if c == 0 or cell_to_cage[(r, c - 1)] != cage_id:
                borders[r][c].add("left")
            if c == size - 1 or cell_to_cage[(r, c + 1)] != cage_id:
                borders[r][c].add("right")
    return borders


def _build_cage_labels(puzzle) -> dict[tuple[int, int], str]:
    """Map top-left cell of each cage to its label string (e.g., '12+')."""
    labels: dict[tuple[int, int], str] = {}
    for cage in puzzle.cages:
        top_left = min(cage.cells, key=lambda c: (c[0], c[1]))
        if cage.operation:
            labels[top_left] = f"{cage.target}{cage.operation}"
        else:
            labels[top_left] = str(cage.target)
    return labels


@app.route("/kenken/generate", methods=["POST"])
def kenken_generate():
    params, error = _parse_kenken_params(request.form)
    if error:
        return render_template(
            "kenken_index.html",
            presets=KENKEN_PRESETS,
            preset_order=KENKEN_PRESET_ORDER,
            preset_descriptions=KENKEN_PRESET_DESCRIPTIONS,
            error=error,
        )

    count = params.pop("count")
    show_answers = params.pop("show_answers")

    try:
        puzzles = [generate_kenken(**params) for _ in range(count)]
    except (ValueError, Exception) as e:
        return render_template(
            "kenken_index.html",
            presets=KENKEN_PRESETS,
            preset_order=KENKEN_PRESET_ORDER,
            preset_descriptions=KENKEN_PRESET_DESCRIPTIONS,
            error=str(e),
        )

    puzzle_data = []
    for puzzle in puzzles:
        puzzle_data.append(
            {
                "puzzle": puzzle,
                "borders": _build_cage_borders(puzzle),
                "labels": _build_cage_labels(puzzle),
            }
        )

    return render_template(
        "kenken_worksheet.html",
        puzzle_data=puzzle_data,
        count=count,
        show_answers=show_answers,
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Puzzle Worksheet server")
    parser.add_argument("-p", "--port", type=int, default=8080)
    args = parser.parse_args()
    app.run(debug=True, port=args.port)
