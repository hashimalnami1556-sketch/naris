# Quality / Error Repair Pass
- Actor Tags are no longer the recommended event transport. Batch 12 standardizes typed event payloads.
- Direct Blueprint casts remain prohibited for cross-system communication.
- Stable IDs are separated from localized text.
- Reputation is clamped to [-100,100].
- Empty IDs are rejected by public mutation APIs.
- Quest runtime is designed for SaveGame serialization.
- Data tables are split by responsibility to prevent monolithic registries.

## Remaining external payloads
Final skeletal meshes, authored animations, Niagara systems, MetaSounds/VO, cinematics and localized text require production assets; this package supplies their contracts and registries, not fabricated binary .uasset files.
