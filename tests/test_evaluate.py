from src.evaluate import method_keys, rouge_l, summarize


def test_identical_messages_score_one():
    assert rouge_l("Fix typo in README", "Fix typo in README") == 1.0


def test_messages_with_no_shared_words_score_zero():
    assert rouge_l("Fix typo in README", "Bump version number") == 0.0


def test_partial_overlap_is_between_zero_and_one():
    score = rouge_l("Add test for transport errors", "Add test")
    assert 0.0 < score < 1.0


def test_method_keys_ignores_diff_real_and_score_columns():
    record = {"diff": "d", "real": "r", "baseline": "b", "model": "m", "model_score": 0.1}
    assert method_keys([record]) == ["baseline", "model"]


def test_summarize_counts_zero_scores_and_fix_openers():
    records = [
        {"real": "Fix typo in README", "model": "Fix typo in README"},
        {"real": "Add retry logic", "model": "Fix bug in client"},
    ]
    s = summarize(records, "model")
    assert s["n"] == 2
    assert s["zero_scores"] == 1
    assert s["starts_with_fix"] == 2
    assert 0.0 < s["rougeL_full"] < 1.0
