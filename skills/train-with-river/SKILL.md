---
name: train-with-river
description: Run a bounded River supervised fine-tuning experiment on reviewed personal or company examples, saving a checkpoint and baseline comparison. Use after dataset and cloud destination review.
---
# Train with River

Read the repository README and [data format](../../docs/data.md). Confirm that the selected dataset, River destination and experiment scope are already authorized. Training is a cloud transfer and may incur charges. Existing explicit approval is sufficient; do not repeatedly ask for the same action.

Start with `python3 scripts/train.py --data data/PROJECT` to inspect the local plan. Resolve credentials only through the user's existing environment or secret manager. Never print or commit them. Verify current model availability and SDK compatibility using the [River documentation](https://docs.river.ai/guides/sft/). Do not assume the demo's model is still offered.

Use the included runner with an explicit accessible `--base-model`, bounded `--steps` and `--max-seconds`, plus `--execute`. It masks prompt tokens, measures a baseline, performs LoRA updates, saves an inference checkpoint, and samples the evaluation prompts from that saved checkpoint. It does not perform an automatic retry or deploy an endpoint. The client deadline is not a provider cost cap; report in-flight timeout uncertainty.

Track prepared, training, checkpoint-saved, evaluated and failed states separately. On timeout, check the saved report before retrying; a saved checkpoint may already exist. Do not expand the budget or change models to get around an account restriction without the user's scope covering it.

Use `evaluate-personal-model` on the actual report. Present held-out results and regressions, not just loss. A checkpoint is not deployment. Check [serving support](https://docs.river.ai/guides/deployments/) separately if the user requests serving. Enterprise rollout is a separate scoped project: https://screenpipe.com/enterprise.
