# The Corrupted Heart — W04 Quest Contract

## Quest ID
`Quest.W04.CorruptedHeart`

## Encounter flow
1. Player enters W04 Bone Beast arena.
2. Arena locks and `EncounterStarted` fires.
3. Bone Beast transitions through authored combat phases.
4. Boss reaches `Dead` state.
5. `EncounterComplete` fires exactly once.
6. Quest objective resolves.
7. Exit gate unlocks.
8. Reward/progression consumers receive completion event.

## Failure/retry
A failed attempt must reset the encounter to its authored initial state without falsely completing the quest.

## Save/progression boundary
Quest completion is persistent progression. Presentation events are not saved as progression state.

## Dependencies
- `Arena.BoneBeast`
- `Boss.BoneBeast`
- `World.W04.AshenForest`
