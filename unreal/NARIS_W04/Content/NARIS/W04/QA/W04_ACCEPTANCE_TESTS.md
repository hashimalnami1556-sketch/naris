# W04 ACCEPTANCE TESTS

T01 Boot and default map.
T02 New Game creates clean state.
T03 Hero movement/camera.
T04 Light/Heavy damage commits through an authored attack hit window and impact notify; smoke fallback uses the same Open -> Commit -> Close path.
T05 Parry window prevents damage only when an incoming hit lands during the window, then raises resonance.
T06 Poise reaches zero and opens execution window.
T07 Five-Essence cycling plus energy spend/restore works from keyboard and gamepad.
T08 Celestial Wolf follow/guard/attack/track contract.
T09 Bone Beast phases P1/P2/P3.
T10 Quest Corrupted Heart progression.
T11 Save/Load restores checkpoint, quest, lore and waystones.
T12 Arabic/English localization.
T13 HUD reflects runtime values.
T14 Pause/resume works from keyboard and gamepad, including input execution while paused.
T15 No public release until all tests pass.
T16 Packaged runtime progression smoke drives Waystone -> MemoryCrystal -> AshGate -> CelestialWolf -> BoneBeast -> DemoEnd.
T17 Runtime smoke Save -> New Game -> Load restores checkpoint, lore, narrative, gate, companion, quest, boss and DemoEnd.
T18 Windows BuildCookRun package launches successfully in en and ar cultures.
T19 Windows Development package emits package-smoke report and requested CSV/GPU/LLM profiling evidence.
