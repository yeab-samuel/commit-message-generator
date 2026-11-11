from src.baseline import baseline_message

DIFF = "diff --git a/scraperwiki/sql.py b/scraperwiki/sql.py\n--- a/scraperwiki/sql.py\n+++ b/scraperwiki/sql.py\n"


def test_baseline_names_the_changed_file():
    assert baseline_message(DIFF) == "Update scraperwiki/sql.py"


def test_baseline_handles_text_without_a_diff_header():
    assert baseline_message("not a diff") == "Update"
