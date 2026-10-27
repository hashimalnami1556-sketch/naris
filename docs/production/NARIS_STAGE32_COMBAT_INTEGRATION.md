# NARIS Stage 32 — real source integration and release boundary

This stage is a **C++ source change in the actual UE5.7 repository**, unlike previous ZIP-only deliveries. It is not a compiled binary or a claim of gameplay readiness.

## Changes
- Add `UNarisStage32CombatComponent` with montage-first atomic stamina commitment.
- Bind montage end callback so Attack/Dodge can transition to Recovery automatically.
- Clear the montage delegate on teardown, interruption and death.
- Apply one damage event per target per swing; reject NaN/negative damage.
- Add team IDs, friendly-fire gate, dodge invulnerability, stamina regeneration, Blueprint vitals event.
- Add 10 offline source contract tests and GitHub Actions source-contract workflow.

## Important integration constraints
1. Default TeamId=0 on **both actors prevents damage**. Assign player TeamId=1 and enemy TeamId=2 in Blueprint.
2. Montage must be valid and playing. Wire attack and dodge Enhanced Input actions to StartAttack/StartDodge and pass the actual mesh and montage.
3. Place AnimNotify calls to BeginHitWindow/EndHitWindow at exact attack frames.
4. Call CancelAction when another system interrupts the montage, or stop the montage so OnMontageEnded executes.
5. This is a **new** component; remove the older Stage30/31 components from actors before enabling Stage32 to prevent duplicate damage logic.
6. Use the original repo's Unreal editor build and strict map validation. No assertion of 30/60 FPS performance or shipping EXE is made.
7. C++ implementation is uncompiled in this environment and requires UE5.7 API/build validation on the Windows host. The connected AsusRog host was offline when checked.

## Next production gates
- UE C++ compile, create Blueprint actor and montage wiring, PIE input/combat checks.
- Import Stage29 map and Stage30 materials, author final UV-linked textures, collision and NavMesh.
- Reconcile hero and guardian skeletons and inspect deformation and animation root motion.
- Pass W04 shipping-map validator, BuildCookRun and Windows EXE smoke tests.
