from src.prompt import INSTRUCTION, MAX_DIFF_CHARS, build_messages, clean_output


def test_prompt_contains_instruction_and_diff():
    messages = build_messages("diff --git a/x.py b/x.py")
    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    assert messages[0]["content"].startswith(INSTRUCTION)
    assert messages[0]["content"].endswith("diff --git a/x.py b/x.py")


def test_very_long_diffs_are_cut():
    messages = build_messages("a" * (MAX_DIFF_CHARS + 500))
    assert len(messages[0]["content"]) == len(INSTRUCTION) + MAX_DIFF_CHARS


def test_clean_output_keeps_only_the_first_line():
    assert clean_output("Add retry logic\nThis change adds...") == "Add retry logic"
    assert clean_output("  Fix typo  \n") == "Fix typo"
    assert clean_output("") == ""
