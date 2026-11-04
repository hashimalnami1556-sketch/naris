# CALL OF NARIS — UI-001 Official Visual Direction (2026-11-04)

**Owner decision:** the three user-provided screenshots are the official visual reference for the Unreal Engine 5.7 main menu, character screen and boss-combat HUD. This is **design approval only**; it is not evidence of installed, compiled or playable UMG widgets.

## Approved three screens
1. **Main menu** — hero and W04 environment background, CALL OF NARIS masthead, right-side Arabic actions: ابدأ اللعبة، متابعة، الإعدادات، خروج.
2. **Character** — left-side menu (الشخصية، المهارات، المعدات، المهام، الخريطة، التحديات، المخزون، المتجر), character scene at center, attributes/equipment/active abilities at right, status indicators at bottom.
3. **Combat** — quest at top-left, boss name/health at top, player resource bars bottom-left, skills with Q/E/R/Shift and target lock indicator. Preserve clear sightlines and minimal screen occlusion.

## Authoring obligations
- Keep original GLB/FBX/USDZ characters and stylized identity; background screenshots are **design references**, not an in-game mesh or functional UI. Follow `docs/DESIGN_PILLARS.md`.
- Extend current `unreal/NARIS_W04` runtime UI/HUD and existing front-end/menu code; avoid duplicate state subsystems.
- Build real UMG buttons, bars, equipment slots, focus navigation and inventory/data bindings. Never flatten a screenshot into a fake interactive menu.
- Distinguish live resource values from the illustrative numbers in the screenshots; continue disabled until a valid save is present.
- Support Arabic RTL/English LTR and keyboard/mouse/gamepad; DPI safe zones at 1280×720, 1920×1080, 2560×1440 and 3440×1440; check readability and accessible focus states.
- For W04 gameplay use actual level/camera/characters and verified production asset imports. No new photorealistic replacement assets.

## Source-reference handoff
The original three PNGs are supplied in a separate zipped artifact `NARIS_UI_001_OFFICIAL_REFERENCES.zip`. It contains unmodified originals with SHA256 checksums, a safe install-preflight PowerShell script and three local manifest verification tests. The binaries are **not** checked into this commit; place them under `docs/ui/references/UI-001` with Git LFS before engine implementation.

## Quality gate
- **Owner visual decision: APPROVED.**
- **UMG implementation: NOT VERIFIED.**
- **Unreal 5.7 build/cook/PIE, actual before/after/diff, bilingual A11y, gamepad, server + two clients, FPS/memory, Windows installer: NOT RUN.**
- No merge or shipping approval until the project quality gates succeed.

## Rollback
Keep existing live UI until UMG integration passes; revert feature branch and remove added reference-only PNGs if required. All original 3D source assets remain untouched.
