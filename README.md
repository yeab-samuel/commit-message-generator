# Commit message generator

A small tool that reads a **git diff** (a code change) and suggests a **one-line commit message**.
Course project 1 for *Selected Topics in Software Engineering: Transformers and Reinforcement Learning* (Addis Ababa University).

- **Demo video:** https://drive.google.com/file/d/1zScUs1kHW4vQi9x4vWvsIK0cNRjuE_2a/view?usp=sharing
- **Team:**

      - Yeabsira Samuel — ATE/9305/14
      - Natnael Nigatu — ATE/7495/14
      - Kassahun Belachew — ATE/8400/14
      - Natnael Yohannes — ATE/0038/14

## The problem and the user

Developers write a short note (the *commit message*) every time they save a change. These notes are often skipped or written badly.
The user here is a developer with a small change to one Python file who wants a first draft of the message.
The tool is a **drafting aid**: a person still reads and edits the suggestion.

**Scope:** single-file Python changes under 2,000 characters. Other languages, multi-file changes and long diffs were not evaluated.

## What was built

| Part | What it is |
|---|---|
| Pretrained Transformer | `Qwen/Qwen2.5-Coder-1.5B-Instruct` from Hugging Face |
| Adaptation | **LoRA fine-tuning** (4.36 M trainable parameters, 0.28% of the model) on 3,000 real (diff, message) pairs, one pass |
| Simple baseline | `Update <file name>` (no Transformer, see `src/baseline.py`) |
| Comparison models | the same model **prompted only** (fine-tuning switched off), and a second fine-tune (v2) |
| Data | [CommitBench](https://huggingface.co/datasets/Maxscha/commitbench) (arXiv:2403.05188), filtered to a single changed `.py` file under 2,000 characters |

Training and evaluation ran on a free Colab T4 GPU (training took about 10 minutes for v1). `src/model.py` also has a CPU path, but it was not tested, and a 1.5B model on a CPU will be slow.

## Results

All scores are **ROUGE-L** (0 to 1, how many words in the same order the suggestion shares with the real message). Higher is better. 200 examples per test set.

| Method | Test set 1 | Test set 2 (fresh projects) |
|---|---|---|
| Baseline `Update <file>` | 0.076 | 0.082 |
| Prompted only | 0.148 | 0.167 |
| **Fine-tuned v1 (the shipped model)** | **0.193** | **0.196** |
| Fine-tuned v2 | not run | 0.193 |

Other numbers (full detail in `results/summary.csv`; `python -m src.evaluate results/test2_results.json` recomputes them):

- **First line only.** Scoring against the first line of the real message gives the same ranking (test set 2: 0.095, 0.176, 0.207, 0.203).
- **Constant messages.** Always answering "Fix bug" scores 0.03 and "Fix bug in the code" scores 0.06 to 0.07, so the fine-tuned score is not just the word "fix".
- **Misses.** On test set 2, 126 of 200 baseline outputs, 41 prompted, 53 v1 and 51 v2 outputs shared no words with the real message.
- **v1 vs v2.** v2 (5,833 examples, first-line targets, fewer "Fix" examples) was better on 60 test-set-2 examples, v1 on 78, 62 tied. The difference is within noise, so v1 was kept.

### Manual rating (30 outputs)

30 random v1 outputs from test set 2 were rated by hand using the question *"would someone who reads only this message be misled?"*
(`manual_ratings.csv`)

| Rating | Count |
|---|---|
| Good (accurate, usable as written) | 10 |
| Okay (right area, but vague or needs editing) | 17 |
| Wrong (describes something the change does not do) | 3 |

Any message containing a dataset placeholder such as `<I>` was counted as at most "okay".
**Caveat:** one rater, and the author did the rating with Claude explaining what each diff does, so this is a rough indication and not an independent measurement. With 30 samples the true share of misleading messages could plausibly be anywhere from a few percent to about a quarter.

## Evaluation setup (how the test was kept honest)

- Dev set (100), test set 1 (200) and test set 2 (200) are all different from the training data. No diff is shared, and **no GitHub project that appears in dev or test 1 was used for training**.
- Test set 2 was built later from 192 projects that appear nowhere else. `tests/test_saved_results.py` checks that dev, test 1 and test 2 share no diff.
- Prompt wording and model versions were compared on the **dev** set. Test set 2 was used to choose between v1 and v2, so its numbers are slightly optimistic. Test set 1 was scored before any such choice.
- Each model was trained once (no repeated seeds), so differences of about 0.03 between versions should not be over-read.

## Failure analysis

Failures were read from 10 random zero-score outputs, then checked against counts over the whole test set and the 30 rated outputs.

1. **Different wording, same meaning.** ROUGE gives zero to messages that are fine but worded differently (for example *Removed _BaseObject* for a real message about removing a metaclass line).
2. **Too generic.** "Fix bug in X" is used when the change is a refactor, a new feature or a small tweak. The model starts 52% of test set 2 outputs with "Fix" (real messages: about 17%).
3. **Invented details.** All 3 "wrong" outputs in the manual rating claimed something the diff does not show (a "typo", "comments", "was not working"). Example: a change that only removed error handling was described as fixing a bug.
4. **Placeholders copied.** CommitBench replaces numbers and links with `<I>` and `<URL>`; the model sometimes copies them (for example `Bumped version to <I>.`).
5. **Not knowable from the diff.** Real messages such as "add serial comma to please my OCD" depend on context the model never sees.
6. **Multi-line messages.** About 20% of real messages have a body; the tool writes one line.

Open questions (not tested, so treat as hypotheses):

- The "Fix" habit may come from the model always choosing its single most likely first word. In v2, cutting "Fix" examples in training to about 23% did **not** lower it (60% on test set 2), and why it went up is unexplained. v2 changed three things at once (more data, first-line targets, fewer "Fix" examples), so the experiment cannot say which change mattered.
- Fine-tuning mostly seems to teach the style of commit messages. It does not reliably teach what a change means.

## Limitations

- Python only, one file, under 2,000 characters. Longer diffs are cut at 4,000 characters, and quality on them is unknown.
- ROUGE-L only counts shared words, so it under-rates good messages and over-rates vague ones with common words.
- Dataset messages are noisy (bumps, merges, in-jokes).
- CommitBench contains code from many public projects; see its dataset card for its license and terms before reusing the data.

## How to run

```bash
git clone https://github.com/yeab-samuel/commit-message-generator
cd commit-message-generator
pip install -r requirements.txt
```

If `peft` raises an `ImportError` about `torchao` (it happened on Colab), run `pip uninstall -y torchao`.

**Run the tests** (no GPU needed; the model itself is not downloaded):

```bash
python -m pytest
```

**Recompute the result tables** from the saved outputs (no GPU needed):

```bash
python -m src.evaluate results/test1_results.json
python -m src.evaluate results/test2_results.json
```

**Get a commit message for a diff** (downloads the 1.5B model, about 3 GB, on first use):

```bash
python -m src.generate examples/sample.diff
git diff | python -m src.generate
python -m src.generate examples/sample.diff --baseline    # no model needed
```

**Re-run everything** (data download, training, scoring): open `notebooks/commit_message_generator.ipynb` in Google Colab with a T4 GPU. The notebook is the real working log, so it also contains a few cells that failed and were fixed (a Colab session reset that wiped memory, and a `torchao` version clash).

## Repository layout

```
src/            baseline, prompt building, model wrapper, command line tool, ROUGE evaluation
tests/          pytest tests (data filter, baseline, prompt, CLI, scoring, saved-results checks)
data/           dev, test and test2 evaluation sets (training data is rebuilt by the notebook)
results/        raw outputs for every method, summary.csv, bar chart
adapter_v1/     the LoRA adapter that was trained (the shipped model)
examples/       a sample diff
manual_ratings.csv   the 30 hand-rated outputs
notebooks/      the Colab notebook
```

## AI tools used

Claude (Anthropic) was used throughout: to plan the project, write and explain the notebook and repository code, interpret results and draft this README.
The model itself (Qwen2.5-Coder) is an AI model that was fine-tuned and evaluated. The manual ratings were made with Claude's help, as described above.

## Credits

- CommitBench dataset (arXiv:2403.05188, Hugging Face: `Maxscha/commitbench`)
- Qwen2.5-Coder-1.5B-Instruct (Qwen team, Hugging Face)
- Hugging Face `transformers`, `peft`, `datasets`; Google `rouge-score`
- Course key paper for this chapter: Vaswani et al. (2017), *Attention Is All You Need*
