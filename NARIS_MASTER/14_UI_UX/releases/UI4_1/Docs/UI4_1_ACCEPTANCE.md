# UI4.1 Acceptance Gate

## Boot
- Normal packaged launch must log `NARIS_FRONTEND READY`.
- Normal packaged launch must NOT log `NARIS_DIRECT_PLAY`.
- Runtime bootstrap must log `NARIS_RUNTIME_READY`.

## Main Menu
- NEW JOURNEY starts gameplay.
- CONTINUE is disabled without a save and loads a valid autosave when present.
- SETTINGS opens safely.
- EXIT terminates cleanly.

## In-game shell target
- Pause: Resume / Save / Load / Settings / Main Menu / Exit.
- Inventory: item list, quantity, equipment summary.
- Map: Ashen Forest route and discovered locations.
- Quest Journal: Ash Shards / regular enemies / Gate Warden / Ash Gate progression.
- Accessibility: subtitles, high-contrast HUD, quality presets.

## Regression
- RiggedV4 assets remain loadable.
- Player movement/combat remains enabled after StartGame.
- Resonance, Parry, Soul Vision and Bone Beast Enrage remain compiled.
- Save/load, quest, audio, VFX and checkpoint smoke gates remain functional.
