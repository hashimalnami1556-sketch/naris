# NARIS Asset Handoff Template

Use this record for every Meshy/Designly/Game Studio handoff.

## Identity

- Asset ID:
- Family: `CHR | ENV | PROP | FX | UI`
- Design version:
- Owner:
- Priority: `P0 | P1 | P2`

## Source

- Reference path:
- Concept/design source:
- Generation source/tool:
- Source asset path:

## Production

- Status: `CONCEPT | APPROVED | PRODUCTION | INTEGRATED | VALIDATED`
- Runtime target:
- Runtime format: `GLB/glTF 2.0`
- LOD policy:
- Collision policy:
- Material/PBR policy:
- Texture budget:

## QA gates

- [ ] Visual identity
- [ ] Silhouette/readability
- [ ] Topology/UV
- [ ] Materials
- [ ] Pivot/units
- [ ] Collision
- [ ] LOD
- [ ] Runtime export
- [ ] Memory/draw-call review
- [ ] Playtest validation

## Review

- Preview/artifact:
- Performance observations:
- Reviewer:
- Decision: `APPROVED | CHANGES_REQUESTED | BLOCKED`
- Blocking issue:
- Next action:

## Collaboration message

`[NARIS][ASSET] <Asset ID> — <status> — <decision>`

Include the asset ID, design version, source/reference, status, preview/artifact, performance budget, review decision, and next action. Never approve an asset solely because a generator produced it.
