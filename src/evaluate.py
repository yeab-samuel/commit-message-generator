"""Score saved model outputs with ROUGE-L (no GPU needed).

    python -m src.evaluate results/test2_results.json
"""
import argparse

from rouge_score import rouge_scorer

from .data import first_line, load_json

_SCORER = rouge_scorer.RougeScorer(["rougeL"])


def rouge_l(real, prediction):
    """ROUGE-L F-measure between a real message and a predicted one (0 to 1)."""
    return _SCORER.score(real, prediction)["rougeL"].fmeasure


def method_keys(records):
    """Names of the methods stored in a results file (everything except diff, real and *_score)."""
    return [k for k in records[0] if k not in ("diff", "real") and not k.endswith("_score")]


def summarize(records, key):
    """Average scores for one method over all records."""
    n = len(records)
    full = [rouge_l(r["real"], r[key]) for r in records]
    first = [rouge_l(first_line(r["real"]), r[key]) for r in records]
    return {
        "method": key,
        "n": n,
        "rougeL_full": sum(full) / n,
        "rougeL_first_line": sum(first) / n,
        "zero_scores": sum(s == 0 for s in full),
        "starts_with_fix": sum(r[key].lower().startswith("fix") for r in records),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Recompute the ROUGE-L table from a saved results file.")
    parser.add_argument("results_file")
    args = parser.parse_args(argv)

    records = load_json(args.results_file)
    print(f"{'method':<12}{'n':>5}{'full':>8}{'first line':>12}{'zeros':>7}{'starts with fix':>17}")
    for key in method_keys(records):
        s = summarize(records, key)
        print(
            f"{s['method']:<12}{s['n']:>5}{s['rougeL_full']:>8.3f}{s['rougeL_first_line']:>12.3f}"
            f"{s['zero_scores']:>7}{s['starts_with_fix']:>17}"
        )


if __name__ == "__main__":
    main()
