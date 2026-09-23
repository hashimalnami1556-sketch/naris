# W04 PLAYABLE ASSEMBLY

## Canonical runtime flow

Main Menu -> Intro -> Forest Entrance / Wake Area -> Broken Shrine / Memory Crystal -> Ruined Bridge -> Whisper Lake -> Ash Gate -> Celestial Wolf -> Bone Beast Arena -> Demo End.

This ordering is authoritative for the current W04 vertical slice because it matches:
- `LEVEL_LAYOUT.json` zone order.
- Corrupted Heart quest steps in runtime/acceptance tests.
- Packaged runtime smoke progression.

## Quest / progression mapping

1. `Z01_FOREST_ENTRANCE` — spawn, movement/combat onboarding, Waystone checkpoint.
2. `Z02_BROKEN_SHRINE` — Memory Crystal, First Whisper narrative trigger, Corrupted Heart step 1.
3. `Z03_RUINED_BRIDGE` — traversal/gating transition toward Whisper Lake.
4. `Z04_WHISPER_LAKE` — Celestial Wolf reveal space; the bond is only committed after the Ash Gate progression condition is satisfied.
5. `Z05_ASH_GATE` — Ash Gate progression gate, Corrupted Heart step 2.
6. Return/transition into the companion beat — Celestial Wolf bond, Corrupted Heart step 3.
7. `Z06_BONE_BEAST_ARENA` — encounter start/lock, Bone Beast defeat, Corrupted Heart step 4 + completion, Demo End.

The spatial order remains Z04 -> Z05 -> Z06. The companion reveal may be staged visually at Whisper Lake before the actual bond state is granted, but gameplay progression must not skip the Ash Gate condition.

## World requirements

- Third-person navigation.
- Traversable combat spaces.
- Navigation mesh for hero and Bone Beast.
- Streaming-ready layout.
- Lighting target: Lumen.
- Geometry target: Nanite where appropriate.
- Volumetric fog and ash atmosphere.
- Encounter boundaries and checkpoint.
- Production Shipping map: `/Game/NARIS/W04/Maps/W04_AshenForest`.
- Development blockout map: `/Game/NARIS/W04/Maps/W04_AshenForest_Blockout`.
- Runtime smoke map: `/Game/NARIS/W04/Maps/W04_Prototype`.

## Shipping rule

`W04_Prototype` and `W04_AshenForest_Blockout` are development evidence only. Shipping must validate and cook `W04_AshenForest`.
