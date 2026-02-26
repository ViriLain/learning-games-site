import pytest

from symbol_grid.app import app
from symbol_grid.config import PRESET_ORDER


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


class TestIndex:
    def test_returns_200(self, client):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_contains_preset_buttons(self, client):
        resp = client.get("/")
        html = resp.data.decode()
        for name in PRESET_ORDER:
            assert f'value="{name}"' in html


class TestGenerate:
    def test_preset_easy(self, client):
        resp = client.post("/generate", data={"preset": "Easy", "count": "1"})
        assert resp.status_code == 200
        html = resp.data.decode()
        assert "Puzzle 1" in html
        assert "puzzle-block" in html

    def test_preset_with_answers(self, client):
        resp = client.post(
            "/generate",
            data={"preset": "Easy", "count": "1", "show_answers": "on"},
        )
        html = resp.data.decode()
        assert "Answer Key" in html

    def test_preset_without_answers(self, client):
        resp = client.post(
            "/generate", data={"preset": "Easy", "count": "1"}
        )
        html = resp.data.decode()
        assert "Answer Key" not in html

    def test_multiple_puzzles(self, client):
        resp = client.post("/generate", data={"preset": "Easy", "count": "4"})
        html = resp.data.decode()
        assert "Puzzle 1" in html
        assert "Puzzle 4" in html
        assert "count-4" in html

    def test_custom_params(self, client):
        resp = client.post(
            "/generate",
            data={
                "grid_size": "3",
                "num_symbols": "3",
                "value_min": "1",
                "value_max": "5",
                "hint_fraction": "1.0",
                "distinct_values": "on",
                "count": "1",
            },
        )
        assert resp.status_code == 200
        assert b"Puzzle 1" in resp.data

    def test_invalid_count(self, client):
        resp = client.post(
            "/generate", data={"preset": "Easy", "count": "3"}
        )
        html = resp.data.decode()
        assert "Puzzle count must be 1, 2, or 4" in html

    def test_invalid_custom_params(self, client):
        resp = client.post(
            "/generate",
            data={
                "grid_size": "abc",
                "num_symbols": "3",
                "value_min": "1",
                "value_max": "5",
                "hint_fraction": "1.0",
                "count": "1",
            },
        )
        html = resp.data.decode()
        assert "Invalid parameter" in html

    def test_validation_error_from_generator(self, client):
        resp = client.post(
            "/generate",
            data={
                "grid_size": "3",
                "num_symbols": "1",
                "value_min": "1",
                "value_max": "5",
                "hint_fraction": "1.0",
                "count": "1",
            },
        )
        html = resp.data.decode()
        assert "num_symbols must be" in html

    @pytest.mark.parametrize("preset", PRESET_ORDER)
    def test_all_presets_generate(self, client, preset):
        resp = client.post(
            "/generate", data={"preset": preset, "count": "1"}
        )
        assert resp.status_code == 200
        assert b"Puzzle 1" in resp.data

    def test_grid_contains_symbols(self, client):
        resp = client.post("/generate", data={"preset": "Easy", "count": "1"})
        html = resp.data.decode()
        # Easy uses 3 symbols — at least one of the first 3 Unicode symbols should appear
        from symbol_grid.config import SYMBOLS

        found = any(s in html for s in SYMBOLS[:3])
        assert found

    def test_hints_rendered(self, client):
        resp = client.post("/generate", data={"preset": "Easy", "count": "1"})
        html = resp.data.decode()
        assert "row-hint" in html
        assert "col-hint" in html
