import copy
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from prepare_dataset import prepare, validate, load
from train import make_datum, main, read_data

class Workflow(unittest.TestCase):
    def setUp(self): self.rows = load(ROOT/'examples/reviewed.jsonl')
    def test_synthetic_roundtrip_and_offline_plan(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)/'data'; prepare(ROOT/'examples/reviewed.jsonl', out)
            # No SDK import allowed during a dry-run.
            with patch.dict(sys.modules, {'river_client':None, 'transformers':None}), contextlib.redirect_stdout(io.StringIO()) as s:
                self.assertEqual(main(['--data',str(out)]),0)
            self.assertFalse(json.loads(s.getvalue())['cloud_transfer'])
    def test_source_group_leakage(self):
        self.rows[-1]['group'] = self.rows[0]['group']
        with self.assertRaises(ValueError): validate(self.rows)
    def test_paraphrase_duplicate_normalization(self):
        self.rows[-1]['prompt'] = '  '+self.rows[0]['prompt'].upper()+'  '
        with self.assertRaises(ValueError): validate(self.rows)
    def test_unreviewed_and_credential(self):
        self.rows[0]['reviewed'] = False
        with self.assertRaises(ValueError): validate(self.rows)
        self.rows[0]['reviewed'] = True
        self.rows[0]['completion'] = 'rv_' + 'x'*40
        with self.assertRaises(ValueError): validate(self.rows)
    def test_modified_dataset(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'data';prepare(ROOT/'examples/reviewed.jsonl',out)
            with (out/'train.jsonl').open('a') as f:f.write('\n')
            with self.assertRaises(ValueError):read_data(out)
    def test_next_token_mask(self):
        row=make_datum([10,11,12],[20,21],99)
        self.assertEqual(row['target_tokens'],[11,12,20,21,99,99])
        self.assertEqual(row['weights'],[0,0,1,1,1,0])
        self.assertEqual(len(row['input_ids']),len(row['weights']))
    def test_existing_output_preserved(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(FileExistsError):prepare(ROOT/'examples/reviewed.jsonl',Path(d))
    def test_saved_checkpoint_survives_sample_failure(self):
        river = MagicMock()
        client = river.Client.return_value
        client.get_capabilities.return_value = ['fixture-model']
        session = client.session.return_value.__enter__.return_value
        model = session.create_model.return_value
        model.step = 1
        model.model_id = 'fixture-model-id'
        model.sample.return_value = [[SimpleNamespace(text='base')] for _ in range(2)]
        model.train_step.return_value = (SimpleNamespace(metrics={'loss':1.0}), None)
        model.save_weights.return_value = SimpleNamespace(path='fixture-checkpoint')
        session.sample.side_effect = TimeoutError()
        tok = MagicMock(eos_token_id=99)
        tok.apply_chat_template.return_value = 'rendered'
        tok.encode.return_value = [10,11]
        transformers = MagicMock()
        transformers.AutoTokenizer.from_pretrained.return_value = tok
        with tempfile.TemporaryDirectory() as d:
            data=Path(d)/'data';out=Path(d)/'run'
            prepare(ROOT/'examples/reviewed.jsonl',data)
            with patch.dict(sys.modules, {'river_client':river,'transformers':transformers}), patch.dict('os.environ', {'RIVER_API_KEY':'fixture'}), contextlib.redirect_stdout(io.StringIO()):
                rc=main(['--data',str(data),'--out',str(out),'--base-model','fixture-model','--steps','1','--execute'])
            report=json.loads((out/'report.json').read_text())
            self.assertEqual(rc,1)
            self.assertEqual(report['state'],'checkpoint_saved_evaluation_failed')
            self.assertEqual(report['checkpoint'],'fixture-checkpoint')
            self.assertEqual(model.train_step.call_count,1)
            client.close.assert_called_once()
            session.create_model.assert_called_once()
    def test_no_eval_rejected(self):
        with self.assertRaises(ValueError):validate([r for r in self.rows if r['split']=='train'])

if __name__ == '__main__':unittest.main()
