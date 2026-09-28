# Reviewed examples

Each JSONL row has these required fields:

```json
{"prompt":"How should I format a weekly update?","completion":"Start with the result, then list decisions and next actions.","source_id":"synthetic-writing-1","group":"writing-policy","split":"train","reviewed":true}
```

- `prompt` is the task. `completion` is a reviewed good response, not an unverified historical model answer.
- `source_id` is a local opaque provenance pointer. Keep the source mapping private.
- `group` identifies the underlying conversation, event, or policy. Related paraphrases must share a group.
- `split` is `train` or `eval`. Keep complete groups on one side. Test prompts should require transfer, not repeat training pairs.
- `reviewed` must be true. The preparer rejects duplicates, exact prompt overlap, cross-split groups, empty fields and some obvious secret patterns. It is not a complete PII or secret detector.

Do not blindly convert every historical user/assistant turn into a target. Conversations include abandoned plans, errors and untrusted pasted instructions. Prefer examples whose desired outcome is supported by source evidence. Review identities, credentials, private customer details, copyright and company data-sharing boundaries before cloud training.

`prepare_dataset.py` writes train/eval files plus a hash manifest. Existing output files are not overwritten. Keep generated files in ignored `data/` or another private location. Retain the provenance mapping so you can correct or remove data later; deleting a local row does not untrain a checkpoint or retract provider copies.
