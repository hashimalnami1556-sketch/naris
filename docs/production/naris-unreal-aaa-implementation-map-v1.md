# Unreal AAA Implementation Map v1

## New/updated asset families
Content/UI/Foundation: colors, typography, icons, materials, CommonUI input data.
Content/UI/Screens: WBP_MainMenu, Pause, HUD, Inventory, Map, QuestJournal, Settings, Death, Loading.
Content/UI/Components: Button, Tab, Tooltip, ItemTile, StatRow, ObjectiveToast, BossBar, Prompt.
Content/Art/Characters: master materials, material instances, rigs, anim BPs, montages, ControlRig.
Content/World: biome data assets, lighting profiles, PCG graphs, HLOD layers, decals, Niagara ambient systems.

## C++ boundaries
UNarisUIManagerSubsystem: screen stack/input mode/pause ownership.
UNarisSaveSubsystem: versioning/atomic save/migrations.
UNarisCombatComponent: buffered commands, attack state, hit windows.
UNarisTargetingComponent: lock-on selection/LOS/death recovery.
UNarisInteractionComponent: trace + prompt model.
UNarisAccessibilitySettings: persistent accessibility values.

## Migration order
1. Foundation tokens + reusable widgets.
2. HUD and Pause flow.
3. Settings + accessibility.
4. Inventory/Map/Quest.
5. Character material/animation pass.
6. Environment/lighting/PCG pass.
7. Combat feedback + AI presentation.
8. Loading/save/death flow.
9. Performance profiling and scalability.
10. RC visual/interaction QA.
