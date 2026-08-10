# Bone Beast Reward Contract

## Reward boundary
The reward system consumes the authoritative `EncounterComplete` event and the quest completion state.

## Reward groups
- Core progression reward
- World progression unlock
- Optional loot reward
- Narrative/lore reward

## Rules
- No reward is granted on `Death` presentation alone.
- Reward must be idempotent: repeated UI/audio/cinematic events cannot duplicate rewards.
- Save progression only after authoritative quest completion.
- Exact item quantities and balance values remain data-driven and require design/playtest approval.
