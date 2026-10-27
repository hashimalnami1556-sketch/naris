# NARIS Stage37 — Combat animation linkage

## Actual source integration
This branch is based on `feature/stage32-combat-integration-20261027` because Stage32's C++ component is **not yet merged to main**. Merge Stage32 first, then Stage37. Do not merge a duplicate component or assume main contains it.

`UNarisCombatHitWindowNotifyState` is a native UAnimNotifyState:
- Begin calls `UNarisStage32CombatComponent::BeginHitWindow()` on the skeletal mesh owner.
- End calls `EndHitWindow()`.
- The existing Stage32 montage completion callback transitions attack/dodge into Recovery.
- A read-only editor Python audit reports skeletal mesh ↔ animation skeleton compatibility.

## Required manual asset hookups in Unreal
1. Compile `NARIS_W04Editor` with the new C++ class.
2. Add `UNarisStage32CombatComponent` to player and enemy actors, set TeamId 1 and 2.
3. Assign actual skeleton-compatible Attack and Dodge Montages to each actor.
4. On the attack Montage notify track, add `NARIS Combat Hit Window` state only across the active swing.
5. Connect Enhanced Input attack/dodge events to `StartAttack(Mesh, Montage)` / `StartDodge(Mesh, Montage)`.
6. Connect locomotion speed to the AnimBP blendspace and verify Idle→Walk→Run→Idle; animation assets cannot be fabricated from concept art.
7. Confirm the mesh's collision channel is Pawn or adapt the Stage32 sweep query; test one hit per swing and friendly-fire prevention.
8. Run the Stage37 audit and fix skeleton mismatches before PIE.

## Not yet proven
No engine build, Blueprint editing, montage placement, retargeting, collision tests, map validation or EXE has been performed on AsusRog (offline). These remain blocking gates. Notify state has not been compiled in UE5.7.
