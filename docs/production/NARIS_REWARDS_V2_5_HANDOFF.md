# NARIS Rewards v2.5 — implementation gate

**2026-10-02.** Local delivery bundle: `NARIS_Expansion_v2_5_Atomic_Rewards.zip` (shared in conversation; **not uploaded to GitHub**). Python/SQLite reference only.

## Completed and locally verified
- `backend/rewards.py` adds strict 100-tier S01 draft catalog validation and `RewardService.collect()`.
- Eligibility from persisted XP and Premium entitlement (not client-supplied fields).
- SQLite immediate transaction: delivery receipt, claim marker, and cosmetic-token wallet credit commit or rollback together.
- Unique player/season/tier/track fulfillment prevents duplicate awards after restart.
- Legacy v2.4 claims without fulfilled delivery receipt can be credited exactly once.
- Erasure covers prototype wallet/deliveries. Per-player balances are isolated.
- Local Python suite: 23 passing unittest cases, including injected SQLite failure and retry.
- Original `claim_pass_reward()` still records a claim **without** credit; callers must not treat it as delivery.

## Explicit production blockers
- **No Unreal Engine runtime bridge** and no Windows build/playtest verification.
- The wallet is a game-only cosmetic-token reference; it does not implement redemption, currencies with monetary value, or a real store.
- Historical `premium` and `pass_xp` fields are not season scoped. S02 must not launch on this data model.
- The earlier `verified=True` flag is **not** payment-provider verification. Never make it a client-facing API.
- Freeze/catalog-sign real season data, then perform migration, security tests, load tests, admin audit and refunds/revocations.
- Keep W04 / Unreal canonical, do not overwrite AsusRog's dirty working tree or declare shipping success.

Release gate: **PUBLIC_DEMO_ALLOWED = false** until engine QA passes.
