from src.data import changed_files, first_line, is_python_only

PY_DIFF = "diff --git a/pkg/mod.py b/pkg/mod.py\nindex 1..2 100644\n--- a/pkg/mod.py\n+++ b/pkg/mod.py\n@@ -1 +1 @@\n-x = 1\n+x = 2\n"
JS_DIFF = "diff --git a/lib/app.js b/lib/app.js\n--- a/lib/app.js\n+++ b/lib/app.js\n@@ -1 +1 @@\n-a\n+b\n"
TWO_FILES = PY_DIFF + "diff --git a/other.py b/other.py\n--- a/other.py\n+++ b/other.py\n@@ -1 +1 @@\n-a\n+b\n"


def test_first_line_returns_subject_only():
    assert first_line("Fix bug\n\nLonger body text") == "Fix bug"
    assert first_line("  Add test  ") == "Add test"


def test_changed_files_reads_the_diff_header():
    assert changed_files(PY_DIFF) == ["pkg/mod.py"]
    assert changed_files(TWO_FILES) == ["pkg/mod.py", "other.py"]
    assert changed_files("no header here") == []


def test_is_python_only_accepts_a_single_python_file():
    assert is_python_only(PY_DIFF)


def test_is_python_only_rejects_other_languages_and_multi_file_diffs():
    assert not is_python_only(JS_DIFF)
    assert not is_python_only(TWO_FILES)
    assert not is_python_only("")
