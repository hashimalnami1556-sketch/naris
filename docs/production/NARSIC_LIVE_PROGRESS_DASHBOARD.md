# NARSIC Live Production Loading Dashboard

**Date:** 2026-10-01  
**Primary display:** ASUS ROG ultrawide  
**Data source:** `data/PRODUCTION_PROGRESS.json`

## Purpose

Turn development progress into a loading-screen-style production monitor that changes with workflow state.

It must show at a glance:
1. what is complete,
2. what is active,
3. what is being worked on,
4. what is missing or blocked,
5. what happens next.

## Naming

- Product/display title: **NARSIC**
- Technical namespace: **NARIS**
- Existing asset IDs, Unreal module names, paths and schemas are not renamed by this dashboard work.

## Visual rules

- Final visual copy is **English only**.
- 32:9 is the primary composition; 21:9 and 16:9 are fallbacks.
- Use a dark ROG-inspired technical frame while keeping NARSIC world art dominant.
- Avoid crowded thumbnail collages.
- Orange/gold = active; green = verified complete; blue = in progress; gray = locked/pending; red = true blocker.
- Planning percentages must never be shown as QA/build/runtime proof.

## 32:9 layout

- Left 18%: phase rail.
- Center 57%: cinematic NARSIC world/key art.
- Right 25%: workstreams, blockers, missing work, next actions.
- Bottom: a single continuous loading strip and compact workflow state.

## Data binding

Read:
- `current_stage`
- `stages`
- `workstreams`
- `blockers`
- `next_actions`
- `host_status_at_sync`

from `data/PRODUCTION_PROGRESS.json`.

## Progress semantics

The screen carries two different concepts:

- **Display progress** — planning indicator for the owner.
- **Evidence state** — actual source/build/runtime/QA evidence.

Never conflate them.

## Update policy

1. Update the evidence-bearing source/report first.
2. Update `data/PRODUCTION_PROGRESS.json`.
3. Re-render the dashboard.
4. Do not mark a stage complete from file presence alone.
5. Shipping/release states require explicit QA/build evidence.

## Current active gate

**Vertical Slice — W04 Ashen Forest**

Required closure chain:

`Windows editor build → Blender/Unreal bridge → production map/assets → packaged full-loop playtest → performance/QA acceptance`
