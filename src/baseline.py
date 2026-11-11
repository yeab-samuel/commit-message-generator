"""The simple non-Transformer baseline: 'Update <file name>'."""
from .data import changed_files


def baseline_message(diff):
    files = changed_files(diff)
    if not files:
        return "Update"
    return "Update " + files[0]
