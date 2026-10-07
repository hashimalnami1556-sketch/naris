#!/usr/bin/env python3
"""Render NARSIC production progress into an ultrawide HTML monitor.

No third-party dependencies are required.
Planning percentages are never treated as QA/runtime evidence.
"""
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA = ROOT / "data" / "PRODUCTION_PROGRESS.json"
DEFAULT_OUT = ROOT / "generated_designs" / "production_dashboard" / "NARSIC_PROGRESS_REPORT.html"

def esc(value: object) -> str:
    return html.escape(str(value))

def bar(percent: int) -> str:
    p = max(0, min(100, int(percent)))
    return f'<div class="bar"><span style="width:{p}%"></span></div>'

def render(data: dict) -> str:
    current = data["current_stage"]
    stages = "".join(
        f'<div class="stage {esc(s["state"])}"><b>{esc(s["label"])}</b>'
        f'<small>{esc(s["state"]).upper()}</small></div>'
        for s in data["stages"]
    )
    streams = "".join(
        f'<div class="row"><span>{esc(w["label"])}</span>{bar(w["display_percent"])}'
        f'<b>{int(w["display_percent"])}%</b></div>'
        for w in data["workstreams"]
    )
    blockers = "".join(f"<li>{esc(x)}</li>" for x in data["blockers"])
    actions = "".join(f"<li>{esc(x)}</li>" for x in data["next_actions"])

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>NARSIC Production Monitor</title>
<style>
:root{{--panel:#0b1119e8;--line:#263244;--gold:#ff9f2f;--green:#40db8a;--muted:#8996a8}}
*{{box-sizing:border-box}}
body{{margin:0;background:radial-gradient(circle at 62% 18%,#35170d 0,#0a1018 38%,#040609 75%);color:#eef3f8;font:15px/1.35 Segoe UI,Arial,sans-serif;min-height:100vh}}
.shell{{display:grid;grid-template-columns:18% 57% 25%;min-height:100vh;border-top:3px solid #a50c26}}
.panel{{background:var(--panel);border:1px solid var(--line);padding:22px;overflow:auto}}
.center{{padding:40px;display:flex;flex-direction:column;justify-content:space-between}}
.brand{{font:64px Georgia,serif;letter-spacing:.2em;color:#f5d1aa;text-shadow:0 0 28px #ff762866}}
.kicker{{letter-spacing:.28em;color:#e2aa63}}
.hero h1{{font-size:34px}}
.hero p{{color:#aab6c5}}
.bar{{height:9px;background:#202a36;border:1px solid #354356;overflow:hidden}}
.bar span{{display:block;height:100%;background:linear-gradient(90deg,#b95c18,#ffd070);box-shadow:0 0 14px #ff9f2f88}}
.row{{display:grid;grid-template-columns:42% 1fr 48px;gap:10px;align-items:center;margin:13px 0}}
.stage{{padding:13px;border-left:3px solid #3b4655;margin:9px 0;background:#0a1017}}
.stage small{{display:block;color:var(--muted)}}
.stage.complete{{border-color:var(--green)}}
.stage.active{{border-color:var(--gold);box-shadow:inset 0 0 22px #ff9f2f16}}
.stage.locked{{opacity:.52}}
h2{{font:20px Georgia,serif;color:#efb45d;letter-spacing:.05em}}
li{{margin:9px 0}}
.footer{{display:flex;justify-content:space-between;color:#8d99aa}}
@media(max-aspect-ratio:2/1){{.shell{{grid-template-columns:24% 46% 30%}}.brand{{font-size:42px}}}}
</style>
</head>
<body>
<div class="shell">
<aside class="panel"><div class="kicker">DEVELOPMENT PIPELINE</div>{stages}</aside>
<main class="center">
<div><div class="brand">NARSIC</div></div>
<section class="hero">
<div class="kicker">CURRENT PHASE</div>
<h1>{esc(current["label"])} — {int(current["display_progress_percent"])}%</h1>
<p>Planning indicator only. Runtime, build and QA evidence remain separate gates.</p>
{bar(current["display_progress_percent"])}
</section>
<div class="footer"><span>{esc(data["canonical_engine"])} / {esc(data["primary_platform"])}</span><span>UPDATED {esc(data["updated_at"])}</span></div>
</main>
<aside class="panel"><h2>CORE WORKSTREAMS</h2>{streams}<h2>BLOCKERS / MISSING</h2><ul>{blockers}</ul><h2>NEXT ACTIONS</h2><ol>{actions}</ol></aside>
</div>
</body>
</html>"""

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    data = json.loads(args.data.read_text(encoding="utf-8"))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(render(data), encoding="utf-8")
    print(args.out)

if __name__ == "__main__":
    main()
