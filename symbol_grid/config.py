from dataclasses import dataclass


# --- Symbols & Colors ---

SYMBOLS = ["★", "♦", "♠", "♣", "♥", "▲", "●", "■", "◆", "✦", "⊕", "⊗"]

SYMBOL_CSS_COLORS = [
    "#ffd700",  # gold
    "#dc3232",  # red
    "#1e64c8",  # blue
    "#32b432",  # green
    "#dc50b4",  # pink
    "#ff8c00",  # orange
    "#783cc8",  # purple
    "#00b4b4",  # teal
    "#b4783c",  # brown
    "#64c8ff",  # sky blue
    "#c8c832",  # yellow-green
    "#a0a0a0",  # silver
]


# --- Difficulty ---

@dataclass(frozen=True)
class DifficultyPreset:
    name: str
    grid_size: int
    num_symbols: int
    value_min: int
    value_max: int
    hint_fraction: float
    distinct_values: bool


PRESETS = {
    "Easy": DifficultyPreset("Easy", 3, 3, 1, 5, 1.0, True),
    "Medium": DifficultyPreset("Medium", 4, 4, 1, 10, 0.75, True),
    "Hard": DifficultyPreset("Hard", 5, 6, 1, 15, 0.6, False),
    "Expert": DifficultyPreset("Expert", 5, 7, 1, 20, 0.0, False),
}

PRESET_ORDER = ["Easy", "Medium", "Hard", "Expert"]

PRESET_DESCRIPTIONS = {
    "Easy": "3×3 grid, 3 symbols, all hints shown",
    "Medium": "4×4 grid, 4 symbols, 75% of hints",
    "Hard": "5×5 grid, 6 symbols, 60% of hints, values may repeat",
    "Expert": "5×5 grid, 7 symbols, minimal hints, values may repeat",
}
