# NARSIC — UE5.7 Verification Report — 2026-10-07

**Product brand:** NARSIC  
**Technical namespace:** NARIS  
**Engine:** Unreal Engine 5.7.4  
**Host:** AsusRog  
**Primary map:** `/Game/NARIS/Maps/L_AshMap_Assembly`  
**Release posture:** Vertical Slice verification; not Release Candidate.

## Executive result

The W04 Unreal implementation now has verified Windows compilation, Shipping and Development packaging, packaged gameplay QA, and packaged four-player listen-server connectivity. These results close the former build/package uncertainty but do **not** close production-art, navigation, frame-time, localization, controller, or end-to-end playthrough gates.

## Build and packaging evidence

| Gate | Result |
|---|---|
| `NARISEditor Win64 Development` | PASS |
| `NARIS Win64 Development` | PASS |
| Shipping `BuildCookRun` | PASS |
| Development `BuildCookRun` | PASS |
| Cook errors | 0 |
| Cook warnings | 2 Lumen scalability/project-setting precedence warnings |
| Cooked packages | 534 |
| IoStore chunks | 1250 |

Shipping archive created on the workstation under `Builds/NARIS_Win64_Shipping_20261007/Windows`.
Development archive created under `Builds/NARIS_Win64_Development_20261007/Windows`.

## Packaged Development gameplay QA

The packaged Development executable was run against `L_AshMap_Assembly` and produced the following results:

| QA gate | Result | Evidence summary |
|---|---|---|
| Combat | PASS | damage, 3-hit combo, dodge, double jump, lock-on, notify-driven hit timing and hit-window callback |
| Objective progression | PASS | Ash Gate reached, boss defeated, objective stage 2, 12 crystals, 4 flasks |
| Save/load | PASS | isolated QA slot round-trip |
| Pause/resume | PASS | paused and resumed correctly |
| Main menu | PASS | menu opened and New Game returned to gameplay state |

Combat runtime evidence included `NotifyDriven=1`, `NotifyTimingUsed=1`, `CallbackSeen=1` and six of six attack clips recognized as notify-driven.

## Cooperative networking acceptance

A packaged Development listen server was launched with `NarisCoopGameMode` on port 7777.

Observed server player counts were `1 → 2 → 3 → 4` as three additional packaged clients connected. A fifth client attempted to connect and was rejected with `PreLogin failure: Server full.` This verifies the current four-player session limit in a real packaged multi-process run.

The repository automation suite `NARIS.Coop` also passed all three available tests:

- `NARIS.Coop.Character.ReplicationDefaults`
- `NARIS.Coop.GameMode.Defaults`
- `NARIS.Coop.Session.FourPlayerCap`

## Performance probe

A packaged Development D3D12 benchmark was launched on the workstation RTX 3050. D3D12 initialized successfully and the runtime observed a 3297 MB texture pool. The run exited normally.

This is **not yet a performance acceptance result** because frame-time percentiles and memory/stability thresholds have not been captured. The runtime also reported that `NARIS_PCD3D_SM5.stable.upipelinecache` was not found; PSO cache generation remains an optimization task.

## Navigation blocker discovered

The packaged navigation probe initialized `RecastNavMesh-Default` and issued move requests, but both the Celestial Wolf and spawned Bone Beast reported `Travelled=0.0` at the current probe point.

Navigation/path-following therefore remains **unresolved** and must not be marked complete.

## Remaining Vertical Slice blockers

1. Repair packaged AI path-following and prove non-zero traversal for companion/enemy actors.
2. Replace or explicitly approve 210 audited Engine BasicShape actors: 192 `ENV`, 8 `ZONE`, 10 `LANDMARK`.
3. Finish production master materials/instances and collision/traversal validation after placeholder replacement.
4. Finish remaining character/enemy technical-art acceptance and broader production animation coverage.
5. Resolve sixteen production audio masters and fourteen Niagara systems.
6. Run one continuous packaged W04 playthrough covering checkpoint, boss, save/load and completion.
7. Capture packaged frame-time percentiles, memory and stability evidence on AsusRog RTX 3050.
8. Close ultrawide, controller and EN/AR localization regression.

## Status consequence

The build/package blocker is closed. Packaged core-system QA and four-player connection acceptance are now evidence-backed. The project remains in **Vertical Slice**, with production-world replacement, navigation, content payload, performance and final regression as the dominant remaining gates.

## Operations-menu implementation — 2026-10-08

The supplied tactical-menu references were translated into the **real UE5.7 packaged runtime**, not retained as a concept mockup.

Implemented runtime structure:

- Product title remains **NARSIC**.
- Six-tab navigation: `OVERVIEW / MISSIONS / CHALLENGES / ARSENAL / TEAM / SETTINGS`.
- Full-screen translucent tactical overlay with top tab rail and controller shoulder navigation.
- Challenge cards and progress bars are bound to actual runtime values such as crystals, combo, health and objective stage.
- Mission panel exposes current W04 mission, objective checklist, rewards and stage progression.
- Right-side mission-control column mirrors the supplied reference hierarchy.
- Team page provides a scoreboard/party-status layout.
- Settings page uses the same dense panel language.
- Revised NARSIC main menu and pause surface use the same visual system.
- Keyboard bindings: `Tab` toggle, `[` previous tab, `]` next tab, `Esc` back.
- Gamepad bindings: View/Special Left toggle, L1 previous, R1 next, Menu/Special Right back.

Validation evidence:

- `NARIS Win64 Development` compile: **PASS**.
- Development BuildCookRun archive: `Builds/NARIS_Win64_Development_20261008_UI/Windows`: **PASS**.
- Cook: **0 errors / 2 existing Lumen precedence warnings**.
- Packaged UI state QA: `NARIS_UI_QA_RESULT Pass=1 Open=1 Next=1 Prev=1 Close=1 Tab=2`.

This verifies menu state, packaging and runtime integration. A live visual pass at the target ultrawide resolution remains required for final spacing/readability acceptance.

