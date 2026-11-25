# ART-001 — Figma Rebuild Specification

**Status:** implementation brief only; not visual approval  
**Canonical file:** https://www.figma.com/design/lYSmWwGHXCEXODKpG9bpJH  
**Reference set:** existing Adobe NARIS main menu, gameplay HUD, bilingual inventory, settings, world selection and art-direction board  
**Target review canvas:** 1920×1080

## 1. Hard constraints

- Preserve the established illustrated/painterly NARIS art direction. Do not replace character identity, silhouettes, costume, weapon design, environment landmarks or palette with generic photorealism.
- Reuse existing V4/V5.2 frames, styles, tokens and source assets where they already meet the contract. Keep the V6 experiment separate until repaired and reviewed.
- Use editable Figma layers: text, vector/icon layers, components, variants and image fills. A flattened full-screen image is not an acceptable UI deliverable.
- The three ART-001 Firefly outputs are image-layer concepts only. Keep registry status `concept`; do not label them approved, final, runtime-ready, mesh, texture or map.
- Do not change the canonical UE project or claim runtime implementation from this Figma-only task.

## 2. Main Menu — node 17:33

### Composition
- Use a 16:9 frame at 1920×1080.
- Establish a clear two-zone composition: a calm, low-detail menu area on the LEFT and the Ashen Vessel / bell-gate focal art on the RIGHT.
- The title `CALL OF NARIS` must remain on one line at the target canvas. Keep it distinct from the subtitle; no collision or wrap.
- Preserve negative space around the title and menu stack. Do not place bright particles, character details or landmark edges behind button labels.
- Use the established bronze/ember frame language and restrained luminous accents from the existing NARIS source. Avoid unrelated modern mobile-card styling.

### Menu stack
- Continue, New Game, World/Chapter selection, Settings, Credits and Exit should use consistent button component dimensions and vertical rhythm.
- Button labels must be horizontally and vertically centered using component constraints, not manual offset hacks.
- Include normal, hover, pressed, selected/focus, disabled and controller-focus states.
- Continue with no compatible save must be visibly disabled and have a concise explanatory tooltip or helper text.
- Keyboard/controller focus must be visually distinguishable from mouse hover.

### Acceptance
- Source artwork visibly renders in the frame; no black/missing image fill.
- Title is single-line; title/subtitle do not overlap.
- No button label is top-aligned or clipped.
- At least one 1920×1080 screenshot is captured and inspected before approval.

## 3. W04 Gameplay HUD — node 17:64

Keep the play space unobstructed and preserve the source HUD's illustrated NARIS frame language.

Required elements:
- Player health.
- Energy/resonance resource.
- Five essence/ability slots with key/controller bindings.
- Objective/quest text and clear interaction prompt.
- Minimap or navigation element consistent with the established reference.
- Boss health presentation only when a boss encounter is active; otherwise do not reserve a permanent oversized bar.
- Damage, resource change, interaction, cooldown and objective-update feedback states.

All displayed values in design frames must be marked as sample data. No mock value is a gameplay balance commitment.

## 4. Boss HUD — node 17:117

- Boss name and health bar must read clearly without covering the boss silhouette or telegraph zone.
- Keep health fill, damage lag and phase marker as separate editable layers/components.
- Use the established W04 boss encounter style and restrained ember accent; do not add unapproved enemy anatomy or substitute the quadruped Bone Beast with a humanoid.
- Include active, depleted, phase-transition and encounter-complete states as component variants.
- Validate readability at 1920×1080 and at a reduced preview scale.

## 5. Pause — node 17:146

- Preserve a readable gameplay backdrop with a controlled dim layer; do not turn the whole scene into a black screen.
- Menu hierarchy: Resume, Restart Checkpoint, Settings, Return to Main Menu.
- Destructive/return actions require a confirmation state and clear focus order.
- Include keyboard and controller navigation, with Resume as the initial focus.
- Ensure the pause overlay does not obscure the state of the current objective or boss encounter unnecessarily.

## 6. W04 Quest Route — node 17:179

- Show the route as a sequence of existing W04 landmarks, not invented locations.
- Distinguish current objective, completed objective and locked/future objective through shape/icon plus color; color alone is insufficient.
- Use Ashen Forest / Waystone / Memory Crystal terminology consistently with the project.
- Keep route labels editable and localizable; avoid baked-in text on the image.

## 7. Relics / Inventory — node 17:214

- Follow the existing bilingual inventory/equipment reference.
- Keep item grid, selected-item details, equipped slots and comparison data as separate components.
- Selection, equipped, unavailable, locked and newly acquired states must be distinct.
- Avoid introducing new stats or item names as if they were approved game data; mark any example values as sample.
- Preserve item icon source/provenance and do not flatten the screen.

## 8. Arabic RTL — node 17:263

- Arabic must use genuine RTL text direction and right-aligned layout, not mirrored English screenshots.
- Mirror directional layout where appropriate, but do not mirror character art, logos, weapon silhouettes or non-directional icons.
- Verify title, subtitle, menu labels, helper text, settings controls, HUD objective and inventory labels.
- Check mixed Arabic/English terms, numerals, key bindings and punctuation for correct ordering.
- Use the same frame dimensions and component structure as the English version.

## 9. Accessibility and interaction

- Establish a predictable focus order for keyboard and controller.
- Provide visible focus state, not hover-only indication.
- Ensure critical state is communicated by icon/shape/text in addition to color.
- Avoid tiny helper text; check contrast against the actual artwork and dim layer.
- Document the interaction behavior for Continue with no save, locked route node, disabled inventory item and confirmation dialogs.

## 10. Required evidence before Figma approval

1. Main Menu, Gameplay HUD, Boss HUD, Pause, Quest Route, Inventory and Arabic Main Menu screenshots at 1920×1080.
2. A component/state sheet showing button states, focus, disabled, selected and RTL behavior.
3. A side-by-side comparison against the existing Adobe reference screens.
4. A manual visual review confirming no clipping, overlap, missing fills, text direction errors or style drift.
5. Record the exact frame/node links and reviewer decision in the ART-001 PR.

## 11. Unreal handoff — not performed by this document

After Figma approval, implement the approved structures in the canonical UE 5.7 project using UMG/CommonUI and existing source assets. Then run the project-specific capture, build/cook, automation, two-client network, input/localization/accessibility and performance gates. This specification does not satisfy those gates.
