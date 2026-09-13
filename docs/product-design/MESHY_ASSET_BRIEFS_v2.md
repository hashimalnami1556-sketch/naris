# NARIS — Mesh Generation Asset Briefs v2

These briefs are generation-ready specifications. They are not claims that a Mesh-generation connector has executed the jobs.

## Global generation rules
- Style: cinematic dark fantasy, premium game asset
- Real-world scale in meters
- Clean production topology where supported
- Separate major material regions
- Neutral studio preview plus beauty preview
- No baked background geometry
- Preserve silhouette readability
- Avoid excessive micro-detail that harms runtime use

## Priority P0

### NARIS-HERO-001 — Ashen Vessel
Deliverables: full-body hero, neutral pose, game-ready proportions, armor/cloak separation, sword attachment point.
Materials: burned steel, worn leather, ember emissive, ancient-gold accents.
Variants: neutral / combat-ready.

### NARIS-COMP-001 — Celestial Wolf
Deliverables: full-body quadruped companion, clean silhouette, attachment points for aura/VFX.
Materials: silver-white fur, cyan spirit layer, violet astral accents.
Variants: neutral / howl-ready.

### NARIS-ENEMY-001 — Bone Beast
Deliverables: boss-scale skeletal creature with readable armor-break regions.
Required break zones: shoulder armor, jaw plates, back spikes, chest cage.
Core: visible corrupted emissive core.

## Priority P1

NARIS-BOSS-001 — Ash Giant
NARIS-BOSS-002 — Mist Guardian
NARIS-BOSS-003 — Veil Mother
NARIS-WEAPON-001 — Flame Relic Sword
NARIS-WEAPON-002 — Mist Bow
NARIS-WEAPON-003 — Aether Dagger

## Export contract

Source → GLB/glTF → engine import → material validation → collision/LOD → preview → registry → QA.

Do not publish generated geometry directly to the runtime branch. Generated assets enter the art-review gate first.
