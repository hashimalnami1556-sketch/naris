# NARIS Stage36: asset-class inventory gate

Read-only Unreal Editor Python script. Inspects `/Game/NARIS` recursively and records asset class counts for World, SkeletalMesh, Skeleton, AnimSequence, AnimMontage, AnimBlueprint, Material and Texture2D. Outputs `Saved/TestReports/naris_stage36_inventory.json`. Does not fabricate missing assets or claim runtime validation.

Run via UnrealEditor-Cmd with `-ExecutePythonScript=<absolute path to naris_stage36_inventory.py>` after compiling the editor. Four local mock-based Python tests passed on the packaged version.

**Important:** class presence is a minimum condition, not proof of valid skeleton compatibility, animation Blueprint links, material UVs, collision, map actors, PIE functionality, or Windows EXE. AsusRog offline: UE build and PIE untested. The Stage35 audit has a separate known preview-material API compatibility risk; this Stage36 tool is read-only.
