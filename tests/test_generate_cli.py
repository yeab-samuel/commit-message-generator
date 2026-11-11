import contextlib
import io
from pathlib import Path

from src.generate import main

SAMPLE = Path(__file__).resolve().parent.parent / "examples" / "sample.diff"


def test_baseline_option_runs_without_a_model():
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        main([str(SAMPLE), "--baseline"])
    assert out.getvalue().strip() == "Update utils/text.py"
