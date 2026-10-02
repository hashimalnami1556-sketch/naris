# NARIS Rewards v2.6 — Season migration and cosmetic redemption gate

2026-10-02 • Implementation in conversation artifact **NARIS_Expansion_v2_6_Season_Rewards.zip**. The full Python implementation is NOT committed to this GitHub branch. Never claim Unreal features are running based on reference tests.

## Change from v2.5
- Separate `season_progress(player_id,season,xp,premium)` so S02 never inherits old S01 values.
- Deduplicate XP by globally unique trusted `event_id` (reject cross-player/season replay).
- Unlock tier with `min(100,1+floor(xp/1000))`.
- Grant virtual cosmetic tokens once per player/season/tier/track in one SQLite transaction.
- Redeem allowlisted cosmetic once with request idempotency key, validated server catalog price, sufficient funds, and unique item ownership.
- Support retries after SQLite failures without loss or double spending.
- Extend prototype account deletion to season state, events, deliveries, balances, redemptions and inventory.

## Acceptance evidence
Local reference suite: **32 passing tests** using Python unittest, including injected inventory database failure, wallet rollback and retry. ZIP contains 20 files, internal archive integrity verified. This is neither engine QA nor GitHub CI evidence.

## Risk and migration rule
Legacy v2.5 columns `players.pass_xp` and `players.premium` have no season provenance; do **not** backfill a new season automatically. The `enable_premium_from_verified_entitlement` method is only a trusted adapter hook; there is no implemented payment-provider validation. Tokens have no cash value. The existing Unreal/W04 Windows project remains canonical; do not overwrite the dirty AsusRog working tree.

## Next Unreal tasks
1. Server authority for XP, claims, inventory and purchases; verified event identity.
2. UDataAsset seasonal catalog and explicit provider entitlement adapter.
3. UMG season pass, claims, equipment and cosmetic preview; Arabic RTL and accessibility.
4. Transaction logs, refunds/revocation and secure backup/account-erasure process.
5. Packaged W04 gameplay and automation/economy exploit testing.

**PUBLIC_DEMO_ALLOWED = false** until Unreal gameplay and production security gates pass.
