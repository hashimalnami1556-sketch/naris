# NARIS — Figma, Blender and Neon integration

Updated: 2026-09-23

This document defines how Figma, Blender and Neon fit the canonical Unreal/Windows production path. It does not claim that engine runtime or cloud backend execution has been verified.

## Integration status

| Tool | Role | Current evidence | Next executable gate |
|---|---|---|---|
| Figma | UI/UX specification and handoff | Live design file created with 3 Starter-compatible pages | Build production components/screens, then map to Unreal UMG/CommonUI |
| Blender | DCC for modeling, UVs, rigging, animation, collision helpers and export | Repository export/validation script is checked in | Run script on an online Blender host and import outputs into Unreal |
| Neon | Lakebase Postgres backend for player/profile/save/telemetry services | Schema contract checked in; remote project is not bound | Bind an actual Neon project/branch, apply migration on a development branch, verify API/runtime |

## Figma

Live file:
https://www.figma.com/design/lYSmWwGHXCEXODKpG9bpJH

Starter-plan page structure:
- `00_Foundations`
- `01_Game_UI`
- `02_Handoff`

The UI page consolidates HUD, menus/settings, inventory/crafting, world map/quest, store/marketplace and accessibility/localization workstreams. Design approval remains separate from Unreal implementation evidence.

### Handoff rule

`Figma approved state -> token/state mapping -> Unreal UMG/CommonUI widget -> input states -> EN/AR layout QA -> engine screenshot comparison`

## Blender

Canonical source directory for authored DCC work should remain outside generated Unreal binaries. The checked-in helper is:

`tools/blender/naris_export.py`

Its purpose is to:
- validate production naming;
- check transforms and mesh data;
- detect missing UVs;
- report likely collision/LOD naming;
- export selected approved objects to FBX and glTF using deterministic settings;
- emit a JSON manifest that can be compared against the master asset registry.

Recommended source convention:

`assets/source/blender/<world>/<asset-id>/<asset-id>.blend`

Recommended exchange convention:

`assets/exchange/<world>/<asset-id>/`

Do not mark a Blender asset engine-ready until Unreal import, materials, collisions, LOD/Nanite policy, scale, skeleton/animation and performance checks pass.

## Neon

The repository intentionally does not contain a live connection string or secret.

Canonical schema seed:
`backend/neon/schema/001_core.sql`

Initial backend scope:
- player account/profile linkage;
- cloud save slot metadata and versioning;
- inventory ownership state;
- entitlement state;
- gameplay/session telemetry suitable for balancing and QA.

The schema is a contract only until it is applied to an isolated Neon development branch and tested. Production migrations must never be executed ad hoc from chat.

## Source-of-truth boundaries

- Figma = design truth, not engine runtime truth.
- Blender = DCC/source-asset truth, not successful Unreal import proof.
- Neon schema = backend data-contract truth, not deployed-service proof.
- Unreal build/playtest remains the final runtime evidence for game behavior.
