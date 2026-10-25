# CALL OF NARIS — P21 Godot Prototype Staging

**Date:** 2026-10-25
**Status:** PROTOTYPE / NOT ENGINE-VERIFIED
**Owner path:** `GAME_STUDIO/prototypes/godot-p21/`
**Production source of truth:** Unreal/W04, unchanged on `main`.

## Proven work

- The independently packaged P21 Godot 4.2+ playtest extends P20 with a physics-ticked combat state machine, three provisional enemy waves, health/stamina HUD, F5/F9 save/load, waypoint save, portal goal, and camera smoothing.
- This branch stages the **combat FSM source and test suite** only. The full P21 playable scene, 5 original GLBs, and 31 reference images remain in the separate delivered ZIP package; they have **not** been pushed to this GitHub branch.
- The locally executed structural audit passed 31/31 checks; ZIP CRC passed. These checks do **not** prove GDScript parsing, gameplay functionality, Godot render output, Windows packaging or frame rate.
- Source geometry was rendered in an independent offline renderer to review shapes and original GLBs. Those PNGs are **not** screenshots from Godot.

## Integration gate

1. Add the P21 Godot scene/assets to this branch with provenance and appropriate large-asset policy.
2. Run `godot --headless --path . --editor --quit` in the Godot project root.
3. Run `godot --headless --path . --script res://tests/test_fsm.gd`.
4. Run a graphical Godot smoke test and obtain genuine viewport screenshots.
5. Verify waystone checkpoint, three-wave loop, enemy collisions and win/lose states manually.
6. Test Windows exports and performance on target hardware.
7. Only after verification, evaluate the reusable design contracts against canonical Unreal/W04.

## Outstanding

- Production rigs, weight painting, 26 polished animations per target, IK, root motion and retargeting.
- USDZ boss conversion and final GLB with rig, PBR and collision.
- Final modular environment, PBR maps, navigation AI and optimization.
- Verified engine build, FPS benchmark, release and installer.

**Do not merge this prototype into `main` until ownership and QA gates pass.**
