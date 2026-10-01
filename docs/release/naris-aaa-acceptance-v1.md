# AAA Acceptance Gates v1

- No screen uses placeholder fonts/icons/textures.
- 100% menu actions reachable by keyboard/mouse/gamepad.
- Arabic RTL checked on every major screen; no clipped text at 125% UI scale.
- HUD readable at 1080p and 4K; safe zones respected.
- Combat has anticipation, impact, recovery, audio and VFX feedback for every attack class.
- Enemy telegraphs remain readable with VFX-heavy scenes.
- Save/load survives process restart and schema version check.
- No synchronous asset-load hitch during normal combat.
- No UI Tick used for static text/stat refresh; event-driven updates.
- 60 fps target profile recorded in exploration, 5-enemy combat and boss arena.
- LOD/HLOD transitions checked for obvious popping.
- Main menu -> Continue -> gameplay <= expected platform loading budget and never lands in paused hidden state.
