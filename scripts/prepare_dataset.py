"""Validate reviewed examples and split locally. No network dependencies."""
import argparse
import hashlib
import json
import re
from pathlib import Path

FIELDS = ('prompt', 'completion', 'source_id', 'group', 'split')
SECRET = re.compile(r'(?:\brv_[A-Za-z0-9_-]{20,}|\bsk-[A-Za-z0-9_-]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----|\bAKIA[A-Z0-9]{16}\b)')

def validate(rows):
    if not rows:
        raise ValueError('No examples')
    groups, prompts = {}, set()
    for i, row in enumerate(rows):
        if not isinstance(row, dict) or any(not isinstance(row.get(k), str) or not row[k].strip() for k in FIELDS):
            raise ValueError(f'Row {i+1}: required nonempty fields missing')
        if row.get('reviewed') is not True or row['split'] not in ('train', 'eval'):
            raise ValueError(f'Row {i+1}: review or split invalid')
        if SECRET.search(json.dumps(row)):
            raise ValueError(f'Row {i+1}: possible credential, review locally')
        group = row['group'].strip().casefold()
        if group in groups and groups[group] != row['split']:
            raise ValueError('Related source group appears in both splits')
        groups[group] = row['split']
        prompt = ' '.join(row['prompt'].casefold().split())
        if prompt in prompts:
            raise ValueError('Duplicate or overlapping prompt')
        prompts.add(prompt)
    if {r['split'] for r in rows} != {'train', 'eval'}:
        raise ValueError('Both train and eval examples are required')
    return rows

def load(path):
    return [json.loads(x) for x in Path(path).read_text().splitlines() if x.strip()]

def prepare(source, out):
    rows = validate(load(source))
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    manifest = {'schema_version': 1, 'files': {}, 'groups': {}}
    for split in ('train', 'eval'):
        selected = [r for r in rows if r['split'] == split]
        f = out / (split + '.jsonl')
        f.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in selected))
        manifest['files'][f.name] = {'sha256': hashlib.sha256(f.read_bytes()).hexdigest(), 'examples': len(selected)}
        manifest['groups'][split] = sorted({r['group'] for r in selected})
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2))
    return manifest

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source'); p.add_argument('--out', required=True)
    a = p.parse_args()
    try:
        print(json.dumps(prepare(a.source, a.out), indent=2))
    except (ValueError, OSError) as e:
        p.exit(1, f'Preparation stopped: {e}\n')
