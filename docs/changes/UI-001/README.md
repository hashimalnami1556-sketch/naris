# UI-001 handoff
The owner-approved images define *appearance*, not runtime readiness. The local UI-001 delivery ZIP contains original image bytes and their SHA256 manifest, non-destructive import scripts, and test reports.

### UMG mapping
| Approved screen | Runtime target | Required interactions |
|---|---|---|
| Main Menu | Existing W04 main-menu widget or WBP_NarisMainMenu | Start, Continue, Settings, Exit, focus |
| Character / Equipment | Existing W04 character/inventory widget | Inventory items, character attributes, equipment, live resource bars |
| Boss Combat | Existing W04 HUD/boss widgets | Boss HP, player HP/stamina/mana, abilities, quest, targeting |

### Completion conditions
1. Confirm exact checked-out UE 5.7 W04 path and baseline HEAD/build on authorized Windows device.
2. Import reference images *without overwriting* existing assets.
3. Rebuild live UMG hierarchy and wiring, test localized Arabic/English, gamepad and ultrawide.
4. Perform fixed-seed before/after/diff screenshots and complete BuildCookRun, Project.* automation, dedicated server + two clients and performance benchmark.
5. Merge PR only when artifacts and tests are documented; rollback clearly recorded.

This documentation preserves the visual approval but does not claim the interfaces were installed into Unreal.
