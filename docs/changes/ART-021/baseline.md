# ART-021 — Owner-approved visual reference lock
Date: 2026-11-13. Target UE 5.7, NARIS W04.
Owner instruction: preserve every approved logo, UI, character, weapon, environment, design and effect without artistic redesign. Technical rig/cloth/socket/IK fixes must preserve visual identity.
## Reference index (sampled frames, not defect measurements)
| ID | Original file | Sample seconds | Observed content |
|---|---|---|---|
| V1 | 3B83CC83-4A20-45F8-BA53-E02A63517B70.mp4 | 6.23,21.79,40.47,56.04 | wings, ruins, volcanic gate, Call Of Narsec credits |
| V2 | E832F683-E9BF-42B0-8F7E-CA66B03FDAEC.mov | 0.80,2.79,5.17,7.16 | NARIS logo, hero, dragons, citadel |
| V3 | gemini_generated_video_1301BB1B.mp4 | 0.80,2.80,5.20,7.20 | NARIS logo, blue energy, dragons |
| V4 | gemini_generated_video_659D30FC.mp4 | 0.80,2.80,5.20,7.20 | hero face, blue eye, layered scarf, forest |
| V5 | gemini_generated_video_7C03F426.MP4 | 0.80,2.80,5.20,7.20 | volcanic gate, ruins, red-eyed boss |
| V6 | gemini_generated_video_7DA15E2B.mp4 | 0.80,2.80,5.20,7.20 | running hero, gate, blue sword, boss |
| V7 | gemini_generated_video_EDCD676A.mp4 | 0.80,2.80,5.20,7.20 | HVM logo, eclipse citadel, fire creature, blue/fire effects |
Preserve branding variants in context; no silent normalization. Original binary references remain in user handoff, not committed here. Still image relevance and exhaustive shot review remain pending.
## Execution gates
ENV-020: authorized AsusRog, actual project path, UE version, clean Git baseline, inventory of skeleton/cloth/physics/socket/IK/AnimBP/montages/test map. Remote Desktop Commander authorization failed; Remote Arc reports zero paired computer agents.
CHAR-022: cape collision/skin/Chaos Cloth, zero visible leg penetration in three idle/run/attack loops.
CHAR-023: weapon socket and grip pivot; proposed drift <=1cm and <=2 degrees during 360-degree turn.
ANIM-024: retarget and montage transition/interrupt tests.
ANIM-025: Foot IK; proposed planted-foot drift and ground gap <=2cm on 0/15/30 degree slopes.
WORLD-026: volcanic gate reference composition and traversal.
UI-027: exact approved visual design, functional controls, EN/AR RTL.
QA-028: fixed 1920x1080 seed/quality before/after/diff, Development build, Project.* tests, server+2 clients, fpschart, RAM/VRAM.
BUILD-029: BuildCookRun and packaged executable smoke test; only merge after gates pass.
## Evidence / rollback
28 sampled frames from seven videos, offline handoff ZIP CRC verified. No actual UE screenshots, asset mutations, build, FPS or memory measurements. Proposed acceptance thresholds are not measured results. Rollback: revert this documentation-only commit; originals untouched. Do not merge or mark implementation approved.
