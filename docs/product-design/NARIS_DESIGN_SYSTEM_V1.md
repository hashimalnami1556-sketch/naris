# NARIS — Design System v1

## Purpose
Implementation contract for visual language, UX hierarchy, UI states, and 3D-content presentation. This document complements `NARIS_PRODUCT_DESIGN_MASTER.md`; it does not replace game-system specifications.

## 1. Design principles

1. **Cinematic first, readable always.** Composition may be dramatic, but combat telegraphs, traversal affordances, objectives, and interaction targets remain readable.
2. **Color is semantic.** Accent colors communicate state or narrative meaning rather than decorating every surface.
3. **Silhouette before detail.** Characters, enemies, interactables, and landmarks must read at gameplay distance.
4. **Material storytelling.** Ash, weathering, oxidation, scorching, bone, cloth, leather, and spectral energy carry world history.
5. **Low-chrome UI.** HUD elements occupy only the information needed for the current gameplay state.

## 2. Semantic color tokens

The canonical named accents are:

- `NARIS_FIRE` — supernatural energy / high-intensity combat accent.
- `ROYAL_VIOLET` — rare arcane / cosmic accent.
- `SPIRIT_CYAN` — spirit / interaction readability accent.
- `ANCIENT_GOLD` — relics / rewards / elite / narrative artifact accent.
- `ASH_NEUTRAL` — world foundation and environmental depth.
- `CHARCOAL_NEUTRAL` — dark UI and silhouette foundation.

Exact numeric color values are intentionally not hard-coded here because the existing source material establishes the semantic palette names, not a single authoritative color-profile specification. Numeric tokens must be locked during visual QA and then propagated to all implementation files.

## 3. Typography contract

- Use one primary readable UI family consistently across HUD, menus, objectives, and settings.
- Use a display treatment only for titles, chapter cards, and cinematic overlays.
- Do not bake gameplay text into 3D textures.
- Support Arabic and English from the same component system.
- Every text component must define normal, focus/hover, disabled, warning, and critical states where applicable.

## 4. Spacing and layout

Use a consistent base spacing scale in implementation. Component dimensions must be tokenized rather than independently tuned per screen.

Recommended component hierarchy:

`Screen → Section → Panel → Component → State`

The final numeric spacing scale is an implementation decision and should be centralized in the UI theme rather than duplicated in individual screens.

## 5. HUD contract

### Persistent
- Health
- Stamina / traversal resource when relevant
- Active ability state

### Contextual
- Interaction prompt
- Objective marker
- Damage/critical feedback
- Loot/reward confirmation
- Status effects

### Rules
- Contextual elements disappear when inactive.
- HUD must preserve the playfield and enemy silhouettes.
- Critical state changes require redundant cues where practical: motion, iconography, contrast, and/or audio rather than color alone.

## 6. Menu components

Required states:

- default
- selected/focused
- pressed/confirmed
- disabled
- unavailable/locked
- warning
- error
- loading

Primary hierarchy:

`Pause → Inventory/Equipment → Abilities → Map/Objective → Settings → Accessibility`

## 7. 3D presentation rules

### Hero
- Establish silhouette, face readability, signature equipment, and supernatural identity before micro-detail.
- Hero materials should expose controlled roughness variation and localized emissive detail.

### Enemies
- Every enemy family requires a distinct silhouette and attack-readability profile.
- Elite/boss variants must communicate hierarchy without relying only on a UI health bar.

### Environment
- Repeatable modules should share material sets and support instancing.
- Landmark assets may receive higher budgets when they materially improve navigation or narrative composition.

## 8. Accessibility

- Never encode critical information by color alone.
- Provide scalable text where the UI framework permits it.
- Keep interaction prompts explicit.
- Avoid unnecessary flashing or rapidly alternating UI effects.
- Maintain sufficient contrast for critical information against the current scene.

## 9. Design review checklist

- [ ] Visual identity consistent
- [ ] Silhouette readable
- [ ] Gameplay information prioritized
- [ ] States specified
- [ ] Arabic/English text behavior considered
- [ ] Color semantics documented
- [ ] Accessibility reviewed
- [ ] Runtime implementation target identified
- [ ] Performance implications recorded
- [ ] Asset ID / screen ID assigned
