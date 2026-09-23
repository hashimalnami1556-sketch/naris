# W04 Presentation Binding Contract

## Authority

Gameplay state is authoritative. Presentation code may observe events and play effects, sound, camera feedback, animation, UI, or Sequencer content; it must not independently change boss phase, quest state, companion progression, save state, or DemoEnd.

## Runtime bus

`UNarisPresentationComponent` owns a list of `FNarisPresentationCue` payloads.

Each payload may contain:
- Niagara system;
- sound / MetaSound-derived sound asset;
- camera shake class;
- volume, pitch and shake falloff tuning.

Calling `TriggerCue` always broadcasts `OnCueTriggered`, even when no authored payload exists. This keeps smoke builds playable and gives Blueprints/Sequencer a stable integration point.

## Authoritative producers

- Hero: attack impacts, parry, dodge, hit reaction, resonance burst, essence switch.
- Celestial Wolf: mode changes, bond, attack/impact, EchoLink pulse.
- Bone Beast: encounter, damage, attack request/impact, phase transition, death, completion.
- Boss Arena: lock, unlock, phase transition, boss death, DemoEnd.

## Asset identity

Canonical cue-to-asset bindings live in:
`Content/NARIS/W04/Presentation/W04_PresentationCueManifest.json`.

Every referenced asset ID must exist exactly once in:
`data/MASTER_ASSET_REGISTRY.json`.

The cue manifest is a production contract, not evidence that the corresponding .uasset has been authored or loaded successfully.

## Bone Beast attacks

Attack names remain data-driven by `FNarisBossAttackDefinition.AttackId`.
Runtime cue shape:

`Boss.Attack.<AttackId>`

No fixed attack names should be invented in presentation code.

## Production binding flow

1. Author/import Niagara, Audio/MetaSound and CameraShake assets.
2. Keep their immutable NARIS IDs aligned with the master registry.
3. Configure the actor/Blueprint's `UNarisPresentationComponent.Cues`.
4. Bind optional `OnCueTriggered` listeners for UI, Sequencer or additional presentation.
5. Verify in editor and packaged Windows build.
6. Capture visual/audio/RTL/performance evidence before closing the presentation gate.
