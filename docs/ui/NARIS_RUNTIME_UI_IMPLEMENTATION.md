# NARIS Runtime UI — Unreal Implementation Map

Target: Unreal Engine 5.4 / UMG / Enhanced Input
Reference resolution: 2560x1440, safe-zone aware, scalable to 1920x1080.
Direction: Obsidian + Ash + Ancient Gold, Ember danger, Aether violet, Spirit cyan.
Rule: mockup imagery is reference only; runtime readiness requires Unreal evidence.

## Screen architecture
| Order | Runtime screen | Unreal widget target | Primary action |
|---|---|---|---|
| 01 | Splash / Legal | WBP_NarisSplash | Continue |
| 02 | Main Menu | WBP_MainMenu | Continue / New Game |
| 03 | New Game | WBP_NewGame | Select difficulty + start |
| 04 | Intro Cinematic | WBP_CinematicOverlay | Skip / subtitles |
| 05 | Gameplay HUD | WBP_GameplayHUD | Play |
| 06 | Interaction Prompt | WBP_InteractionPrompt | Interact |
| 07 | Combat / Boss HUD | WBP_BossHUD | Combat feedback |
| 08 | World Map | WBP_WorldMap | Navigate / waypoint |
| 09 | Inventory | WBP_Inventory | Equip / use |
| 10 | Item Detail | WBP_ItemDetail | Compare |
| 11 | Journal / Quests | WBP_Journal | Track objective |
| 12 | Skills | WBP_Skills | Unlock / inspect |
| 13 | Crafting | WBP_Crafting | Craft |
| 14 | Shop | WBP_Shop | Buy / sell |
| 15 | Dialogue | WBP_Dialogue | Choose response |
| 16 | Memory / Lore | WBP_MemoryArchive | Inspect lore |
| 17 | Pause | WBP_Pause | Resume |
| 18 | Settings | WBP_Settings | Apply |
| 19 | Controls | WBP_Controls | Rebind |
| 20 | Accessibility | WBP_Accessibility | Apply |
| 21 | Death / Respawn | WBP_Death | Respawn |
| 22 | Loading | WBP_Loading | Passive |
| 23 | Demo End | WBP_DemoEnd | Continue / menu |
| 24 | Credits | WBP_Credits | Return |

## W04 HUD composition
- Top-left: player portrait, health, stamina, active essence.
- Top-center: contextual boss health only while engaged.
- Top-right: compass/minimap + tracked objective.
- Bottom-left: quick slots.
- Bottom-right: abilities / cooldowns.
- Center: reticle and interaction prompt; hidden when not actionable.
- Subtitle safe area: bottom-center above action bar.

## Interaction states
Every actionable component must support Default, Hover, Focus, Pressed, Disabled.
Every data surface must support Loading, Empty, Error, Ready.
Gamepad focus is mandatory. Arabic and English layouts must remain readable without truncation.

## Foundation implemented in C++
- ENarisUIScreen canonical screen enum.
- FNarisUIFlow deterministic screen state.
- UNarisScreenBase reusable UMG base.
- NarisUITheme semantic colors and 8pt spacing tokens.
- Automation tests for boot, gameplay/pause round trip, and core menu routing.

## Next Unreal content pass
1. Create WBP_NarisRoot and route ENarisUIScreen to widget classes.
2. Create WBP_MainMenu and WBP_GameplayHUD first.
3. Bind Enhanced Input actions for Pause, Inventory, Map, Journal and Skills.
4. Bind health/stamina/objective/save data.
5. Build remaining widgets from shared components.
6. Validate keyboard/mouse + gamepad + Arabic/English.
7. Capture PIE screenshots/video as runtime evidence.

## Shared component library
- WBP_NarisButton
- WBP_NarisIconButton
- WBP_NarisTab
- WBP_NarisPanel
- WBP_NarisModal
- WBP_NarisTooltip
- WBP_NarisProgressBar
- WBP_NarisResourceBar
- WBP_NarisItemTile
- WBP_NarisQuestRow
- WBP_NarisMapMarker
- WBP_NarisPrompt
- WBP_NarisToast
- WBP_NarisSubtitle
- WBP_NarisFocusRing

## Acceptance gate
The conversion is not called “inside the game” until the widgets compile and are captured running in Unreal PIE or a packaged Windows build.
