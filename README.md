# Personal AI

**Train an AI on how you work.**

Agent skills for turning selected AI chats and Screenpipe context into a personal or company model with [River](https://river.ai).

Your conversations contain preferences. Your work history contains examples. This toolkit helps an AI coding agent turn the parts you choose into reviewed training data, run a small fine-tuning experiment, and test what changed.

**[Explore Screenpipe Enterprise](https://screenpipe.com/enterprise)** to scope a team pilot, data access, and implementation support. Training, inference, and managed delivery are scoped separately. This repository is a self-directed experimental toolkit.

Requires Python 3.12 or newer for River execution. Local preparation and dry-runs use only the standard library.

## Start with your agent

Clone this repository, open it in Codex, Claude Code, or another coding agent, and paste:

> Read skills/curate-work-context/SKILL.md. Help me prepare a small dataset from AI chats and Screenpipe history I select. Keep it local while we review it. Then use skills/train-with-river/SKILL.md to plan a River experiment and skills/evaluate-personal-model/SKILL.md to compare the results. Start with one behavior I want my model to learn.

```sh
git clone https://github.com/screenpipe/personal-ai.git
cd personal-ai
python3 scripts/prepare_dataset.py examples/reviewed.jsonl --out data/demo
python3 scripts/train.py --data data/demo
```

The last command validates the data and prints a local plan. It makes no API calls and does not download a model. The included examples are synthetic plumbing fixtures, not enough data to produce a useful personalized model.

Keep the skills in this checkout so their linked documentation and scripts remain available. Reference their paths directly in your agent; no global installation is required.

## The workflow

| Skill | What it produces |
| --- | --- |
| [Curate work context](skills/curate-work-context/SKILL.md) | Reviewed prompt/answer examples with provenance and an independent evaluation split |
| [Train with River](skills/train-with-river/SKILL.md) | A bounded LoRA run, baseline outputs, a saved checkpoint, and sampled outputs |
| [Evaluate a personal model](skills/evaluate-personal-model/SKILL.md) | A comparison against the same prompts, failure cases, and a serving decision |

Sources can include selected Codex or Claude conversations, user-provided ChatGPT exports, reviewed Screenpipe OCR/transcripts, and written procedures. The skills use your agent's existing local tools. This repo does not silently crawl your computer or upload raw history.

## Run a real experiment

1. Follow the curation skill and replace the synthetic examples with reviewed examples. See [the data format](docs/data.md).
2. Install dependencies in a virtual environment: `python3 -m venv .venv`, activate it, then `pip install -r requirements.txt`.
3. Configure `RIVER_API_KEY` through your environment or secret manager. Never put it in a command argument, dataset, or committed file.
4. Check [River model access](https://docs.river.ai/guides/models/) and choose a model available to your account.
5. Review the local plan, then run with explicit execution:

```sh
python scripts/train.py --data data/your-project --base-model YOUR_AVAILABLE_MODEL \
  --steps 10 --max-seconds 300 --execute
```

The execution sends the reviewed prompt/completion tokens and evaluation prompts to River and can incur training/inference charges. The time limit is a client-side stop between requests, not a provider billing cap; an in-flight request can outlast it. Runs do not retry automatically. Outputs stay in ignored `runs/`.

## What this does and does not show

Fine-tuning can teach recurring response patterns, language preferences, and procedures. It is not a reliable database for changing facts. Use retrieval for source-grounded recall and evaluate both approaches for your task.

A small demo is not a personal superintelligence, a proven company clone, or evidence of broad reliability. Keep unrelated conversations out of training, hold out entire source groups, and test failure cases. Passing a few training-like questions does not establish generalization.

A saved River checkpoint is separate from a deployed endpoint. Confirm model and serving support in your River account before promising a live chat UI. This toolkit does not enable paid serving or change account configuration automatically.

## Validation

```sh
python3 -m unittest discover -s tests -v
```

See [validation coverage](docs/validation.md). Local tests exercise preparation, leakage rejection, masking and dry-run behavior. A successful local test is not a completed River training run.

Built by [Screenpipe](https://screenpipe.com), using River's public API. No official River partnership is implied.
