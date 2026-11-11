"""Command line tool: turn a git diff into a commit message.

Examples:
    git diff | python -m src.generate
    python -m src.generate examples/sample.diff
    python -m src.generate examples/sample.diff --baseline     (no model, no GPU)
"""
import argparse
import sys

from .baseline import baseline_message


def main(argv=None):
    parser = argparse.ArgumentParser(description="Suggest a one-line commit message for a git diff.")
    parser.add_argument("diff_file", nargs="?", help="path to a diff file (default: read from standard input)")
    parser.add_argument("--adapter", default="adapter_v1", help="folder with the LoRA adapter (default: adapter_v1)")
    parser.add_argument("--baseline", action="store_true", help="use the simple 'Update <file>' baseline instead of the model")
    args = parser.parse_args(argv)

    if args.diff_file:
        with open(args.diff_file, encoding="utf-8") as f:
            diff = f.read()
    else:
        diff = sys.stdin.read()

    if not diff.strip():
        parser.error("the diff is empty")

    if args.baseline:
        print(baseline_message(diff))
        return

    from .model import CommitMessageGenerator  # imported here so --baseline works without torch

    generator = CommitMessageGenerator(adapter_dir=args.adapter)
    print(generator.generate(diff))


if __name__ == "__main__":
    main()
