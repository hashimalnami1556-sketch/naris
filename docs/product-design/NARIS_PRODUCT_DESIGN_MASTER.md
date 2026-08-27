# NARIS — Master Product Design

## Status
Production design baseline for the NARIS project. This document unifies visual identity, UX, 3D asset production, runtime integration, and validation.

## 1. Product Direction

NARIS is a cinematic dark-fantasy 3D action experience. The product design must preserve three simultaneous goals:

- **Cinematic identity:** strong silhouettes, controlled contrast, atmospheric depth, memorable hero moments.
- **Readable gameplay:** combat state, traversal affordances, interactables, damage, stamina, health, and objectives remain legible without covering the playfield.
- **Production discipline:** every visual asset has an owner, naming contract, target platform budget, LOD policy, material policy, and validation state.

## 2. Visual System

### Core palette

- Naris Fire — primary supernatural energy/accent.
- Royal Violet — rare arcane/cosmic accent.
- Spirit Cyan — readable spirit/interaction accent.
- Ancient Gold — relics, rewards, elite status, and narrative artifacts.
- Ash / charcoal neutrals — world foundation, silhouettes, and environmental depth.

### Material language

- Weathered stone, ash, oxidized metal, scorched wood, bone, leather, cloth, spectral energy.
- Prefer layered PBR materials with restrained roughness variation and localized emissive detail.
- Avoid uniform gray surfaces; environmental storytelling must come from material age, damage, deposits, and color temperature.

## 3. Player Experience

### Primary verbs

Move, sprint, evade, attack, heavy attack, block/parry where authored, interact, use ability, inspect, and traverse.

### Camera

Third-person cinematic camera with gameplay-safe framing. Combat camera must preserve enemy silhouettes and attack telegraphs; exploration camera may widen for environmental composition.

### HUD

Persistent HUD is intentionally low-chrome. Keep health/stamina/ability information compact. Objective and interaction prompts are contextual and disappear when not needed.

### Menu hierarchy

1. Pause
2. Inventory / equipment
3. Abilities
4. Map / objective
5. Settings
6. Accessibility

All text-heavy surfaces use DOM/UI-layer components rather than being baked into the 3D scene.

## 4. Character Design Contract

Each character asset must ship with:

- hero/reference sheet
- neutral and combat silhouettes
- clean topology
- UVs and PBR material set
- skeleton/rig contract
- animation naming contract
- gameplay pivot and capsule/collision proxy
- LOD0/LOD1/LOD2 where justified
- optimized GLB/glTF runtime export

The Ashen Vessel remains the primary hero reference. Enemy families should share the world material language but have distinct silhouettes and combat readability.

## 5. Environment Design Contract

Ashen Forest and associated world spaces use modular construction:

- terrain/ground modules
- cliff and rock modules
- tree/trunk/branch modules
- ruins/architecture modules
- traversal modules
- encounter props
- narrative props
- lighting/atmosphere volumes

Every repeated prop should be designed for material reuse, instancing, and LOD. Large environments must not rely on high-resolution unique textures for every object.

## 6. 3D Asset Production Pipeline

**Reference → Concept lock → Mesh generation → Blender cleanup → UV/material → LOD/collision → GLB export → glTF optimization → runtime validation.**

Mesh generation services are treated as upstream authoring tools, not runtime dependencies. If Meshy is unavailable as a connected tool, the asset specification remains executable manually or through an equivalent generation workflow.

Shipping contract: **GLB/glTF 2.0**. FBX/OBJ/BLEND are source/interchange formats, not the long-term browser runtime contract.

## 7. Asset Naming

Use stable semantic IDs rather than filenames as gameplay APIs.

Examples:

- `CHR_Hero_AshenVessel`
- `CHR_Enemy_BoneBeast`
- `ENV_AshenForest_Rock_Cliff_A01`
- `ENV_AshenForest_Tree_Trunk_A01`
- `PROP_Relic_AncientGold_A01`
- `FX_NarisFire_Burst_A01`
- `UI_Ability_Ring_A01`

## 8. Performance Budgets

Budgets are enforced per asset class and platform rather than by visual ambition alone. Default review targets:

- minimize unique materials
- reuse texture sets where visually acceptable
- use Meshopt/Draco selectively for geometry delivery
- use KTX2/BasisU or WebP/AVIF where the runtime stack supports them
- keep collision meshes simple and explicit
- use LODs for repeated or distant geometry
- validate memory, draw calls, triangle counts, and texture residency in runtime

## 9. Product Design States

Every asset and screen progresses through:

`CONCEPT → APPROVED → PRODUCTION → INTEGRATED → VALIDATED`

No asset is considered shipped solely because it was generated. Integration and runtime validation are separate gates.

## 10. Tool Roles

### Mesh generation

Use Meshy or an equivalent 3D generation workflow for rapid concept-to-mesh iteration. Generated output must pass the NARIS cleanup, material, topology, pivot, LOD, collision, and GLB validation gates.

### Design

Use Designly/Figma/Canva-class design tooling for UX layouts, visual references, design-system documentation, and presentation artifacts. The design system must remain implementable by the game UI stack.

### Collaboration

Slack is the coordination surface for design reviews, asset handoffs, blockers, and approvals when connected. The current workspace connection did not expose a NARIS channel, so no message was fabricated or sent.

### Game Studio

Game Studio owns the runtime architecture and routes the project to the specific 3D runtime/asset/QA skills. Simulation remains separate from rendering; DOM overlays handle text-heavy HUD and menus; GLB/glTF is the default 3D shipping format.

## 11. Definition of Done

A Product Design item is complete only when:

- visual direction is consistent with NARIS identity
- gameplay readability has been reviewed
- asset naming and metadata are registered
- source and runtime formats are separated
- LOD/collision/material strategy is documented
- runtime export is validated
- UX state transitions are specified
- accessibility and responsive behavior are considered for UI
- performance risks have an explicit mitigation
- the item is linked to the relevant game-system or content registry
