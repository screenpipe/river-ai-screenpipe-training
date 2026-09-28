"""Dry-run by default. Explicit --execute sends reviewed data to River."""
import argparse
import hashlib
import json
import os
import time
from contextlib import closing
from pathlib import Path
from prepare_dataset import load, validate


def make_datum(prompt_ids, completion_ids, eos):
    if not prompt_ids or not completion_ids:
        raise ValueError('Empty token sequence')
    ids = prompt_ids + completion_ids + [eos]
    return {'input_ids': ids, 'target_tokens': ids[1:] + [eos],
            'weights': [0.0] * (len(prompt_ids)-1) + [1.0] * (len(completion_ids)+1) + [0.0]}


def read_data(directory):
    directory = Path(directory)
    manifest = json.loads((directory/'manifest.json').read_text())
    result = {}
    for name in ('train', 'eval'):
        f = directory/(name+'.jsonl')
        if hashlib.sha256(f.read_bytes()).hexdigest() != manifest['files'][f.name]['sha256']:
            raise ValueError('Dataset changed after preparation; prepare a new reviewed version')
        result[name] = load(f)
        if any(r['split'] != name for r in result[name]):
            raise ValueError('Row stored in wrong split')
    validate(result['train'] + result['eval'])
    return result, manifest


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data', required=True)
    p.add_argument('--base-model')
    p.add_argument('--steps', type=int, default=10)
    p.add_argument('--max-seconds', type=int, default=300)
    p.add_argument('--out', default='runs/latest')
    p.add_argument('--execute', action='store_true')
    a = p.parse_args(argv)
    if not 1 <= a.steps <= 20 or not 30 <= a.max_seconds <= 600:
        p.error('Use 1–20 steps and 30–600 seconds for this starter')
    data, manifest = read_data(a.data)
    plan = {'state': 'prepared', 'base_model': a.base_model, 'steps_requested': a.steps,
            'client_deadline_seconds': a.max_seconds, 'train_examples': len(data['train']),
            'eval_examples': len(data['eval']), 'dataset_manifest': manifest,
            'cloud_transfer': bool(a.execute), 'deployment': 'not_requested'}
    if not a.execute:
        print(json.dumps(plan, indent=2)); return 0
    if not a.base_model or not os.environ.get('RIVER_API_KEY'):
        p.error('Execution needs --base-model and RIVER_API_KEY in the environment')
    out = Path(a.out); out.mkdir(parents=True, exist_ok=False)
    def save():
        (out/'report.json').write_text(json.dumps(plan, indent=2))
    save()
    # Imports and tokenizer downloads happen only after explicit execution.
    started = time.monotonic()
    def remaining():
        seconds = a.max_seconds - (time.monotonic() - started)
        if seconds <= 0:
            raise TimeoutError('Client deadline reached')
        return min(45, max(1, seconds))
    try:
        import river_client as river
        from transformers import AutoTokenizer
        if len(data['eval']) > 20:
            raise ValueError('Starter evaluation exceeds 20 examples')
        tok = AutoTokenizer.from_pretrained(a.base_model)
        if tok.eos_token_id is None:
            raise ValueError('Tokenizer has no EOS token')
        def prompt(text):
            return tok.apply_chat_template([{'role':'user','content':text}], tokenize=False,
                                            add_generation_prompt=True, enable_thinking=False)
        batch = [make_datum(tok.encode(prompt(r['prompt']), add_special_tokens=False),
                            tok.encode(r['completion'], add_special_tokens=False), tok.eos_token_id)
                 for r in data['train']]
        if sum(len(x['input_ids']) for x in batch) > 32000:
            raise ValueError('Starter batch exceeds 32000 tokens; reduce the reviewed scope')
        prompts = [prompt(r['prompt']) for r in data['eval']]
        plan['evaluation'] = [{'prompt':r['prompt'], 'expected':r['completion'], 'source_id':r['source_id']} for r in data['eval']]
        with closing(river.Client(api_key=os.environ['RIVER_API_KEY'], timeout=remaining(), enable_retries=False)) as client:
            if a.base_model not in client.get_capabilities():
                raise ValueError('Requested model is not enabled for this account')
            with client.session(project='screenpipe-personal-ai', timeout=remaining()) as session:
                model = session.create_model(base_model=a.base_model, lora=river.LoraConfig(rank=8), tokenizer=tok, timeout=remaining())
                plan.update(state='training', model_id=model.model_id, steps=[]); save()
                before = model.sample(prompts, max_tokens=128, temperature=0.0, timeout=remaining())
                for row, sample in zip(plan['evaluation'], before): row['before'] = sample[0].text
                save()
                for _ in range(a.steps):
                    fb, _ = model.train_step(batch, lr=2e-4, grad_clip_norm=1.0, timeout=remaining())
                    plan['steps'].append({'step':model.step, 'metrics':fb.metrics}); save()
                ckpt = model.save_weights('personal-ai', mode='inference', timeout=remaining())
                plan.update(state='checkpoint_saved', checkpoint=ckpt.path); save()
                after = session.sample(prompts, base_model=a.base_model, checkpoint=ckpt,
                                       max_tokens=128, temperature=0.0, timeout=remaining())
                for row, sample in zip(plan['evaluation'], after): row['after'] = sample[0].text
                plan['state'] = 'evaluated'; save()
    except Exception as e:
        # Avoid provider exception bodies, which can echo request content or credentials.
        plan.update(state='checkpoint_saved_evaluation_failed' if plan.get('checkpoint') else 'failed',
                    error_type=type(e).__name__)
        save(); print('Run stopped. Review the local report; do not blindly retry.'); return 1
    finally:
        plan['elapsed_seconds'] = round(time.monotonic()-started, 2); save()
    print('Saved checkpoint and comparison in ' + str(out/'report.json'))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
