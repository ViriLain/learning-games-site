from flask import Flask, render_template, request

from symbol_grid.config import (
    PRESETS,
    PRESET_DESCRIPTIONS,
    PRESET_ORDER,
    SYMBOLS,
    SYMBOL_CSS_COLORS,
)
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


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Puzzle Worksheet server")
    parser.add_argument("-p", "--port", type=int, default=8080)
    args = parser.parse_args()
    app.run(debug=True, port=args.port)
