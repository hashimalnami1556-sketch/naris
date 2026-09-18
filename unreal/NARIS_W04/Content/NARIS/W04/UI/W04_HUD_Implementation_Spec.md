# W04 HUD IMPLEMENTATION SPEC

## Runtime bindings
- Health -> Player NarisCombatComponent.Health / MaxHealth.
- Energy -> NarisEnergyComponent.Energy / MaxEnergy.
- Resonance -> NarisCombatComponent.Resonance / MaxResonance.
- Essence -> NarisEnergyComponent.ActiveEssence.
- Boss -> BoneBeastCombatComponent Health/Poise and BoneBeastPhaseComponent Phase.
- Arabic RTL and English localization are required.

## HUD states
Normal, LowHealth, ResonanceReady, BossEncounter, ExecutionWindow, Dead, Paused.

## Accessibility
Subtitle toggle, text scale, reduced motion, high contrast, controller remap.

## Rule
No decorative widget is considered complete until it is connected to runtime state and save/load.
