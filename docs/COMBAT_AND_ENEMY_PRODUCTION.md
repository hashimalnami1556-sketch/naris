# NARIS Combat & Enemy Production Standard

## Combat pillars

1. Readable telegraphs before high-damage attacks.
2. Distinct enemy silhouettes and attack signatures.
3. Hit reactions with controlled stagger budgets.
4. Animation-driven timing rather than arbitrary damage ticks.
5. Every weapon has a distinct risk/reward profile.
6. Bosses change behavior by phase rather than only gaining health.

## Enemy archetypes

| Archetype | Function | Core behavior |
|---|---|---|
| Grunt | pressure | close-range pursuit, flank, retreat |
| Ranged | spacing | maintain distance, punish healing/recovery |
| Elite | threat | armor, stance breaks, signature combo |
| Controller | arena control | zones, summons, movement denial |
| Assassin | burst | stealth/teleport, high commitment attack |
| Tank | anchor | slow movement, guard, heavy stagger |
| Boss | encounter | phases, arena mechanics, unique VFX/audio |

## Required data per enemy

`asset_id`, `archetype`, `health`, `poise`, `armor`, `move_speed`, `detection_range`, `attack_range`, `damage_profile`, `telegraph_ms`, `recovery_ms`, `stagger_rules`, `resistances`, `loot_table`, `animation_set`, `vfx_set`, `sfx_set`, `arena_rules`.

## Weapon families

Sword, greatsword, dagger, bow, spear, scythe, hammer and mace are the initial families. Each family requires light/heavy attacks, dodge interaction, hit reaction, impact VFX, audio events and stamina/resource rules.

## Mace revision target

`NARIS-W04-WPN-MACE-0001` is a massive infernal club/mace: heavy dark metal, asymmetrical brutal head, worn surfaces and restrained ancient engravings. It must read clearly at gameplay distance and remain performant through LODs.

## Character revision target

The supplied demon-like enemy reference is treated as a visual source only. The production revision adds a heavy tail, replaces the hand weapon with the Infernal Mace, and reduces horn scale while preserving the approved anatomy, armor language and material direction.

## Animation gates

- locomotion
- idle variants
- anticipation
- active hit frame
- recovery
- hit reaction
- stagger
- death
- traversal if applicable
- boss phase transitions

## QA gates

No enemy is approved until collision, nav behavior, attack timing, animation events, damage windows, VFX readability, audio events, LOD transitions and frame-time impact are verified in the target runtime.
