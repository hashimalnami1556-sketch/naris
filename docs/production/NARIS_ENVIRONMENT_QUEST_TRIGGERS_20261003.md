# NARIS W04 — Persistent Environment Quest Triggers

## Actor
Use `ANarisEnvironmentQuestTrigger` or a Blueprint subclass.

Supported trigger types:
- RegionEnter
- LandmarkDiscover
- CaveEnter
- MountainPeak
- WaterEnter
- HolySite
- BossArena
- SecretArea
- TreasureRoom
- LavaZone

## Authoring fields
- TriggerId: stable unique ID used for save persistence.
- TargetId: region/landmark/cave/boss identifier for presentation or Blueprint logic.
- RequiredQuest: optional active quest requirement.
- QuestToStart: optional quest to start.
- QuestStepToSet: optional step to set on QuestToStart or RequiredQuest.
- bOneTime: persist consumption through Runtime TriggerNarrative state.
- bAutoSave: save immediately when state changes.

## Example
`BP_EnvTrigger_AshCave01`
- TriggerId = AshCave01
- TriggerType = CaveEnter
- TargetId = Cave.AshCave01
- RequiredQuest = Quest.W04.CorruptedHeart
- QuestStepToSet = 2
- bOneTime = true
- bAutoSave = true

On first player entry the trigger validates the required quest, advances it, emits the Blueprint event, records `EnvironmentTrigger.AshCave01`, autosaves, and disables further overlaps. On reload, BeginPlay checks the persisted narrative marker and keeps the trigger consumed.

## Design rule
Do not generate dozens of random quests from enemy *instances*. Author quest templates/data once and use environment triggers to advance meaningful progression. This avoids duplicated IDs, save corruption, repetitive objectives, and uncontrolled quest database growth.
