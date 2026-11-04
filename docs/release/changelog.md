# Changelog

## [Unreleased]

- CHAR-001-G0 (#86): prioritize Ash Wanderer production acceptance, freeze monster rig expansion and add a draft 92-node export specification with G0–G6 gates. No player-visible behavior has changed.
- CHAR-001-G0 (#86): recover original Ash 92-node specification, supersede the alternative CSV allocation and retain structural checks plus source hashes. No runtime behavior changed.
- Fix CHAR-001 export audit false acceptance for wrong bone counts and invalid hierarchy; merge reviewed execution-board/build-report handoffs. G0 stays open; no gameplay or production approval. Refs #86.

## 2026-11-04 — ENV-003
- Fix Blender exchange collision helper UV/naming checks and exclude Unreal collision proxies from visible GLB exports while retaining FBX helpers.
- Actual Blender synthetic roundtrip and Python regression evidence recorded in docs/changes/ENV-003; Unreal/gameplay validation remains unexecuted.
