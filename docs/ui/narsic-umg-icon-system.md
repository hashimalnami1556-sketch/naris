# NARSIC UMG Icon System

## Runtime target

The system menu is implemented as a real Unreal Engine 5.7 UMG view:
- `UNarisSystemMenuWidget`
- `UNarisMenuRowButton`
- `ANarisPlayerController::SelectMenuIndex`
- `ANarisPlayerController::ActivateMenuIndex`

The legacy Canvas path remains a fallback only if the UMG widget cannot be created.

## Visual rule

Icons must not become opaque blocks. Selection is communicated by:
1. a subtle row wash,
2. a bronze value/label accent,
3. a low-opacity icon plate,
4. a semi-transparent glyph.

### Opacity tokens

| State | Icon plate alpha | Icon glyph alpha | Row wash |
|---|---:|---:|---:|
| Active / selected | 0.18 | 0.68 | 0.12 |
| Inactive | 0.025 | 0.24 | 0.018 |

This is intentionally more transparent than the previous dense prototype treatment.

## Palette

- Obsidian canvas
- Blackened-steel surfaces
- Aged-bronze selection accents
- Ember highlight
- Muted bone typography

## Interaction

Rows are actual UMG buttons:
- Mouse hover updates selection.
- Mouse click activates the selected action.
- Keyboard/gamepad navigation still uses the controller contract.
- The controller retains a direct left-mouse fallback path for robustness.

## Responsive layout

The UMG system menu uses percentage anchors rather than fixed screen coordinates:
- Header: 3.5%–96.5% width
- Menu list: 3.5%–60.5%
- Status panel: 63.5%–96.5%
- Footer: 3.5%–96.5%

This keeps the interaction region center-safe on 16:9, 21:9 and 32:9 targets.

## Acceptance gate

Do not mark the UI complete until the AsusRog package passes:
- visible main/pause menu,
- mouse hover + click,
- keyboard,
- gamepad,
- 16:9 screenshot,
- 21:9 screenshot,
- 32:9 screenshot,
- no lighting-rebuild warning,
- no blocking firewall dialog.
