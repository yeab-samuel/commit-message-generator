"""Helpers for reading diffs and the evaluation data."""
import json


def first_line(text):
    """Return the first line of a commit message (the subject line)."""
    return text.strip().split("\n")[0]


def changed_files(diff):
    """List the files touched by a git diff, taken from its 'diff --git' header lines."""
    return [line.split(" b/")[-1] for line in diff.split("\n") if line.startswith("diff --git")]


def is_python_only(diff):
    """True if the diff changes exactly one file and that file is a .py file.

    This is the filter used to build the dev/test/train sets.
    """
    files = changed_files(diff)
    return len(files) == 1 and files[0].endswith(".py")


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)
