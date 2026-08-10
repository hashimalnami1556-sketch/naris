# W04 Integration Event Matrix

| Event | Producer | Consumers |
|---|---|---|
| `AttackStarted` | BossController | Animation / VFX / Audio |
| `AttackImpact` | Gameplay hit event | Damage / Hit VFX / Audio |
| `ParryWindow` | Combat | UI / Audio / VFX |
| `PhaseChanged` | BossController | VFX / Music / UI |
| `BossDied` | BossController | Quest / Loot / UI / Audio |
| `ArenaGateLocked` | Arena | BossController / UI |

## Principle
Gameplay events are the single source of truth for cross-system synchronization.
