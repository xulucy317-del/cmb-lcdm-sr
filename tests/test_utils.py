"""Shared utility regression tests."""
import json

import numpy as np

from cmb_lcdm_sr.utils import save_json, save_text


def test_save_json_maps_nested_nonfinite_numbers_to_null(tmp_path):
    path = tmp_path / "report.json"
    save_json({
        "finite": np.float32(1.25),
        "invalid": [float("nan"), np.float64("inf"), -float("inf")],
        "array": np.array([2.0, np.nan]),
        "count": np.int64(3),
    }, path)

    text = path.read_text()
    assert "NaN" not in text and "Infinity" not in text
    payload = json.loads(
        text,
        parse_constant=lambda token: (_ for _ in ()).throw(
            AssertionError(f"non-standard JSON constant: {token}")),
    )
    assert payload == {
        "finite": 1.25,
        "invalid": [None, None, None],
        "array": [2.0, None],
        "count": 3,
    }
    assert not list(tmp_path.glob(".report.json.*.tmp"))


def test_save_json_replaces_existing_file_atomically(tmp_path):
    path = tmp_path / "report.json"
    path.write_text('{"old": true}\n')
    save_json({"new": np.float64(2.0)}, path)
    assert json.loads(path.read_text()) == {"new": 2.0}
    assert not list(tmp_path.glob(".report.json.*.tmp"))


def test_save_text_replaces_existing_file_atomically(tmp_path):
    path = tmp_path / "report.md"
    path.write_text("old")
    save_text("new\n", path)
    assert path.read_text() == "new\n"
    assert not list(tmp_path.glob(".report.md.*.tmp"))
