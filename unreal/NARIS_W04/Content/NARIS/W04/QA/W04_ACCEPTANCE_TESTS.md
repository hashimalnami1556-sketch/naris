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
T20 Presentation cue bus fans authoritative gameplay events into optional Niagara, Audio/MetaSound and CameraShake payloads without mutating gameplay state.
T21 Bone Beast arena blocker closes on EncounterStarted and reopens on EncounterComplete; packaged runtime smoke verifies the lock cycle.
T22 Every W04 presentation VFX/AUD/Camera asset ID referenced by the cue manifest exists exactly once in MASTER_ASSET_REGISTRY.json.
T23 Boss arena entry trigger automatically starts Bone Beast only for the local player and disables itself after encounter start/completion.
T24 Shipping Release Candidate gate rejects any unbound presentation VFX/AUD/Camera asset before Shipping BuildCookRun.
T25 Hero death disables control, then respawns at the saved Waystone location with restored health, poise, energy, movement and input.
T26 Graphics/audio/accessibility settings persist through NarisGameUserSettings, including quality, VSync/FPS, master/music/SFX/voice, subtitles/scale, camera-shake reduction/intensity, high-contrast interactions and color-vision correction; Apply & Save and Reset Defaults are reachable from the pause menu.
T27 Every bound W04 Niagara presentation payload must be a real NiagaraSystem with at least one emitter handle; empty placeholder systems are rejected by binding resolution/profile authoring and cannot pass Shipping RC.
T28 Runtime subtitles are data-driven through NarisSubtitleSubsystem, respect Subtitles Enabled and Subtitle Scale, expire deterministically, and may be authored on First Whisper/Memory Crystal without hard-coded fabricated dialogue.
