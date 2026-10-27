# Stage 29 — Correct 136 Stage27 placement coordinates

Actual audit: Stage27 zone centers extended to 625000 cm across six zones, exceeding W04 declared X bounds of 160000 cm. Stage29 transforms X to `0.2*x-62500` and Y/Z to `0.2*y`/`0.2*z`, retaining all 136 placement records. Offline range assertions pass.

A separate archive `NARIS_STAGE29_MAP_MATERIAL_ANIMATION_BINDING.zip` provides corrected placements, a Windows preparer, and Unreal Editor Python staging map placer. Source PBR GLBs are from Stage28 and must be imported before placement. It creates `/Game/NARIS/W04/Maps/W04_Stage29_Staging`, refuses to overwrite existing maps, and writes `Saved/TestReports/naris_stage29_placement.json`.

**Not claimed:** Unreal execution, animation blueprint/retargeting, montage playback, collision, production map approval or Windows Shipping. The host was offline. Character SkeletalMeshActors are visual-only pending real Animation Blueprint integration.
