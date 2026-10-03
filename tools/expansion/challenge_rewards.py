"""NARIS server-authoritative challenge reward reference."""
from dataclasses import dataclass
from datetime import date,timedelta

@dataclass(frozen=True)
class ChallengeDefinition:
    challenge_id:str; cadence:str; metric:str; target:int; tokens:int
    def __post_init__(self):
        if self.cadence not in ("daily","weekly") or not self.challenge_id or not self.metric: raise ValueError("invalid challenge")
        if type(self.target) is not int or self.target<=0 or type(self.tokens) is not int or self.tokens<=0: raise ValueError("invalid challenge values")

class ChallengeService:
    def __init__(self,repo,definitions):
        self.repo=repo; self.defs={d.challenge_id:d for d in definitions}
        if len(self.defs)!=len(definitions): raise ValueError("duplicate challenge id")
        with repo._connect() as db:
            db.executescript("""CREATE TABLE IF NOT EXISTS challenge_events(event_id TEXT PRIMARY KEY,player_id TEXT NOT NULL REFERENCES players(id),metric TEXT NOT NULL,amount INTEGER NOT NULL,event_day TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS challenge_claims(player_id TEXT NOT NULL REFERENCES players(id),challenge_id TEXT NOT NULL,period_key TEXT NOT NULL,tokens INTEGER NOT NULL,PRIMARY KEY(player_id,challenge_id,period_key));
CREATE TABLE IF NOT EXISTS challenge_wallet(player_id TEXT PRIMARY KEY REFERENCES players(id),balance INTEGER NOT NULL CHECK(balance>=0));
CREATE TABLE IF NOT EXISTS challenge_milestones(player_id TEXT NOT NULL REFERENCES players(id),milestone INTEGER NOT NULL,tokens INTEGER NOT NULL,PRIMARY KEY(player_id,milestone));""")
    @staticmethod
    def _day(v):
        try:return date.fromisoformat(v)
        except (TypeError,ValueError):raise ValueError("invalid day")
    @staticmethod
    def _period(c,d):
        if c=="daily":return d.isoformat()
        y,w,_=d.isocalendar();return f"{y}-W{w:02d}"
    def _player(self,db,p):
        if not isinstance(p,str) or not p:raise ValueError("invalid player")
        if db.execute("SELECT 1 FROM players WHERE id=?",(p,)).fetchone() is None:raise KeyError("unknown player")
    def record_progress(self,p,metric,amount,event_id,event_day):
        day=self._day(event_day)
        if not isinstance(metric,str) or not metric or type(amount) is not int or not 0<amount<=100000:raise ValueError("invalid progress")
        if not isinstance(event_id,str) or not 1<=len(event_id)<=128:raise ValueError("invalid event")
        with self.repo._connect() as db:
            db.execute("BEGIN IMMEDIATE");self._player(db,p)
            old=db.execute("SELECT player_id,metric,amount,event_day FROM challenge_events WHERE event_id=?",(event_id,)).fetchone()
            if old:
                if tuple(old)!=(p,metric,amount,day.isoformat()):raise PermissionError("event replay mismatch")
                return False
            db.execute("INSERT INTO challenge_events VALUES(?,?,?,?,?)",(event_id,p,metric,amount,day.isoformat()));return True
    def _progress(self,db,p,d,day):
        if d.cadence=="daily":start=end=day
        else:start=day-timedelta(days=day.weekday());end=start+timedelta(days=6)
        n=db.execute("SELECT COALESCE(SUM(amount),0) n FROM challenge_events WHERE player_id=? AND metric=? AND event_day BETWEEN ? AND ?",(p,d.metric,start.isoformat(),end.isoformat())).fetchone()["n"]
        return min(d.target,int(n))
    def reward_inbox(self,p,event_day):
        day=self._day(event_day);out=[]
        with self.repo._connect() as db:
            self._player(db,p)
            for d in self.defs.values():
                key=self._period(d.cadence,day)
                if self._progress(db,p,d,day)>=d.target and not db.execute("SELECT 1 FROM challenge_claims WHERE player_id=? AND challenge_id=? AND period_key=?",(p,d.challenge_id,key)).fetchone():
                    out.append({"challenge_id":d.challenge_id,"cadence":d.cadence,"period":key,"tokens":d.tokens})
        return sorted(out,key=lambda x:(x["cadence"],x["challenge_id"]))
    def claim_all(self,p,event_day):
        day=self._day(event_day);count=total=0
        with self.repo._connect() as db:
            db.execute("BEGIN IMMEDIATE");self._player(db,p)
            for d in self.defs.values():
                if self._progress(db,p,d,day)<d.target:continue
                key=self._period(d.cadence,day)
                if db.execute("INSERT OR IGNORE INTO challenge_claims VALUES(?,?,?,?)",(p,d.challenge_id,key,d.tokens)).rowcount:
                    count+=1;total+=d.tokens
            if total:db.execute("INSERT INTO challenge_wallet VALUES(?,?) ON CONFLICT(player_id) DO UPDATE SET balance=balance+excluded.balance",(p,total))
        return {"claimed":count,"tokens":total}
    def wallet_balance(self,p):
        with self.repo._connect() as db:
            self._player(db,p);r=db.execute("SELECT balance FROM challenge_wallet WHERE player_id=?",(p,)).fetchone();return int(r["balance"]) if r else 0
    def _days(self,db,p):
        ids=[d.challenge_id for d in self.defs.values() if d.cadence=="daily"]
        if not ids:return []
        q="SELECT DISTINCT period_key FROM challenge_claims WHERE player_id=? AND challenge_id IN (%s) ORDER BY period_key"%(",".join("?"*len(ids)))
        return [date.fromisoformat(r["period_key"]) for r in db.execute(q,(p,*ids))]
    def streak(self,p,event_day):
        day=self._day(event_day)
        with self.repo._connect() as db:self._player(db,p);days=set(self._days(db,p))
        n=0
        while day in days:n+=1;day-=timedelta(days=1)
        return n
    def milestone_tokens(self,p):
        with self.repo._connect() as db:
            db.execute("BEGIN IMMEDIATE");self._player(db,p);m=(len(self._days(db,p))//7)*7
            if m<7 or not db.execute("INSERT OR IGNORE INTO challenge_milestones VALUES(?,?,300)",(p,m)).rowcount:return 0
            db.execute("INSERT INTO challenge_wallet VALUES(?,300) ON CONFLICT(player_id) DO UPDATE SET balance=balance+300",(p,));return 300
