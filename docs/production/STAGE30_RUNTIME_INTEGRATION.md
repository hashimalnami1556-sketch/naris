# NARIS Stage 30 — Runtime Integration

Status: IMPLEMENTATION CONTRACT / ENGINE VALIDATION PENDING

## 1 Animation
Production character integration requires:
- AnimBP with Idle/Walk/Run locomotion state machine or blendspace.
- Speed and IsInAir driven from CharacterMovement.
- Attack and Dodge Montages using dedicated slots.
- AnimNotifies for attack trace begin/end, stamina commit, dodge i-frames, and foot contacts.
- No stamina/attack state commit if montage playback fails.
- Transition QA: Idle→Walk→Run→Stop, 45/90/135/180 pivots, Attack→Recovery, Dodge→Recovery.
- Foot IK and contact curves remain mandatory for production acceptance.

## 2 PBR Materials
Every production environment material must provide valid UVs and physically based inputs:
BaseColor, Normal, Roughness, Metallic where applicable, and AO where authored.
Ground uses macro/micro tiling, vertex/landscape blending, detail normal and breakup masks.
Trees require bark/leaf material separation where available.
Ruins require stone variation, edge/moss/ash breakup and no baked studio lighting.

## 3 UE 5.7 Runtime Gate
Required evidence:
1. C++ Development Editor build succeeds.
2. W04_AshenForest opens without missing production assets.
3. PIE locomotion, attack and dodge execute.
4. Combat damage/stamina/recovery behavior passes.
5. Collision/NavMesh/AI encounters execute.
6. No blocking errors in Output Log.
7. Shipping build remains blocked until all production gates pass.

AsusRog engine execution is required for PASS. Repository-only checks cannot mark Runtime or Visual QA as passed.
