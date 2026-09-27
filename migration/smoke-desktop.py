from pathlib import Path
import subprocess,time,json,hashlib
root=Path(r"C:\Users\Admin\NARIS")
out=Path(r"C:\Users\Admin\NARIS_AUDIT_20260927\docs\production")
saves=root/"Saved/SaveGames"
def hashes():return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in saves.glob("*.sav") if not p.name.startswith("NARIS_Smoke")}
before=hashes()
log=root/"Saved/Logs/AuditSmoke_20260927.log"
exe=r"C:\Program Files\Epic Games\UE_5.7\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
proc=subprocess.Popen([exe,str(root/"NARIS.uproject"),"-game","-unattended","-nullrhi","-nosound","-NarisQuestSmoke","-abslog="+str(log)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
text=""
try:
 for i in range(60):
  time.sleep(1)
  text=log.read_text(encoding="utf-8",errors="replace") if log.exists() else ""
  if "NARIS_QUEST_SMOKE PASS" in text or "NARIS_QUEST_SMOKE FAIL" in text or proc.poll() is not None:break
finally:
 if proc.poll() is None:
  proc.terminate()
  try:proc.wait(timeout=10)
  except subprocess.TimeoutExpired:proc.kill();proc.wait()
after=hashes()
markers=[x for x in text.splitlines() if any(k in x for k in ["NARIS_QUEST_SMOKE","NARIS_RELEASE_GATE","NARIS_RUNTIME_READY","Fatal error"])]
report={"date":"2026-09-27","scope":"UE5.7 editor game headless; not packaged or visual QA","smoke_pass":"NARIS_QUEST_SMOKE PASS" in text,"player_saves_unchanged":before==after,"markers":markers}
(out/"desktop-runtime-evidence.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print(json.dumps(report,indent=2))
