import copy
import hashlib
from pathlib import Path
import tempfile
import unittest

from validate_collision_candidate import inspect_report


class CandidateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'asset.glb').write_bytes(b'fixture')
        self.row = {'source': 'asset.glb', 'sha256': hashlib.sha256(b'fixture').hexdigest(), 'measured_concavity': .02}

    def check(self, row):
        return inspect_report([row], self.root)

    def test_acceptable_measurement_never_promotes_runtime(self):
        result = self.check(self.row)
        self.assertEqual(result['precision_status'], 'MEASUREMENT_CHECK_ACCEPTED')
        self.assertFalse(result['runtime_promotion_allowed'])

    def test_missing_and_invalid_measurements_fail_closed(self):
        for value in (None, True, float('nan'), float('inf'), -.01, '.02'):
            with self.subTest(value=value):
                row = dict(self.row, measured_concavity=value)
                self.assertEqual(self.check(row)['precision_status'], 'REJECTED')

    def test_failed_geometry_cannot_be_overridden_by_report_target(self):
        row = dict(self.row, measured_concavity=.114, target_concavity=1, runtime_promotion_allowed=True)
        self.assertEqual(self.check(row)['precision_status'], 'REJECTED')

    def test_modified_source_rejected(self):
        (self.root / 'asset.glb').write_bytes(b'changed')
        self.assertEqual(self.check(self.row)['precision_status'], 'REJECTED')

    def test_unsafe_missing_and_duplicate_sources_rejected(self):
        for name in ('../asset.glb', 'missing.glb', 'x\\asset.glb', ''):
            self.assertEqual(self.check(dict(self.row, source=name))['precision_status'], 'REJECTED')
        self.assertEqual(inspect_report([self.row, copy.copy(self.row)], self.root)['precision_status'], 'REJECTED')

    def test_upstream_failure_is_preserved(self):
        self.assertEqual(self.check(dict(self.row, precision_gate='FAIL'))['precision_status'], 'REJECTED')

    def test_empty_report_rejected(self):
        with self.assertRaises(ValueError):
            inspect_report([], self.root)


if __name__ == '__main__':
    unittest.main()
