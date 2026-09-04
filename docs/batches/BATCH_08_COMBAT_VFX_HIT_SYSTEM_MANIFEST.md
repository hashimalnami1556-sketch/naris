# NARIS — Batch 08 Manifest
## Combat VFX & Hit System

**Batch:** 08  
**Status:** IN PRODUCTION  
**Predecessor:** Batch 07 — Character & Enemy Factory  
**Project:** CALL OF NARIS / HVM NARIS

---

## Objective

Build the production combat-feedback layer that consumes Batch 07 animation markers, weapon ability hooks, enemy status effects, and combat events.

## Systems

### 1. Hit Event Pipeline
- `HitEvent` canonical event payload
- attacker / defender IDs
- weapon ID
- attack type
- damage type
- hit position / normal
- critical / parry / guard-break flags
- status-effect payload
- animation frame marker
- VFX/SFX routing hooks

### 2. Impact VFX
- light slash impact
- heavy slash impact
- thrust impact
- bone impact
- armor impact
- flesh impact
- ethereal impact
- projectile impact
- ground impact

### 3. Combat Motion Feedback
- hit-stop
- directional camera shake
- impulse response
- stagger feedback
- guard-break feedback
- perfect-parry feedback
- dodge near-miss feedback

### 4. Status VFX
- Bone Hound bleed
- Aether Serpent poison DoT
- burn / ember status
- ash corruption
- aether slow
- radiant cleanse

### 5. Weapon Ability VFX
- `RuneSlash`
- `AetherThrust`
- `AetherArrowRain`

### 6. Enemy Death VFX
- Bone Hound bone-collapse / shard burst
- Aether Serpent `DeathDissolve`
- reusable death-event routing for future enemies and bosses

### 7. Performance
- VFX pooling
- lifetime limits
- distance-based LOD
- burst caps
- deterministic cleanup
- no persistent orphan particles

## Required Deliverables

```text
data/combat/
  hit_event_schema.json
  damage_types.json
  status_effects.json
  vfx_event_map.json

data/vfx/
  impact_library.json
  ability_vfx.json
  death_vfx.json

scripts/combat/
  HitEvent.gd
  HitResolver.gd
  StatusEffectController.gd

scripts/vfx/
  CombatVFXRouter.gd
  VFXPool.gd
  ImpactVFXController.gd
  AbilityVFXController.gd

scripts/camera/
  CombatCameraFeedback.gd
```

## Acceptance Criteria

- Every Batch 07 combat animation can emit deterministic event markers.
- Every hit resolves through one canonical event path.
- VFX are data-driven and pooled.
- Bleed and poison have independent status lifetimes and tick schedules.
- Weapon abilities trigger their assigned VFX without hard-coded scene dependencies.
- Parry, stagger and guard-break have distinct feedback signatures.
- Aether Serpent death dissolve can be triggered from its animation state.
- No VFX allocation spike occurs during ordinary multi-target combat.

## Handoff from Batch 07

Consumed assets and hooks:
- Bone Hound `Bite`, `Death`, `PACK_AGGRO`
- Aether Serpent `Strike`, `DeathDissolve`, `AMBUSH_PATROL`
- Emberedge `RuneSlash`
- Aether Spear `AetherThrust`
- Ash Bow `AetherArrowRain`
- Ashen Vessel `DodgeRoll`, `Parry`, `Combo01`, `Combo02`, `RuneSlash`, `AetherStep`, `HitHeavy`, `Stagger`, `Interact`, `DeathDramatic`

**Production rule:** do not create a second combat-event protocol. Extend the canonical Batch 08 schema for future enemies, weapons, bosses, and cinematics.
