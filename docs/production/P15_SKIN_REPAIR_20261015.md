# P13/P15 skin connectivity repair — 2026-10-15

Actual P13 and P15 archives were recovered and inspected. P15 had one eight-joint skin per character and 31 one-joint rigid skins for the Gatekeeper. This is asset-source evidence, not proof that runtime systems are absent or present.

The repair tool consolidates the Gatekeeper into one skin with 32 connected joints, connects each character under a shared root (9 joints), remaps joint indices/inverse binds and rebakes 13/13/11 source clips. Detached character mesh motion is deliberately transferred to the skeleton root; boss common-root motion is retained on the new root. Rigid part weights remain rigid and geometry-derived boss pivots are provisional, not anatomical approval.

Khronos glTF Validator found zero errors on all three repaired files: no boss warnings, one generated tangent-space warning per character. CPU skin-matrix comparisons across source keys and intermediate samples had maximum component error below 0.0002, accounting for deliberate character root-motion migration. This number is not a world-space displacement or visual-quality score. Geometry, original weights, materials and image descriptors were preserved.

Validation: six synthetic conversion tests; 342 total CI source tests; six AssetForge tests; repository validator passed. Blender, Unreal, root-motion extraction/capsule behavior, combat montage timing, final soft deformation, Foot IK, Windows packaging and performance have not been verified for these candidates. AsusRog was offline. Engine and release gates stay open.

The delivered candidate ZIP contains GLBs, original-source hashes, the repair/CPU validation tools, Khronos results and numerical reports. It is not a game build or a production asset promotion. Do not replace registered production assets without the existing import/visual/runtime gates.

Reproduce: `python tools/assets/unify_skin.py INPUT.glb OUTPUT.glb`, then `python tools/assets/check_skin_repair.py INPUT.glb OUTPUT.glb`. A new output path is required. The converter is limited to rigid transforms/unit scale and LINEAR animation rebaking; it is not a general-purpose autorigger.

References: https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html#skins ; https://github.com/KhronosGroup/glTF-Validator
