# symbol_grid/kenken_config.py
from dataclasses import dataclass


@dataclass(frozen=True)
class KenKenPreset:
    name: str
    grid_size: int
    max_cage_size: int
    operations: tuple[str, ...]


KENKEN_PRESETS = {
    "Easy": KenKenPreset("Easy", 3, 2, ("+",)),
    "Medium": KenKenPreset("Medium", 4, 3, ("+", "-")),
    "Hard": KenKenPreset("Hard", 5, 4, ("+", "-", "×")),
    "Expert": KenKenPreset("Expert", 6, 4, ("+", "-", "×", "÷")),
}

KENKEN_PRESET_ORDER = ["Easy", "Medium", "Hard", "Expert"]

KENKEN_PRESET_DESCRIPTIONS = {
    "Easy": "3×3 grid, addition only, small cages",
    "Medium": "4×4 grid, addition & subtraction",
    "Hard": "5×5 grid, add/subtract/multiply, larger cages",
    "Expert": "6×6 grid, all four operations",
}
