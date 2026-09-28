# NARIS source asset intake — 2026-09-28

## Status
The seven attached 3D source files were inspected in the work session and recorded in the asset inventory. **The 3D binaries themselves are not present in this GitHub branch yet.** No engine import or visual/technical-art approval is claimed.

The 14 image references are present in the current work session and pass image decode checks. Their SHA-256 values match the corresponding records in `NARIS_MASTER/SOURCE_ASSET_INVENTORY.json`. A fetch of the recorded image path `ASSETS/CHARACTERS/REFERENCES/IMG_3846.jpeg` on `main` returned 404, so matching inventory records must not be read as proof that image binaries are committed there. See [asset intake follow-up](../../production/work/active/asset-intake-20260928.md).

## Included 3D source set
- Five GLB 2.0 files: environment, city, two character models, and a rigged character prototype.
- One original ZIP package. Its CRC check passes; it contains the same five GLBs, and each embedded file matches its separately attached counterpart by SHA-256.
- One file named `fdb365cc-0ad2-487b.usdz`. Its first bytes identify a `PXR-USDC` crate, not a ZIP-based USDZ package. Keep it in review until verified with a compatible USD tool; do not silently rename the supplied original.

## Structural inspection
- Each GLB header's declared length matches the actual file size, and its JSON chunk parses.
- The rigged prototype has 19 nodes, one skin and one animation. The other four GLBs have no skin or animation in their parsed JSON.
- Each GLB has one mesh and one material; the model files embed 2048×2048 JPEG normal, base-color and RM texture maps.
- This is a structural intake check only. It does not validate GLB conformance, scale, axis, skeleton quality, retargeting, collision, LOD, licensing, Unreal import, or gameplay fit.

## Proposed destination after binary transfer
- Individual GLBs: `assets/project_uploads/2026-09-28/models/`
- Original ZIP: `assets/project_uploads/2026-09-28/original-source/`
- USD-format review: `assets/project_uploads/2026-09-28/usd-review/`

The paths above are planned destinations, not files already in the repository. See [manifest](PROJECT_UPLOAD_MANIFEST.md) and [binary upload queue](../../../migration/UPLOAD_QUEUE_2026-09-28.md).
