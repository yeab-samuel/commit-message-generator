"""Checks on the data and results files in the repository.

They skip themselves if the files have not been added yet.
"""
from pathlib import Path

import pytest

from src.data import is_python_only, load_json
from src.evaluate import summarize

ROOT = Path(__file__).resolve().parent.parent


def _load(relative_path):
    path = ROOT / relative_path
    if not path.exists():
        pytest.skip(f"{relative_path} not found")
    return load_json(path)


def test_evaluation_sets_have_the_expected_sizes_and_filters():
    for name, size in [("dev", 100), ("test", 200), ("test2", 200)]:
        data = _load(f"data/{name}.json")
        assert len(data) == size
        assert all(is_python_only(e["diff"]) and len(e["diff"]) < 2000 for e in data)


def test_dev_test_and_test2_do_not_share_any_diff():
    dev, test, test2 = (_load(f"data/{n}.json") for n in ("dev", "test", "test2"))
    sets = [{e["diff"] for e in part} for part in (dev, test, test2)]
    assert not (sets[0] & sets[1])
    assert not (sets[0] & sets[2])
    assert not (sets[1] & sets[2])


def test_test2_covers_many_different_projects():
    test2 = _load("data/test2.json")
    assert len({e["project"] for e in test2}) > 150


def test_saved_results_belong_to_the_evaluation_sets():
    test = _load("data/test.json")
    test2 = _load("data/test2.json")
    r1 = _load("results/test1_results.json")
    r2 = _load("results/test2_results.json")
    assert [r["diff"] for r in r1] == [e["diff"] for e in test]
    assert [r["diff"] for r in r2] == [e["diff"] for e in test2]


@pytest.mark.parametrize(
    "file, key, expected",
    [
        ("results/test1_results.json", "baseline", 0.076),
        ("results/test1_results.json", "model", 0.148),
        ("results/test1_results.json", "finetuned", 0.193),
        ("results/test2_results.json", "baseline", 0.082),
        ("results/test2_results.json", "prompted", 0.167),
        ("results/test2_results.json", "v1", 0.196),
        ("results/test2_results.json", "v2", 0.193),
    ],
)
def test_headline_scores_match_the_report(file, key, expected):
    records = _load(file)
    assert summarize(records, key)["rougeL_full"] == pytest.approx(expected, abs=0.0006)
