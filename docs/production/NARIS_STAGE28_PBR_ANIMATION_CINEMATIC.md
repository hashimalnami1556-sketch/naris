# NARIS Stage 28 — PBR, animation preservation, cinematic handoff (2026-10-27)

Source: the 23 actual GLB files in Stage27 (10 characters, 12 props, 1 environment), not extracted 3D from the reference JPEGs. Original source GLBs have **zero glTF materials/textures**. Stage28 writes new GLBs with embedded procedural 256px PBR base-color, ORM, neutral-normal textures, a bound glTF material for each primitive, and planar UV0 where absent. All 60 source animation clips and 10 skins are preserved structurally. This is a **prototype appearance baseline**, not hand-painted production art or verified Unreal deformation.

## Installation
Download `NARIS_STAGE28_MATERIALS_ANIMATION_CINEMATICS.zip`. Extract it to `C:\Users\Admin\NARIS_CANON\Stage28` (so `Assets_PBR`, `Tools`, and `Reports` are direct children). In Unreal 5.7 with Python Editor Script Plugin and glTF/Interchange import enabled, run `Tools/Install-Stage28-InUnreal.py`. Imports into `/Game/NARIS/_Import/Stage28_PBR`, never overwrites W04 production maps. Then inspect `Saved/TestReports/naris_stage28_unreal_import.json`. Do not interpret the offline GLB checks as an engine pass.

## Animation
10 characters contain a total of 60 glTF animation clips; no new hand-authored animations or reliable retargeting are claimed. Engine validation must verify imported AnimationSequences, skeleton consistency, montage state, socket, foot contact and root motion. Importing animations does not automatically attach an Animation Blueprint to map actors.

## Cinematics / montage
`Reports/cinematic_shotlist.json` is a timed shot plan for Ashen Forest intro (7 shots); `Tools/Create-Stage28-Cinematic-InUnreal.py` creates a new LevelSequence asset and camera actors in an open staging level, for subsequent manual shot/camera-cut verification. It does not render a final video.

## Gates
Offline GLB validation: pass. Unreal import: unrun. Material appearance and animation deformation: unrun. Sequencer preview/render: unrun. Final W04 map and Windows shipping build: not approved. AsusRog remote host was offline at inspection.
