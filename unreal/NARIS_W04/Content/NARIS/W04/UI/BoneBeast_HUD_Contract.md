# Bone Beast HUD Contract

## Required HUD elements
- Boss nameplate: BONE BEAST
- Boss health bar
- Phase indicator: P1/P2/P3
- Stagger state indicator
- Encounter state indicator
- Optional arena hazard warning

## Event bindings
- EncounterStarted -> show HUD
- DamageTaken -> update health
- PhaseTransition -> update phase presentation
- Stagger -> show stagger state
- Death -> play defeat state
- EncounterComplete -> hide/resolve HUD

## Authority
HUD is presentation-only. Health and phase are read from authoritative gameplay state/events.

## Accessibility
- Do not rely on color alone for phase/state communication.
- Support scalable text and UI-safe margins.
