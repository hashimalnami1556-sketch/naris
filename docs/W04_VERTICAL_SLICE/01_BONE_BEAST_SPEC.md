# Bone Beast — Technical Spec

**Asset ID:** `NARIS-ENM-W04-0004`  
**World:** `W04`  
**Arena:** Bone Beast Arena

## Runtime contract
- HP: `TUNE`
- Damage: `TUNE`
- Stamina pressure: High
- Phases: 3 proposed execution phases; exact thresholds are `TUNE`.
- Theme: Bone / Ash / Aether

## Player counterplay
- Parry
- Dodge
- Environmental positioning

## Dependencies
Arena, AI, animations, VFX, audio, UI, quest.

## Authority model
`BossController` owns phase/state. Downstream systems consume events:
`Boss.PhaseChanged`, `Boss.AttackStarted`, `Boss.AttackImpact`, `Boss.Staggered`, `Boss.Died`.

## Non-goals
Do not invent final HP, damage, cooldowns, or phase thresholds before playtest evidence exists.
