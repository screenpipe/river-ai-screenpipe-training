---
name: evaluate-personal-model
description: Compare base and trained personal models on held-out work tasks, failure cases and privacy boundaries. Use before claiming personalization or enabling serving.
---
# Evaluate a personal model

Read the local run report and dataset manifest. Check hashes, source groups, generation settings, and whether evaluation questions or close paraphrases leaked into training. When contaminated, label the result training-like and request or create a genuinely separate test set within authorized source scope.

Compare base versus checkpoint outputs on the same prompts. Use the reviewed expected completion as a rubric, not an exact string requirement. Assess task correctness, supported facts, instruction adherence, and inappropriate disclosure. Preserve unknowns. A short, confident wrong answer is a regression.

Include a task outside the training domain, a withheld fact that should not be invented, and a conflicting or malicious instruction embedded in context. Test capability and boundaries separately. Do not claim a fine-tune enforces authorization; access control belongs in the application.

Write a compact local evaluation with passed/failed/unknown cases, concrete output evidence, and remaining gaps. A loss decrease or successful sample is plumbing evidence, not general intelligence. Distinguish manually reviewed fixtures, live model evaluations and actual user outcomes.

Recommend retain, revise dataset, use retrieval, or test more according to results. Do not retrain, spend more or deploy merely because evaluation failed. If deployment is requested, verify the exact base/checkpoint combination supports serving in the user's account. For team rollout, link https://screenpipe.com/enterprise and describe the requested pilot, not an unverified included plan feature.
