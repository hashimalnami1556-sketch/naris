# Stage 28 W04 authoring preview — 2026-10-27

Source: Stage26 Ashen Forest candidate GLB, preserved in the separately downloadable Stage28 ZIP.

This commit adds an Unreal Editor Python preview-level authoring script, and the required six-zone authoring contract. **It creates TargetPoint markers, not playable bosses, enemies, interaction systems or a final map.** The geometry must be imported and assembled; collisions, navmesh, materials, animations and gameplay need real PIE validation.

Run only with UE5.7 installed on Windows. Copy contract to `unreal/NARIS_W04/Stage28/STAGE28_W04_AUTHORING_CONTRACT.json`; script resides in `Content/Python/`. The script refuses to overwrite a pre-existing preview map and never writes to `/Game/NARIS/W04/Maps/W04_AshenForest`.

Offline bundle contains the actual candidate GLB, tests (6/6 pass), source SHA256 and handoff guide. **No .umap or EXE was generated**: the connected AsusRog machine is offline. Existing strict shipping gate must not be bypassed.
