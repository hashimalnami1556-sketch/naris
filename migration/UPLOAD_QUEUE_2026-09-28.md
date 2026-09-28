# NARIS binary upload queue — 2026-09-28

## Pending source binaries
- `Environmental 1.glb`
- `Character 3.glb`
- `Character1_NARIS_Rigged_Prototype.glb`
- `City 1.glb`
- `Character 1.glb`
- `Character 1.zip` (source package duplicates the five listed GLBs)
- `fdb365cc-0ad2-487b.usdz` (detected `PXR-USDC`; resolve actual container/extension before promotion)

## Required next checks
1. Transfer binary payloads through an authenticated Git/LFS-capable checkout; verify SHA-256 after upload.
2. Preserve the original ZIP as provenance or explicitly choose individual GLBs; avoid accidental duplicate runtime copies.
3. Verify the USD crate with a compatible USD tool and retain the submitted filename in provenance.
4. Assign canonical NARIS asset IDs only after the owner/art review; do not invent IDs or mark assets approved.
5. Import candidates into the desktop Unreal project and record scale, axes, material, skeleton/animation, collision/LOD and packaging checks individually.

No binary payload was committed by this text-only intake update. See [source intake README](../docs/project-uploads/2026-09-28/README.md).
