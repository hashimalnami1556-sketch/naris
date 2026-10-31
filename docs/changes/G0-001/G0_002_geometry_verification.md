# G0 mesh identity verification

Direct GLB geometry comparison (no Unreal run):

| Metric | Character 1.glb | Character1_NARIS_Rigged_Prototype.glb |
| --- | ---: | ---: |
| Vertices | 32,373 | 32,373 |
| Faces | 49,886 | 49,886 |
| Max coordinate difference | 0 | 0 |
| Face index order | Identical | Identical |
| Skin joints | 0 | 18 |
| Animations | 0 | 1 |

**Finding:** The existing prototype references the exact original mesh, so **do not remodel**. The 18-joint prototype is not the 92-joint production rig; no validated target rig/skinning or UE5 retargeting is established. The source images are concepts rather than verified meshes. Original assets must remain unmodified. Editor screenshots, BuildCookRun, network and performance checks remain not run because the device is offline. Evidence in separately generated `NARIS_G0_002_VERIFIED.zip`.

**Next gate:** bind verified 92-joint target to this existing mesh; check inverse bind matrices, weights, twist, locomotion, foot contacts and UE5 runtime. Do not merge until complete.
