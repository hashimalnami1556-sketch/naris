# ANIM-024 — actual Windows UE5.7.4 Build, Cook, Package and two-client login QA (2026-11-21)

**Evidence quality:** Windows UE **real execution** on paired AsusRog. All operations use the **isolated review copy** `C:\dev\NARIS_ANIM024_20261121\InputReviewProject`, derived from existing local `NARIS_ENV020_20261114\unreal\NARIS_W04`. This is a **review Development build**, not an approved game release or a GitHub-stored binary.

## Tested configuration
- Engine `5.7.4-51494982+++UE5+Release-5.7`; Windows 11; Intel Core i5-14400F; 32GB RAM; NVIDIA GeForce RTX 3050 (~4GB VRAM).
- Isolated input normalization: 57 scalar `Key=X` mappings (43 action, 14 axis), one malformed escaped newline fixed, no input `Key=()`.
- Exact W04 `Project.Maps.PIE` before on original: **FAIL**, 9 errors, engine exit 1. After isolated correction: **PASS WITH 13 WARNINGS**, 0 errors, engine exit 0; source correction validated by GitHub TDD.

## Actual Development Build evidence

| Attempt | Tool / settings | Result |
| --- | --- | --- |
| Editor attempt 1 | `Build.bat NARIS_W04Editor Win64 Development`, Unreal Build Accelerator 10 concurrent actions | Stalled at action 1/50; isolated UBT process was stopped; **NO PASS** |
| Editor attempt 2 | `-NoUBA`, default up to 10 actions | **FAIL**, MSVC `C3859` PCH virtual memory and `C1076` compiler internal heap limit; not proof of C++ source defect |
| Editor attempt 3 | `-NoUBA -MaxParallelActions=2` | **PASS**, `UnrealEditor-NARIS_W04.dll` linked; `Result: Succeeded`, process exit 0 |
| Game target | `Build.bat NARIS_W04 Win64 Development -NoUBA -MaxParallelActions=2` | **PASS**, 54/54 actions, executable `NARIS_W04.exe` linked, process exit 0 |

SHA256 of retained local logs:
- `input_fix_build_lowparallel.log`: `CBF22D3EE26D5A53324875C512D629B409771C756D3A04A9B46D6E60C680D25F`
- `input_fix_game_build_lowparallel.log`: `8D09B4DDEF23A163C8333DDF6099E22E9E616E07BECA403236E4E343598F1A5E`

## Actual BuildCookRun

`RunUAT.bat BuildCookRun -project=<isolated W04> -noP4 -platform=Win64 -clientconfig=Development -skipbuild -cook -stage -pak -archive -archivedirectory=<isolated PackageReview> -unattended -utf8output`

- **PASS** `BUILD SUCCESSFUL`, `AutomationTool exiting with ExitCode=0 (Success)`.
- Cook inspected **443** packages: **436 cooked, 7 skipped by platform**.
- `UnrealPak.exe` stages both exited 0, and Archive completed.
- Staged location: `C:\dev\NARIS_ANIM024_20261121\PackageReview\Windows`; **47 files, approx 841MB**, below the 8GB package target **for this package only**.
- Contains `Windows\NARIS_W04.exe` launcher, `Windows\NARIS_W04\Binaries\Win64\NARIS_W04.exe` (actual Development executable), and `Windows\NARIS_W04\Content\Paks\NARIS_W04-Windows.pak`.
- BuildCookRun log `input_fix_buildcookrun.log` SHA256 `BCE1CD60A5F0B958D5BCD5ADA18EC068AF752841BAD3E5820217708A4686E98A`.

## Two-client local network handshake

From the **packaged Development executable** launched **one listen server** on loopback port **17777** with map `/Game/NARIS/W04/Maps/W04_Prototype?listen`, plus **two independent clients** connecting to `127.0.0.1:17777`; flags include `-nullrhi -nosound -unattended` (valid for protocol smoke, NOT visual/perf).

- Server logged **`Join succeeded` twice**, with two distinct client login identifiers and control channels accepted.
- Each client logged **`Welcomed by server`** on `/Game/NARIS/W04/Maps/W04_Prototype`, GameMode `/Script/NARIS_W04.NarisGameMode`.
- Harness stopped its three started processes at end. No remaining packaged NARIS_W04 processes observed immediately afterward.
- Local logs: `net_server.log`, `net_client1.log`, `net_client2.log`; source harness `net_smoke.ps1`; result `net_smoke_report.json` SHA256 `22A99A14DF2EF72859994840F1A4327177E69F1AFD8AB0E853EEDA6E05557F9B`.
- Result: **LOGIN/CONNECTION SMOKE PASS**, **NOT** verified gameplay replication, combat authority, damage, montage playback, late join, disconnections, or dedicated server binary.

## Remaining unreleased gates

1. Target 87-bone production hero import, real source licensed animation, approved source/target IK Rig + IK Retargeter, playable AnimBP/Montages and notifies. Local Ashen Vessel 53 bones, Bone Beast 43; wolf V8/V9 both 35 bones and share skeleton. Exact 10 W04 manifest Montage paths still failed to load in local review; four *different* Wolf V9 montages do load.
2. Original PIE test's six missing UI icons, missing `/Script/AugmentedReality` map import and missing localization `.locmeta` warnings remain; the corrected PIE test passed **with warnings**.
3. Real 1920x1080 image before/after/diff, gameplay GIF, stable game Seed, measured FPS/frametime/RAM/VRAM and visual integrity are **not evidenced by NULLRHI network tests**.
4. Build and Cook success plus two clients connected **do not authorize merge** until gameplay/visual/perf gates pass. **PR #110 remains DRAFT**.
5. `PackageReview` is **local to the user's computer**, not uploaded to GitHub; do not claim a downloadable packaged build via a fabricated sandbox link.

**Rollback / scope:** No original character `.uasset` or map was intentionally modified. Trial copies, compiled outputs, scripts and raw QA logs are in the isolated `NARIS_ANIM024_20261121` directory. Do not clean the user's detached-HEAD original checkout or untracked art. The original input `.ini` modification timestamp shifted during engine startup; without a pre-run hash, byte-identical preservation of that specific file is not proven.

References: [Epic Build Operations](https://dev.epicgames.com/documentation/en-us/unreal-engine/build-operations-cooking-packaging-deploying-and-running-projects-in-unreal-engine); [Epic Testing & Optimizing](https://dev.epicgames.com/documentation/en-us/unreal-engine/testing-and-optimizing-your-content).
