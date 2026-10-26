# Stage 30 — PBR + combat + motion source audit

Actual GLB map updated offline: 1,327 geometry meshes assigned glTF PBR material factors, nine glTF materials, three separate 512px textures not UV-linked. Existing rigged hero has 18 joints and 1 animation; Gate Guardian has 13 joints and 12 animations. Binary models and textures are delivered in `NARIS_STAGE30_MATERIALS_CHARACTERS_COMBAT_MOTION.zip`, **not committed to GitHub** pending Git LFS review.

C++ combat component added to repository, not compiled in UE5.7; it needs animation montage binding and input integration, including ensuring no stamina cost on failed montage play. Six offline structure tests pass. No PIE or EXE verification. Device AsusRog offline. Never treat this branch as shipping-ready.
