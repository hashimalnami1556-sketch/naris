# CHAR-001 G0/G1-G — twelve structural checks (not behavioral)

1. Owner-approved target is 87 runtime bones + five Unreal sockets, not 92 skin bones.
2. Exactly 83 deform and four helper bones are specified; helpers named and non-deform.
3. Names are unique and casefold-safe.
4. Exactly one motion root exists; pelvis is its non-connected child.
5. Every non-root bone has a valid parent and there are no cycles.
6. No zero-length bones in the authored Armature.
7. Rest matrices are finite and invertible; object transform identity.
8. Left/right mirrored head/tail positions and bone roll match anatomical axes.
9. Export excludes Control Rig and attachment sockets as skin joints.
10. Skeleton source identity and mesh transforms are recorded with immutable GLB SHA-256.
11. GLB export has no duplicated or unrelated nodes and passes structural parsing.
12. Full 87-bone Unreal import, scale/orientation and five socket creation are confirmed at G5.

G0 design checks can pass independently of G1/G5 physical evidence. Do not mark **G1-A**, **G1-G**, **G2** or **G5** PASS on documentation alone.
No walk, foot sliding, twist stress, fists or animation requirement belongs to G0.
