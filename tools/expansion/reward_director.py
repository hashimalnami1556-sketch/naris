"""Durable presentation queue for NARIS rewards. Does not grant economy value."""
import json
class RewardDirector:
    KINDS={"boss","exploration","achievement","loot","challenge","battle_pass"}
    def __init__(self,repo):
        self.repo=repo
        with repo._connect() as db: db.execute("""CREATE TABLE IF NOT EXISTS reward_director_events(event_id TEXT PRIMARY KEY,player_id TEXT NOT NULL REFERENCES players(id),kind TEXT NOT NULL,source_id TEXT NOT NULL,payload TEXT NOT NULL,priority INTEGER NOT NULL,acked INTEGER NOT NULL DEFAULT 0)""")
    def _player(self,db,p):
        if db.execute("SELECT 1 FROM players WHERE id=?",(p,)).fetchone() is None: raise KeyError("player missing")
    def enqueue(self,p,event_id,kind,source_id,payload):
        if not event_id or kind not in self.KINDS or not source_id or not isinstance(payload,dict): raise ValueError("invalid event")
        body=json.dumps(payload,sort_keys=True,separators=(",",":"),ensure_ascii=True)
        rarity=payload.get("rarity"); priority=100 if rarity=="legendary" else 80 if rarity=="epic" else 70 if kind=="boss" else 60 if kind=="achievement" else 40
        with self.repo._connect() as db:
            db.execute("BEGIN IMMEDIATE");self._player(db,p)
            old=db.execute("SELECT player_id,kind,source_id,payload FROM reward_director_events WHERE event_id=?",(event_id,)).fetchone()
            if old:
                if tuple(old)!=(p,kind,source_id,body): raise PermissionError("event replay mismatch")
                return False
            db.execute("INSERT INTO reward_director_events VALUES(?,?,?,?,?,?,0)",(event_id,p,kind,source_id,body,priority));return True
    @staticmethod
    def _row(r): return None if r is None else {"event_id":r["event_id"],"kind":r["kind"],"source_id":r["source_id"],"payload":json.loads(r["payload"]),"priority":r["priority"]}
    def peek(self,p):
        with self.repo._connect() as db:self._player(db,p);return self._row(db.execute("SELECT * FROM reward_director_events WHERE player_id=? AND acked=0 ORDER BY priority DESC,rowid ASC LIMIT 1",(p,)).fetchone())
    def ack(self,p,event_id):
        with self.repo._connect() as db:self._player(db,p);return db.execute("UPDATE reward_director_events SET acked=1 WHERE player_id=? AND event_id=? AND acked=0",(p,event_id)).rowcount==1
