# CHAR-001-G0 — 12 Structural Tests
1. Exactly 92 production deform/export bones according to the approved contract.
2. Bone names are unique.
3. Every non-root bone has an existing parent.
4. Exactly one root.
5. Pelvis is a direct child of root.
6. No zero-length deform bones.
7. No NaN/Inf transforms.
8. No non-uniform scale in exported skeleton.
9. No duplicate exported nodes.
10. No unused exported Control Rig nodes; CONTROL class is excluded.
11. Skin influences <= 4 per vertex and weights normalize to 1 within tolerance.
12. GLB audit + UE5.7 import smoke completes without scale/axis/root errors.

PASS policy: G0 remains PENDING until all 12 have machine evidence; documentation alone cannot mark PASS.
