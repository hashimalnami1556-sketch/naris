[Reading 37 lines from start (total: 37 lines, 0 remaining)]

# Aetheria Master Execution Pack
Baseline: clean 7-part Aetheria specification integrated into NARIS Unreal production tree.

## Gate 0 — Stabilization
- Compile-clean C++ before content expansion.
- Camera uses SpringArm + Camera; controller owns yaw/pitch/lock-on only.
- Combat states use Gameplay Tags: State.Attacking, State.Dodging, State.Invulnerable, State.Stunned, Combat.ParryWindow.
- Encounter attack-token coordinator: max 2 simultaneous attackers for a six-enemy group.
- Boss phases are zero-based and data-driven; no unreachable phase branches.

## Track A — Month 2 / Five Realms
1. Frozen Peaks — traversal, ice hazards, vertical shortcuts.
2. Ashen Wastes — heat pressure, ash visibility, Malakar encounter.
3. Verdant Hollow — corruption ecology, stealth routes.
4. Crystal Depths — reflection puzzles, resonance combat.
5. Storm Sanctum — wind traversal, lightning timing.
Each realm requires 12 locations, critical/optional/secret paths, miniboss, boss, 5 secrets, 3 puzzles and 10 lore fragments.

## Track B — Six Additional Lords
Veyra/Frost, Malakar/Ash, Sylwen/Root, Orun/Crystal, Kael/Storm, Seraphine/Tide. Final Throne Lord remains campaign capstone.
Boss contract: 3 phases, 5-7 attacks, explicit telegraphs, punish windows, phase hazards, accessibility-safe VFX.

## Track C — Optimization
Target: 1080p, GTX 1660-class, 60 FPS, 20 active enemies.
Budgets: Game <= 5.5ms, Render <= 5.5ms, GPU <= 15.5ms, AI avg <= 0.20ms/enemy.
Use significance-based AI ticks, animation budget allocator, Niagara scalability, HLOD/World Partition, pooled transient actors, async loading.
Profile with Unreal Insights + stat unit/gpu/ai + CSV profiler. Never optimize from editor FPS alone.

## Track D — Audio
MetaSounds-ready state model: Exploration, Suspicion, CombatLow, CombatHigh, BossP1, BossP2, BossP3, Victory.
Layer stems: pulse, percussion, low strings, high strings, brass, choir.
CombatIntensity is smoothed and drives stem gains; boss phase transitions are quantized.
Reverb zones: Citadel, Exterior, Cave, Cathedral, Crystal, Storm, Underwater.
SFX concurrency and virtualization required for footsteps, impacts, ambience and magic.

## Acceptance
Build succeeds; 20-enemy benchmark runs; all 7 boss archetypes load from data; audio states transition without hard cuts; realm manifests validate; existing NARIS vertical slice remains playable.

[executed on device: AsusRog (81c43ddb-199e-4bc1-9944-e3faf018908f)]