# NARIS — Batch 07 Manifest
## Character & Enemy Factory

**Batch:** 07  
**Status:** COMPLETE / LOCKED  
**Project:** CALL OF NARIS / HVM NARIS  
**Production track:** Character & Enemy Factory  
**Next batch:** 08 — Combat VFX & Hit System

---

## 1. Deliverables

### Characters / Enemies

#### Bone Hound
- Type: quadrupedal skeletal creature
- Skeleton: 29 bones
- Width: 1.4 m
- Height: 0.9 m
- AI: `PACK_AGGRO`
- Pack size: 3
- HP: 180
- Sprint speed: 11 m/s
- Status effect: bite-induced bleeding
- Required animations: `Idle`, `Walk`, `Sprint`, `Bite`, `Death`
- Bite requirement: full jaw deformation / jaw bone chain driven during attack

#### Aether Serpent
- Type: ethereal serpentine ambush creature
- Skeleton: 28 bones
- Spine chain length: 4.0 m
- Hover height: 1.2 m
- AI: `AMBUSH_PATROL`
- Environment behavior: hides within ash / concealment zones
- Required animations: `Slither`, `Coil`, `Strike`, `Hood Flare`, `Death Dissolve`
- Death requirement: ethereal dissolve treatment
- Poison: 15 damage/second × 5 seconds

### Weapons

#### Emberedge
- Skeleton: 7 bones
- Structure: handle → guard → blade → tip → FX bones
- Material identity: bone / flame
- Ability: `RuneSlash`

#### Aether Spear
- Skeleton: 8 bones
- Range: 2.2 m
- Visual identity: glowing aether crystal
- Ability: `AetherThrust`

#### Ash Bow
- Skeleton: 13 bones
- Structure: limbs + string + arrow nock
- Range: 30 m
- Ability: `AetherArrowRain`

### Ashen Vessel — Extended Animation Set

1. `DodgeRoll`
2. `Parry`
3. `Combo01`
4. `Combo02`
5. `RuneSlash`
6. `AetherStep`
7. `HitHeavy`
8. `Stagger`
9. `Interact`
10. `DeathDramatic`

### Animation State Machine JSONs

Six state-machine JSON specifications are registered for the character/enemy production layer. Each specification supports, as applicable:
- complete transitions
- `blend_in`
- `blend_out`
- boss phase hooks
- IK setup
- mount system hooks
- pack behavior hooks

---

## 2. Runtime / Integration Contract

All Batch 07 entities must expose stable IDs for engine integration and remain data-driven through JSON manifests/state machines.

Suggested canonical IDs:
- `character.ashen_vessel`
- `enemy.bone_hound`
- `enemy.aether_serpent`
- `weapon.emberedge`
- `weapon.aether_spear`
- `weapon.ash_bow`

Combat status hooks reserved for Batch 08:
- `damage`
- `hit_confirm`
- `bleed`
- `poison_dot`
- `stagger`
- `death`
- `weapon_ability`
- `impact_vfx`

---

## 3. Production Acceptance Criteria

- Skeleton counts match the Batch 07 specification.
- Character scale is authored in meters and uses a consistent root/pivot convention.
- Animation names are stable and engine-safe.
- State machines are deterministic and transition-safe.
- Enemy AI identifiers are data-driven rather than hard-coded into animation assets.
- Weapon abilities are exposed as events/hooks and are not coupled to a single renderer.
- Bone Hound bite supports full jaw motion.
- Aether Serpent Slither drives the complete spine chain.
- Aether Serpent Death Dissolve exposes a VFX trigger for Batch 08.
- Ashen Vessel extended animations expose combat/event markers for hit, parry, dodge and ability systems.

---

## 4. Dependencies

**Consumes:**
- NARIS visual identity / Art Direction
- existing character/enemy data layer
- existing JSON → engine bridge
- existing combat and energy architecture

**Feeds:**
- Batch 08 Combat VFX & Hit System
- enemy encounter director
- combat resolver
- animation event system
- weapon ability system
- cinematic / boss systems

---

## 5. Roadmap

| Batch | Scope | Status |
|---|---|---|
| 03–07 | Core production batches | COMPLETE |
| **07** | **Character & Enemy Factory** | **COMPLETE** |
| **08** | **Combat VFX & Hit System** | **NEXT** |
| 09 | UI / UX | PENDING |
| 10 | Audio / Cinematics | PENDING |

---

## 6. Batch 08 Handoff

Batch 08 must consume the hit/event hooks created by Batch 07 and implement the production combat feedback layer:

- hit sparks and directional impact VFX
- slash / thrust / projectile trails
- hit-stop and camera shake hooks
- damage-number / combat feedback hooks
- bleed and poison VFX
- parry / perfect-parry VFX
- stagger / guard-break feedback
- weapon ability VFX for `RuneSlash`, `AetherThrust`, `AetherArrowRain`
- enemy death VFX, including Aether Serpent dissolve
- VFX pooling and lifetime management
- hitbox/hurtbox event routing
- deterministic combat-event manifest

**Batch 07 is therefore considered production-locked and handed off to Batch 08.**
