# NARIS W04 Unreal Bootstrap

This directory is the engine-facing bootstrap layer for the W04 Bone Beast vertical slice.

## Current repository state
The repository currently does **not** contain a `.uproject` or Unreal `Source/` module. Therefore this bootstrap intentionally does not claim to be a compilable Unreal project yet.

## Target module
`NARIS_W04`

## Target content root
`Content/NARIS/W04/Bosses/BoneBeast/`

## Integration order
1. Create/open the Unreal project.
2. Add the `NARIS_W04` C++ module.
3. Move the scaffold headers/cpp from `docs/W04_VERTICAL_SLICE/` into the module's source tree.
4. Register Gameplay Tags.
5. Create `DA_BoneBeast` and phase/attack data.
6. Create the Blueprint actor and components.
7. Bind Animation Notify events to the authoritative event bridge.
8. Connect Niagara, Audio, UI and Quest consumers.
9. Run the W04 QA matrix.

## Non-negotiable authority rule
Boss phase/state is owned by gameplay code. Animation, VFX, Audio, UI and Quest systems consume events and never author phase state.
