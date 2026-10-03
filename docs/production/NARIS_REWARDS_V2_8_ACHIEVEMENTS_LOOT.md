# NARIS Rewards v2.8 — Achievements, World Rewards & Loot Pity

Date: 2026-10-03. Reference artifact: `NARIS_Expansion_v2_8_Achievement_Loot.zip`.

## Locally verified reference behavior
- Public + secret achievements from idempotent metric events.
- Claim-once achievement token rewards and pending achievement inbox.
- Exactly-once boss/exploration rewards; event replay with changed payload is rejected.
- Persistent loot result per event ID across restart.
- Persistent pity counters: Epic-or-better by pull 8; Legendary by pull 20.
- Account erasure covers achievement, world-reward, pity and loot records.
- Full Python reference suite: **48/48 tests passed** with ResourceWarning treated as error.
- ZIP: 28 files/entries, internal integrity check PASS.

## W04 draft hooks
- Memory Crystal 01: 40 cosmetic tokens.
- First Whisper: 60.
- Celestial Wolf: 150.
- Bone Beast: 300.
- Ash Gate completion: 125.
These values are balancing drafts, not production economy commitments.

## Unreal integration boundary
Unreal W04 remains canonical. Runtime must issue trusted unique event IDs for kills, discoveries, boss completion and exploration. Never accept token amount, rarity, achievement completion, pity counters, or loot outcome from an untrusted client. No Unreal subsystem/UMG implementation, hosted authority, cryptographic event signing, live balancing telemetry, or packaged Windows QA is proven by these Python tests.

**PUBLIC_DEMO_ALLOWED = false** until engine/runtime QA passes.
