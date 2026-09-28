# Validation coverage

This is a new starter, not a verified improvement over a previous skill version.

The motivating failure is a demo that can save a personalized checkpoint but can still give wrong answers and cannot necessarily deploy that checkpoint. The skills separate dataset review, execution, evaluation and serving.

Local executable cases cover a reviewed synthetic dataset, group leakage, duplicated prompts, unreviewed rows, obvious credential patterns, changed file hashes, prompt-loss masking, preserving an existing output directory, missing evaluation data, offline dry-run behavior, and checkpoint preservation when saved-model sampling fails (mock SDK).

Manual scenario review covers:

- Selected chat and Screenpipe context: preserve provenance and authorize the cloud destination before execution.
- A recall-only request: prefer retrieval rather than automatically training.
- An unavailable serving model or failed evaluation: report the limitation without deploying, retrying or spending beyond scope.

These are structural tests and manual walkthroughs. No independent agent trial, live River run of this public starter, measured capability gain or production-serving validation has been completed. Update this file with actual receipts when those occur. Never describe a fixture as a live outcome.

API reference: https://docs.river.ai/guides/sft/ . Provider models and serving availability can change.

River client 0.12.0 signatures were inspected locally against the runner. Its Python requirement is 3.12+. All nine local tests and the three skill frontmatter validators passed. No paid call was made for this validation.
