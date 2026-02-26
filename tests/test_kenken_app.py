import pytest

from symbol_grid.app import app
from symbol_grid.kenken_config import KENKEN_PRESET_ORDER


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


class TestKenKenIndex:
    def test_returns_200(self, client):
        resp = client.get("/kenken")
        assert resp.status_code == 200

    def test_contains_preset_buttons(self, client):
        html = client.get("/kenken").data.decode()
        for name in KENKEN_PRESET_ORDER:
            assert f'value="{name}"' in html


class TestKenKenGenerate:
    def test_preset_easy(self, client):
        resp = client.post("/kenken/generate", data={"preset": "Easy", "count": "1"})
        assert resp.status_code == 200
        html = resp.data.decode()
        assert "Puzzle 1" in html

    def test_preset_with_answers(self, client):
        resp = client.post(
            "/kenken/generate",
            data={"preset": "Easy", "count": "1", "show_answers": "on"},
        )
        html = resp.data.decode()
        assert "Answer Key" in html

    def test_preset_without_answers(self, client):
        resp = client.post(
            "/kenken/generate", data={"preset": "Easy", "count": "1"}
        )
        html = resp.data.decode()
        assert "Answer Key" not in html

    def test_multiple_puzzles(self, client):
        resp = client.post("/kenken/generate", data={"preset": "Easy", "count": "4"})
        html = resp.data.decode()
        assert "Puzzle 1" in html
        assert "Puzzle 4" in html
        assert "count-4" in html

    def test_invalid_count(self, client):
        resp = client.post(
            "/kenken/generate", data={"preset": "Easy", "count": "3"}
        )
        html = resp.data.decode()
        assert "Puzzle count must be 1, 2, or 4" in html

    @pytest.mark.parametrize("preset", KENKEN_PRESET_ORDER)
    def test_all_presets_generate(self, client, preset):
        resp = client.post(
            "/kenken/generate", data={"preset": preset, "count": "1"}
        )
        assert resp.status_code == 200
        assert b"Puzzle 1" in resp.data

    def test_grid_cells_rendered(self, client):
        resp = client.post("/kenken/generate", data={"preset": "Easy", "count": "1"})
        html = resp.data.decode()
        assert "kenken-cell" in html

    def test_cage_labels_rendered(self, client):
        resp = client.post("/kenken/generate", data={"preset": "Easy", "count": "1"})
        html = resp.data.decode()
        assert "cage-label" in html
