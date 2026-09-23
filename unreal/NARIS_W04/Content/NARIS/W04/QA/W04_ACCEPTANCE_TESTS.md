# W04 ACCEPTANCE TESTS

T01 Boot and default map.
T02 New Game creates clean state.
T03 Hero movement/camera.
T04 Light/Heavy damage commits through an authored attack hit window and impact notify; smoke fallback uses the same Open -> Commit -> Close path.
T05 Parry window prevents damage only when an incoming hit lands during the window, then raises resonance.
T06 Poise reaches zero and opens execution window.
T07 Five-Essence cycling plus energy spend/restore works from keyboard and gamepad.
T08 Celestial Wolf Follow/Guard/Attack/Track/EchoLink modes execute their distinct runtime behavior and emit presentation cues.
T09 Bone Beast phases P1/P2/P3 remain authoritative in ABoneBeastBoss, mirror into PhasePresentation, and fan out through presentation cues.
T10 Corrupted Heart persists step 1 at Memory Crystal, step 2 at Ash Gate, step 3 at Celestial Wolf bond, and step 4/completion at Bone Beast defeat.
T11 Save/Load restores checkpoint ID/location, active/completed quest state and step, lore, narrative, gate, companion, boss and waystones.
T12 Arabic/English localization.
T13 HUD reflects health/resonance/energy/essence, interaction prompt, Celestial Wolf state/mode, Corrupted Heart objective, boss state and DemoEnd.
T14 Pause/resume opens the native pause menu; keyboard/gamepad navigation remains executable while paused and can enter/leave Settings.
T15 No public release until all tests pass.
T16 Packaged runtime progression smoke drives Waystone -> MemoryCrystal -> AshGate -> CelestialWolf -> BoneBeast -> DemoEnd.
T17 Runtime smoke Save -> New Game -> Load restores checkpoint, lore, narrative, gate, companion, quest, boss and DemoEnd.
T18 Windows BuildCookRun package launches successfully in en and ar cultures.
T19 Windows Development package emits package-smoke report and requested CSV/GPU/LLM profiling evidence.
T20 Presentation cue bus fans authoritative gameplay events into optional Niagara, Audio/MetaSound and CameraShake payloads without mutating gameplay state; every audio cue declares SFX/Music/Voice routing.
T21 Bone Beast arena blocker closes on EncounterStarted and reopens on EncounterComplete; packaged runtime smoke verifies the lock cycle.
T22 Every W04 presentation VFX/AUD/Camera asset ID referenced by the cue manifest exists exactly once in MASTER_ASSET_REGISTRY.json.
T23 Boss arena entry trigger automatically starts Bone Beast only for the local player and disables itself after encounter start/completion.
T24 Shipping Release Candidate gate rejects any unbound presentation VFX/AUD/Camera asset before Shipping BuildCookRun.
T25 Hero death disables control, then respawns at the saved Waystone location with restored health, poise, energy, movement and input.
T26 Graphics/audio/accessibility settings persist through NarisGameUserSettings, including quality, VSync/FPS, master/music/SFX/voice, subtitles/scale, camera-shake reduction/intensity, high-contrast interactions and color-vision correction; presentation audio applies Master × selected SFX/Music/Voice bus volume; Apply & Save and Reset Defaults are reachable from the pause menu.
T27 Every bound W04 Niagara presentation payload must be a real NiagaraSystem with at least one emitter handle; empty placeholder systems are rejected by binding resolution/profile authoring and cannot pass Shipping RC.
T28 Runtime subtitles are data-driven through NarisSubtitleSubsystem, respect Subtitles Enabled and Subtitle Scale, expire deterministically, and may be authored on First Whisper/Memory Crystal without hard-coded fabricated dialogue.
T29 Controller remap exposes the 11 core W04 gameplay actions from the paused Controls page, captures a new gamepad button, rejects conflicts and reserved Start/B keys, persists through InputSettings SaveKeyMappings/ForceRebuildKeymaps, and can restore the canonical defaults.
T30 Normal W04 boot opens the localized front-end with New Game, Continue, Settings, Controller Remap and Quit; Continue requires an existing auto-save, New Game writes clean state and reloads the current level with a one-shot front-end bypass, and packaged runtime smoke bypasses the front-end automatically.
T30 Presentation audio routing is explicit and manifest-driven: every audio payload declares sfx/music/voice, profile authoring rejects missing or invalid buses, and runtime volume uses Master × the selected bus.
T31 Production combat animations are registry-backed AnimMontages at deterministic W04 paths; Hero Light/Heavy require hit-window + impact notifies, Wolf/Bone Beast attacks require their native impact notifies, and Shipping RC rejects missing montages, missing notifies or zero-duration hit windows.
T32 Windows runtime log QA scans only artifacts created during the launch-smoke window and fails Development packaging on crash artifacts, Fatal error, Unhandled Exception, Assertion failed, LowLevelFatalError or Ensure condition failed.
T33 Core production assets (Ashen Vessel, Celestial Wolf, Bone Beast, Waystone, Memory Crystal, Ash Gate and Sword of Poem) must resolve at deterministic Unreal paths and pass technical QA: assigned materials, required LOD count, Skeleton + PhysicsAsset for skeletal meshes, authored/simple collision for static meshes, recorded Nanite state/LOD0 triangle count, no more than 4 material slots on the core static assets, and Ash Gate LOD0 at or below its documented 22,000-triangle budget; strict Shipping RC rejects any unresolved or invalid core asset.
T34 Shipping uses the production Ashen Forest map only: /Game/NARIS/W04/Maps/W04_AshenForest must exist, contain the core W04 progression actors, contain no DEV_* labels or NARIS_RuntimeSmokeDirector, and the Shipping RC must never cook W04_Prototype.
T35 W04_AshenForest_Blockout is authored only from the canonical Ashen Forest LEVEL_LAYOUT, places the core progression actors into their intended zones, labels zone geometry/markers BLOCKOUT_*, and is never used as a Shipping map.
T36 Ashen Forest environment factory v2 is registry-backed and reads its dimensions/policies from data/environments/W04_AshenForest_environment_factory_v2.json: 1m snap grid, 4m floor module, 3.5m wall height, 128m streaming cell, canonical collision and LOD policy; Blender must not hard-code conflicting grid/LOD metadata.
T37 Ashen Forest Factory v2 end-to-end authoring runs from factory-startup Blender, applies UVs, saves the canonical registry-backed .blend source for NARIS-W04-ENV-FACTORY-0002, then passes through the existing Blender validation/export manifest and Unreal import bridge before it may be treated as exchange evidence.
T38 W04 material production gate maps every Ashen Forest material-library ID to a canonical NARIS-W04-MAT asset and deterministic Unreal MaterialInstanceConstant path, requires the correct M_MASTER_SURFACE or M_MASTER_WATER parent, validates authored PBR scalar/vector values within tolerance, and blocks Shipping on unresolved masters, unresolved instances or parameter drift.

