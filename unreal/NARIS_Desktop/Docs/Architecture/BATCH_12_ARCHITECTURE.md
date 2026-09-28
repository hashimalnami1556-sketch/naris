# Batch 12 Architecture

Flow: World/Combat/AI Event -> GameplayEventRouter -> QuestSubsystem -> WorldStateSubsystem -> Dialogue/Faction/Codex/Cinematic reactions.

## Rules
1. Gameplay logic references stable FName IDs, never display text.
2. Dialogue conditions are evaluated against WorldState/Faction/Quest state.
3. Quest objectives subscribe to typed events rather than polling.
4. Consequences are commands: SetFlag, AddFactionRep, UnlockCodex, UnlockFastTravel, StartEncounter, SetWeather, TriggerCinematic.
5. NPC schedules are data-driven and can be overridden by quest/world-state conditions.
6. Save serialization stores IDs + state only; assets are resolved from registries.

## Integration
- Batch 08: Kill/Hit/Interact events advance objectives.
- Batch 09: Encounter completion and boss phases publish events.
- Batch 10: Zone discovery/streaming events drive exploration objectives.
- Batch 11: Fast-travel/weather/environment consequences consume world-state commands.
