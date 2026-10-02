"""Unit tests for the engine-neutral claim ledger. Run: python -m unittest discover -s tools/expansion -p 'test_*.py'"""
import importlib.util
import sqlite3
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("claims", Path(__file__).with_name("battle_pass_claims.py"))
claims = importlib.util.module_from_spec(spec)
spec.loader.exec_module(claims)


class ClaimLedgerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "claims.db"
        self.db = sqlite3.connect(self.path)

    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()

    def test_duplicate_claim_remains_blocked_after_reopen(self):
        args = ("p1", "s01", 1, "free", 0, False)
        self.assertTrue(claims.claim_reward(self.db, *args))
        self.db.close()
        self.db = sqlite3.connect(self.path)
        self.assertFalse(claims.claim_reward(self.db, *args))
        self.assertEqual(claims.claims_for_player(self.db, "p1", "s01"), [(1, "free")])

    def test_ineligible_premium_and_locked_tier_are_not_recorded(self):
        self.assertFalse(claims.claim_reward(self.db, "p1", "s01", 2, "free", 0, False))
        self.assertFalse(claims.claim_reward(self.db, "p1", "s01", 1, "premium", 0, False))
        self.assertEqual(claims.claims_for_player(self.db, "p1", "s01"), [])

    def test_earned_tier_and_verified_premium(self):
        self.assertTrue(claims.claim_reward(self.db, "p1", "s01", 2, "free", 1000, False))
        self.assertTrue(claims.claim_reward(self.db, "p1", "s01", 2, "premium", 1000, True))

    def test_reject_bad_tier(self):
        with self.assertRaises(ValueError):
            claims.claim_reward(self.db, "p1", "s01", True, "free", 0, False)


if __name__ == "__main__":
    unittest.main()
