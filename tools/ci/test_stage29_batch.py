import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
with patch.dict(sys.modules, {'unreal': types.ModuleType('unreal')}):
    spec = importlib.util.spec_from_file_location('stage29_batch_test', ROOT/'unreal/NARIS_W04/Content/Python/naris_stage29_batch.py')
    BATCH = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(BATCH)

class Stage29BatchTests(unittest.TestCase):
    def invoke(self, report, apply=False):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'receipt.json'
            result=BATCH.run(lambda **kwargs: report,path,apply=apply)
            self.assertEqual(result,json.loads(path.read_text()))
            return result

    def test_dry_run_is_preflight_only(self):
        result=self.invoke({'run_id':'a'*32,'errors':[],'map_saved':False,'placed':0,'attempted':136})
        self.assertEqual(result['status'],'preflight_complete_requires_apply')
        self.assertEqual(result['G1'],'NOT_VERIFIED')
        self.assertEqual(result['G2'],'NOT_RUN')

    def test_apply_receipt_does_not_claim_pie_acceptance(self):
        result=self.invoke({'run_id':'a'*32,'errors':[],'map_saved':True,'placed':136,'attempted':136},True)
        self.assertEqual(result['status'],'authoring_complete_requires_PIE')
        self.assertEqual(result['G1'],'NOT_VERIFIED')

    def test_partial_authoring_and_preflight_errors_are_failures(self):
        cases=[({'run_id':'a'*32,'errors':[],'map_saved':True,'placed':135,'attempted':136},True),
               ({'run_id':'a'*32,'errors':['Missing asset']},False)]
        for report,apply in cases:
            with tempfile.TemporaryDirectory() as folder:
                path=Path(folder)/'receipt.json'
                with self.assertRaises(RuntimeError):BATCH.run(lambda **kw:report,path,apply=apply)
                result=json.loads(path.read_text());self.assertEqual(result['status'],'failed');self.assertTrue(result['errors'])

    def test_exception_preserves_failure_receipt(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'receipt.json'
            def fail(**kwargs):raise ValueError('Engine API failed')
            with self.assertRaises(ValueError):BATCH.run(fail,path)
            self.assertIn('Engine API failed',json.loads(path.read_text())['errors'])

    def test_stale_receipt_refused_before_execution(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'receipt.json';path.write_text('old evidence')
            def unexpected(**kwargs):self.fail('Must not execute with an existing receipt')
            with self.assertRaises(RuntimeError):BATCH.run(unexpected,path)
            self.assertEqual(path.read_text(),'old evidence')

if __name__=='__main__':unittest.main()
