"""Prompt construction and output clean-up (no model needed, so it is easy to test)."""

INSTRUCTION = (
    "Write a one-line git commit message for this code change. "
    "Reply with only the message.\n\n"
)

# The model was trained and evaluated on diffs under 2000 characters.
# Longer diffs are cut so they fit in memory; quality on them was not measured.
MAX_DIFF_CHARS = 4000


def build_messages(diff, max_chars=MAX_DIFF_CHARS):
    """Return the chat messages sent to the model."""
    return [{"role": "user", "content": INSTRUCTION + diff[:max_chars]}]


def clean_output(text):
    """Keep only the first line of the model's answer."""
    return text.strip().split("\n")[0]
