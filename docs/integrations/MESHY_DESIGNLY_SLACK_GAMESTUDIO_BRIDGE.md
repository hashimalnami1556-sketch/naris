# NARIS Tool Bridge — Meshy / Designly / Slack / Game Studio

## Objective

Create one production loop in which visual design decisions become registered game assets and runtime-ready content without losing provenance or quality gates.

## Pipeline

`Design reference → Design system → 3D generation → DCC cleanup → Asset registry → Runtime integration → Playtest → Approval`

## Meshy role

Mesh generation is an upstream authoring step. Generated meshes are never accepted directly as final runtime assets. Each generated asset passes Blender cleanup, UV/material review, pivot normalization, collision authoring, LOD review, GLB export, optimization, and runtime validation.

## Designly role

Design tooling defines the visual system, UI component states, interaction hierarchy, iconography, typography, color tokens, spacing, and reference boards. Designs must expose implementation states rather than only static screenshots.

## Slack role

Slack is the handoff and review layer when an appropriate project channel exists. Required review message structure:

- Asset ID
- Design version
- Source/reference
- Current status
- Preview or artifact
- Performance budget
- Review decision
- Next action

No channel is assumed when none can be discovered.

## Game Studio role

Game Studio routes implementation to the correct browser-game specialist. For an explicit 3D browser runtime, use vanilla Three.js for plain TypeScript/Vite or React Three Fiber for a React-hosted runtime. Keep simulation state outside the renderer and use DOM overlays for text-heavy HUD/menu surfaces.

## Integration contract

Every asset must have:

1. Stable semantic ID.
2. Source/reference record.
3. Design approval state.
4. Runtime format.
5. LOD/collision/material metadata where applicable.
6. Optimization status.
7. Integration target.
8. Validation result.

## Current tool availability

The connected workspace exposes Slack and GitHub. No installed Meshy or Designly connector was available in this session, so the bridge is documented without pretending that those services were executed. The project can still proceed through the defined interfaces and equivalent upstream tools.
