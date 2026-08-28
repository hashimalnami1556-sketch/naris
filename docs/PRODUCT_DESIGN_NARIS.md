# NARIS Toolkit — Product Design Record

**Project:** CALL OF NARIS
**Platform:** NARIS Toolkit — Blender-centered game production platform
**Date:** 2026-08-28
**Status:** Product Design exploration / visual direction selection

## Product intent

NARIS Toolkit is a reusable production platform inside Blender, not a simple script or viewer. It is intended to unify asset creation, organization, inspection, optimization, validation, documentation, reuse, and export for game production.

## Primary users

- 3D artists and environment artists
- Character and creature artists
- Technical artists
- LookDev / material artists
- Animators and riggers
- Developers and pipeline TDs
- Producers who need production visibility

## Core user outcome

A creator should be able to open a project, understand its production state immediately, work on an asset or scene without hunting through unrelated panels, validate it against production rules, optimize it, and export an engine-ready deliverable from one coherent workspace.

## Product principles

1. Production-first rather than feature-showcase UI.
2. High information density where technical users need it, without visual clutter.
3. Clear separation between creative work and pipeline/QA work.
4. Fast access to the current asset, scene, validation state, and next action.
5. Modular architecture that can grow with the NARIS Toolkit.
6. Consistent naming, metadata, asset IDs, validation, and export states.
7. Designed for both artists and programmers/technical artists.

## Primary surface

The initial Product Design target is the **NARIS Workbench / Dashboard** inside Blender.

The primary frame should prioritize:

- Current scene / viewport
- Active asset
- Production state / pipeline progress
- Validation status
- Recent or relevant assets
- One clear next action

It should not attempt to expose every NARIS feature simultaneously.

## Core information architecture

- Project
- Workbench
- Assets
- Scene / World
- Materials
- UV / Textures
- Characters
- Rigging / Animation
- VFX
- Lighting / Rendering
- Validation / QA
- Export
- Pipeline / Logs
- Settings

## Visual language

The established CALL OF NARIS visual identity is Dark Fantasy + High Fantasy + Cinematic AAA. Core accents include Naris Fire, Aether Violet, Mist Cyan, and Ancient Gold. The interface should remain professional and production-oriented rather than becoming decorative fantasy UI.

## Design directions explored

### Ashen Industrial

Dark, professional, focused, minimal-distraction workspace. Best foundation for production efficiency and broad team use.

### Aether Tech

Technical, data-rich, developer-friendly workspace. Strong emphasis on pipeline visibility, diagnostics, system state, logs, metrics, validation, and extensibility.

### Ember Forge

Warm, immersive, artist-centric workspace. Strongest for LookDev, lighting, materials, and creative exploration, while retaining production controls.

## Recommended product strategy

Use a **production backbone derived from Ashen Industrial / Aether Tech**, while allowing **Ember Forge visual treatment to influence creative modules such as LookDev, Materials, Lighting, and Render Preview**.

The final system should therefore avoid designing the entire product as a purely cinematic dashboard. The interface must scale to technical artists and developers as well as designers.

## Technical UX requirements

- Blender 4.x+ environment
- Clear scene and asset context at all times
- Deterministic validation results
- Asset IDs and metadata visible when relevant
- Performance metrics without overwhelming the creative workspace
- Export readiness clearly represented
- Logs and diagnostics available without replacing the primary creative surface
- Keyboard-friendly and mouse-efficient interactions
- Modular panels suitable for future NARIS modules

## Current design decision

The next prototype should be designed as a **professional production workbench for artists + technical artists + developers**, not as a cinematic presentation dashboard.

The central viewport remains visually important, but surrounding UI must communicate production state, validation, asset metadata, pipeline progress, and actionable tools with restrained hierarchy.

## Source context

The repository is the versioned production source of truth for CALL OF NARIS specifications, schemas, manifests, automation definitions, and release history. This document records the Product Design direction so future implementation stays aligned with the production pipeline.
