# NARIS Expansion v2.3 — Integration and security handoff

Date: 2026-10-02. **Status: reference implementation, not production/release approved.**

## Source of truth
- Unreal W04 (`unreal/NARIS_W04/NARIS_W04.uproject`) remains the canonical Windows PC slice. Do **not** replace the existing Unreal runtime with the experimental Unity or Godot bridge.
- External reference package: `NARIS_Expansion_v2_3_Engineering_Pack.zip` (delivered separately; not yet copied into this repository). Do not mark these features merged until tested in-engine.
- Keep NARIS technical IDs stable while NARSIC remains the product brand.

## Implemented in the separately delivered reference package
- SQLite prototype player states and idempotent pass-XP events.
- Server-side guarded receipt placeholders; **no payment provider is wired**.
- An atomic `apply_prestige` update enforcing level >=100 and prestige <10, resetting XP.
- Explicit prototype erasure `delete_player`, covering players, XP events, purchase transactions, and cosmetics.
- Read-only demonstration API with ephemeral bearer token. **Not production authentication.**

## Unreal integration contract (proposed)
| Topic | Unreal owner | Boundary |
|---|---|---|
| Player level, XP, prestige | PlayerState / authoritative game subsystem | Never accept level or prestige from an untrusted client |
| Save-game | Versioned USaveGame / secure service | Do not persist bearer tokens or credit card data |
| Battle pass | Season subsystem + verified remote grants | Event IDs idempotent, claims unique by player/season/tier/track |
| Store | Entitlement subsystem | Verify receipts with official provider backend before grant |
| Titles | Data assets + progression subsystem | Validate catalog and achievement predicates |
| Analytics | Opt-in subsystem | Off by default; aggregate coarse in-level cells; retention policy |

## Release blockers
1. Verify the W04 boot-to-demo loop inside Unreal, including input, combat, collectible, gate, boss, end screen.
2. Authoritative multiplayer sync and persistent profile migration are NOT implemented.
3. Bind payment server-side verification and refunds/revocations to provider APIs before enabling checkout.
4. Secure login, audit logs, rate limits, account erasure, and backup policy required before hosting API.
5. Validate Arabic RTL font and accessibility against live in-engine UI.
6. Run cook/package/launch and capture reproducible logs and FPS/frametime evidence on target PC.

## Acceptance gate
**PUBLIC_DEMO_ALLOWED = false** until automation and manual playtests document passing results. The presence of assets, architecture documents, and green Python unit tests does not constitute a shippable Unreal build.
