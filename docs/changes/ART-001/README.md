# ART-001 — W04 Style-Matched Concept Assets

**Status: CONCEPT ONLY — NOT APPROVED FOR PRODUCTION**

## Why

The previous UI concept pass did not meet the owner's visual quality bar. Review of the canonical Figma file and Adobe Creative Cloud revealed that the project already has a stronger illustrated NARIS art direction and bilingual game UI references. The rework therefore uses the existing visual source instead of inventing a new photorealistic style.

## What

Three style-matched concept candidates were generated and registered on this branch:
- `NARIS-W04-UI-MENUART-0001` — menu key-art composition
- `NARIS-W04-ENV-LAND-0001` — Ashen Forest Waystone + Memory Crystal vista
- `NARIS-W04-BOS-ARENA-0001` — quadruped Bone Beast arena key art

Adobe source/output URNs and full edit prompts are in `assets.json`.

## How

Adobe Firefly `image_instruct_edit` was applied to existing Adobe concept assets. The edits were inspected through Adobe's image preview. A first incorrect boss edit was rejected and a second pass explicitly selected the four-legged Bone Beast from the source sheet.

## Evidence

- Existing high-quality NARIS UI references were recovered from Adobe: main menu, bilingual inventory, settings, world selection, gameplay HUD and the visual-production board.
- The three output concept assets were previewed at 900px long edge.
- GitHub issue #117 tracks the V6 UI visual rework.
- Canonical Figma file: https://www.figma.com/design/lYSmWwGHXCEXODKpG9bpJH

## Tests

- Adobe asset search confirmed output asset URNs.
- Visual review: title composition, W04 Waystone/Memory Crystal, quadruped Bone Beast.
- Figma V6 structural review found defects (missing background image fill, title/subtitle overlap, button vertical alignment); V6 is rejected and not approved.
- No Unreal import, BuildCookRun, PIE, multiplayer test, or engine screenshot was performed.

## Performance

No assets were imported into Unreal. FPS, frame time, memory and package-size deltas are **N/A**, not zero.

## Risk

Firefly can drift from exact model/character geometry despite source references. These images are illustrative key art, not approved meshes, textures, rigs, animations or maps. The Bone Beast candidate must be checked against the canonical enemy model before approval.

## Rollback

Revert the ART-001 branch commits. Remove the three concept entries from the registry and discard the associated manifest. No changes were made to main or to Unreal source.

## Next action

After Figma MCP quota resets, rebuild V6 using the existing Adobe UI references as the style/layout source, correct the image-fill and typography defects, and use the concept assets only as image layers. After Desktop Commander quota resets, import through the canonical asset pipeline and run Unreal's actual build, runtime, network and performance gates.
