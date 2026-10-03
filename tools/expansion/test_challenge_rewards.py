import importlib.util,sqlite3,tempfile,unittest
from contextlib import contextmanager
from pathlib import Path
spec=importlib.util.spec_from_file_location("cr",Path(__file__).with_name("challenge_rewards.py"));cr=importlib.util.module_from_spec(spec);spec.loader.exec_module(cr)
class Repo:
 def __init__(self,p):
  self.p=p
  with self._connect() as d:d.execute("CREATE TABLE players(id TEXT PRIMARY KEY)")
 @contextmanager
 def _connect(self):
  d=sqlite3.connect(self.p);d.row_factory=sqlite3.Row
  try:yield d;d.commit()
  except: d.rollback();raise
  finally:d.close()
class T(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.r=Repo(Path(self.t.name)/"x.db")
  with self.r._connect() as d:d.execute("INSERT INTO players VALUES('p')")
  self.s=cr.ChallengeService(self.r,[cr.ChallengeDefinition("d","daily","kills",10,50),cr.ChallengeDefinition("w","weekly","kills",50,200)])
 def tearDown(self):self.t.cleanup()
 def test_event_idempotency_inbox_and_claim_all(self):
  self.assertTrue(self.s.record_progress("p","kills",10,"e","2026-10-03"));self.assertFalse(self.s.record_progress("p","kills",10,"e","2026-10-03"))
  self.assertEqual(self.s.reward_inbox("p","2026-10-03")[0]["challenge_id"],"d")
  self.assertEqual(self.s.claim_all("p","2026-10-03"),{"claimed":1,"tokens":50});self.assertEqual(self.s.claim_all("p","2026-10-03"),{"claimed":0,"tokens":0})
 def test_streak_and_seven_day_milestone(self):
  from datetime import date,timedelta
  for i in range(7):
   day=str(date(2026,10,1)+timedelta(days=i));self.s.record_progress("p","kills",10,f"e{i}",day);self.s.claim_all("p",day)
  self.assertEqual(self.s.streak("p","2026-10-07"),7);self.assertEqual(self.s.milestone_tokens("p"),300);self.assertEqual(self.s.milestone_tokens("p"),0);self.assertEqual(self.s.wallet_balance("p"),650)
 def test_replay_mismatch_rejected(self):
  self.s.record_progress("p","kills",1,"x","2026-10-03")
  with self.assertRaises(PermissionError):self.s.record_progress("p","kills",2,"x","2026-10-03")
if __name__=="__main__":unittest.main()
