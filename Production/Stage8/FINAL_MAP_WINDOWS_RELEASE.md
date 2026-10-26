# Stage 8 — Final Map + Windows EXE Gate

## Objective
Close the two release blockers:
1. /Game/NARIS/W04/Maps/W04_AshenForest
2. A verified Windows Shipping executable.

## Current truth
The repository has UE 5.7 source and packaging infrastructure, but the final production .umap and a verified packaged EXE are not yet runtime evidence.

## Promotion rule
W04_Prototype is development smoke only.
W04_AshenForest_Blockout is assembly only.
W04_AshenForest is the only Shipping map.

The Windows script refuses to package if W04_AshenForest.umap is absent, runs the shipping-map validator, executes BuildCookRun, requires a NARIS *.exe, and prints SHA-256.

No EXE is marked complete until a self-hosted Windows Unreal runner or the authorized workstation actually passes this gate.
