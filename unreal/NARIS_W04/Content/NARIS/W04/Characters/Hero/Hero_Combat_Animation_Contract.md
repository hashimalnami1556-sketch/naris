# Hero combat animation contract

Target: W04 hero combat integration.

## Runtime authority

Gameplay damage remains owned by `ANarisHeroCharacter` and the combat components.
Animation assets control *when* an authored attack may commit its hit.

Production animation sequence:

1. Input calls `LightAttack()` or `HeavyAttack()`.
2. C++ records `ENarisAttackKind` and emits `OnAttackRequested`.
3. The animation/montage begins.
4. Add `NARIS Attack Hit Window` (`UNarisAttackWindowNotifyState`) over the valid contact interval.
5. Add one `NARIS Attack Impact` (`UNarisAttackImpactNotify`) at the authored contact frame.
6. Impact calls `CommitPendingAttackHit()`.
7. Only the first impact inside the open window is accepted.
8. Window end clears the pending attack.

## Smoke fallback

`bImmediateSmokeAttackHit=true` exists only so the generated W04 smoke map remains playable before final animation assets are authored. It drives the exact same Open -> Commit -> Close code path immediately.

For production hero Blueprints/animation assets, set `bImmediateSmokeAttackHit=false` and use the native notifies above.

## Acceptance

- No hit before the window opens.
- No hit after the window closes.
- No duplicate hit from the same attack window.
- Light/Heavy tuning remains in the hero C++/Blueprint properties.
- Resonance reward is granted only after a successful committed hit.
- Lock-on/range validation remains authoritative in gameplay C++.
