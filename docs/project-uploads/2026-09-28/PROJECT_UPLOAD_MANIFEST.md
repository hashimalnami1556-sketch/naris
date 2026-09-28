# Binary source manifest — 2026-09-28

All names below are preserved from the user attachments. Status `SOURCE_FOUND` means inspected in the current workspace; it does not mean committed to GitHub.

| Source file | Bytes | SHA-256 | Structural note | Status |
|---|---:|---|---|---|
| `Environmental 1.glb` | 1,210,488 | `64780ab4c7abb5c38d10fe5035d740f294ba5aed4824c897c9bcc494f30b4271` | GLB 2.0; one mesh/material; no skin or animation | SOURCE_FOUND |
| `Character 3.glb` | 1,052,664 | `ac36ad54c102b7d755359195997afc009160689b28b0cfb4b53b77987dbb72b5` | GLB 2.0; one mesh/material; no skin or animation | SOURCE_FOUND |
| `Character1_NARIS_Rigged_Prototype.glb` | 2,828,520 | `83e4d41f347c959e61ec57355fd682db99ed4652dfabba622ae0784b8cd9b628` | GLB 2.0; 19 nodes, one skin, one animation | SOURCE_FOUND |
| `City 1.glb` | 1,525,136 | `2032dd3208d9215a5531f1fa880a2ea2e6ab4962a0836a4a6acb12dd8ec36e52` | GLB 2.0; one mesh/material; no skin or animation | SOURCE_FOUND |
| `Character 1.glb` | 2,177,340 | `d3d83628a982079a614541295334f11cafe616af86f621cd0947190afb1acc75` | GLB 2.0; one mesh/material; no skin or animation | SOURCE_FOUND |
| `Character 1.zip` | 6,717,666 | `390705615481f86841c4b78617505db7deed89614882ce184747d571dae453f9` | CRC passes; contains all five GLBs above, byte-identical by member SHA-256 | SOURCE_FOUND |
| `fdb365cc-0ad2-487b.usdz` | 1,763,041 | `aca97111f4ebc1d3fe6d9042b13757d1d74d648b3f50f0be81cc63523abf9d89` | Signature `PXR-USDC`; file extension/container discrepancy needs USD-tool validation | SOURCE_FOUND |

## Verification boundary
GLB length/header and JSON-chunk checks passed; ZIP CRC test passed. No import into Blender or Unreal, visual model inspection, asset approval, or runtime test was performed. The binaries remain pending transfer to the proposed paths.
