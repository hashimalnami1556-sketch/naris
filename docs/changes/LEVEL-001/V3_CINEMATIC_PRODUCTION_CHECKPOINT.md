# CALL OF NARIS — Cinematic V3 production checkpoint
Date: 2026-11-23
Status: REVIEW ONLY / NO MERGE / NO PRODUCTION APPROVAL
Change-ID: LEVEL-001 (existing camera+map quality gate)

## Decision
Reject the flat visual V2 as a shipping-quality design and replace its art-direction target with a cinematic, full-scene dark fantasy composition. This is an art-quality **reference**, not an actual Unreal frame or proof that the game matches flagship titles.

## Work actually completed outside Unreal
- Original user's 5 GLB files were audited: 154,023 total triangles. Character 1 and Character 3 each have 0 GLB skin and 0 animation; NARIS Rigged Prototype has 1 skin and 1 animation.
- Built a browser-only cinematic interaction experiment (menu, pseudo-gameplay, HUD, attack/dodge/pause/quest, 4 moods, English/Arabic RTL, high contrast/reduced motion) and passed 20/20 browser integration checks. **Not gameplay in UE; not actual 3D player movement.**
- Produced a genuine glTF/GLB diorama study using 4 of the user's source geometry assets plus procedural terrain/ruins: 317 scene nodes; offline GLB re-import check passed. **Not a shipped map or art-quality approval.**
- Authored non-destructive Unreal Editor Python source to duplicate the map and inspect/fix only two known camera-obstructing oversized props, refusing overwrite. Code compiled as Python, **never executed in Unreal**.
- Prepared Development automation/BuildCookRun shell; server+two-clients, 1080p benchmark, original 1920x1080 screenshots and UE Automation remain **NOT RUN** this turn.

## Why Unreal work is blocked
On 2026-11-23, AsusRog showed online via Remote Desktop Commander, but the connector returned: "You've reached this month's Desktop Commander usage, so tool calls are paused." Do not retry or claim an editor build, screenshots, or Git integration test.

## Engineering acceptance gates for LEVEL-001
1. Original map SHA unchanged, isolated review map only; source baseline/seed/resolution recorded.
2. Spawn and camera actual collision, sweep and raycast clear. AABB check alone is not enough.
3. Original vs review screenshots at 1920×1080, fixed seed and same quality: gameplay, UI, debug and perf; visual human acceptance.
4. UE Development Editor build + BuildCookRun + Automation Project.* PASS.
5. Packaged server + two clients: join AND movement/hit damage replication under latency.
6. Real game 1080p 60fps desktop target, 30fps minimum target, VRAM budget 4GB, CPU/GPU frame metrics.
7. Before/after/diff, rollback, changelog and linked PR; do not merge until all gates are green.

## Source files
The full preview/code, imagery, five source GLBs, audit receipts, GLB diorama, and Unreal scripts are provided as downloadable artifacts in the associated ChatGPT conversation. They have not been uploaded as repository binaries. Do not infer that this branch contains runnable V3 or final UE assets.

## Primary references
- Epic performance profiling: https://dev.epicgames.com/documentation/en-us/unreal-engine/introduction-to-performance-profiling-and-configuration-in-unreal-engine
- Epic Lumen: https://dev.epicgames.com/documentation/en-us/unreal-engine/lumen-technical-details-in-unreal-engine
- glTF spec: https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html
