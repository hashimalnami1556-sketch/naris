# ASHEN VESSEL — Definitive Character Bible

**Project:** CALL OF NARIS  
**Asset ID:** `NARIS-CHR-ASHEN-VESSEL-0001`  
**Domain:** `CHR`  
**Status:** Design Direction Locked / Production Reference  
**Version:** V001

## 1. Core identity

Ashen Vessel is the primary heroic warrior of CALL OF NARIS. The visual read must be **noble, courageous, battle-hardened, intelligent, and protective**. He must never read as an evil, demonic, corrupted, cursed, or villainous character.

The intended archetype is **Battle-Hardened Noble / Arcane Warrior**: royal elegance combined with practical military equipment and the physical credibility of a veteran fighter.

## 2. Face and hair

- Male, youthful mature appearance.
- Strong square jaw and defined cheekbones.
- Straight, proportionate nose.
- Pale but healthy skin.
- Clean-shaven.
- Calm, focused, intelligent expression.
- Thick, long silver-white hair reaching between the shoulders and shoulder blades.
- Hair is naturally wavy and swept back from the face.
- Individual strands must remain visible in close-up renders.
- Hair uses layered silver highlights and darker silver shadow masses for depth.
- Eyes remain natural and human. No demonic glow. Any supernatural reflection is subtle and warm.

## 3. Clothing

### Crimson damask tunic

The hero wears a long open-front slit tunic in deep rust-red / crimson / coral-red. The fabric is **not plain**. It uses a premium damask/jacquard weave with repeating botanical motifs—interlocking leaves and small floral forms—rendered in a slightly darker red.

The tunic should communicate age, status, craftsmanship, and movement without becoming ornamental cosplay.

### Leather system

- Wide dark rich-brown leather waist belt, approximately 3 inches wide.
- Subtle weathering and fine edge stitching.
- Simple polished bronze buckle.
- Narrow dark-brown leather baldric crossing from right shoulder to left waist.
- Matching leather vambraces.
- Vambraces carry restrained versions of the crimson textile motif and small bronze buckles.

### Lower body

- Fitted dark charcoal/brown trousers.
- Heavy cloth or soft suede appearance.
- Tall rugged dark-brown riding boots reaching the knee or slightly above.
- Boots must look functional for rough terrain and extended travel.

## 4. Primary weapon — Flame Relic Sword

**Asset ID:** `NARIS-W10-WPN-SWD-0001`

The sword is an iconic heroic weapon and must be visibly long. It must not resemble a short sword, arming sword, dagger, or oversized fantasy slab.

### Target proportions

- Total length: approximately **150 cm**.
- Blade: approximately **115 cm**.
- Full-length blade must be clearly visible in reference renders.
- Two-handed-capable grip.
- Straight polished steel blade.
- Subtle forged Damascus texture.
- Precise central fuller.
- Refined, slightly curved engraved crossguard.
- Tightly wrapped grip.
- Prominent round decorated pommel.
- Controlled ember energy may appear along the fuller, but the weapon must never look cursed or evil.

### Weapon silhouette rule

At thumbnail scale the sword must immediately communicate **heroic legendary longsword**. The blade should contribute substantially to the character silhouette and should never visually collapse into a short one-handed weapon.

## 5. Secondary weapon

**Asset ID:** `NARIS-W10-WPN-SWD-0002`

A slender secondary sword remains in a simple leather scabbard on the left side. It is practical and visually subordinate to the Flame Relic Sword.

## 6. Color language

Primary:
- Rust Red / Crimson
- Deep Brown Leather
- Silver-White Hair
- Polished / Weathered Steel

Secondary:
- Restrained Ancient Gold / Bronze
- Warm Ember Orange
- Small Mist Cyan accents where required by NARIS visual language

Avoid dominant black-corruption palettes.

## 7. Material targets

Every production asset must preserve believable physically based material separation:

- Hair: anisotropic strand/highlight response.
- Textile: visible woven damask/jacquard relief at close range.
- Leather: grain, edge wear, controlled roughness variation.
- Steel: directional roughness and micro-scratches; polished but battle-used.
- Bronze: subtle oxidation and edge polish.

## 8. Required reference views

The definitive character sheet must contain:

1. Front full body.
2. 3/4 hero view.
3. Side profile.
4. Rear view.
5. Face/hair close-up.
6. Full-length sword profile.
7. Fabric close-up.
8. Leather/material close-up.
9. Weapon detail.
10. Neutral production turntable reference.

All views must preserve the same face, hair, costume construction, proportions, and weapon geometry.

## 9. Cinematic environment references

### Heroic / Golden Hour

A symmetrical stone causeway leads toward a towering castle between monumental mountain ranges. Two colossal eagle/griffin statues flank the route. Warm natural golden-hour light establishes grandeur and destiny.

### Dark / Otherworldly

An abandoned stone gate and ruined architecture frame a distant castle glowing with restrained blue/orange light. The scene is cold, mysterious, and tense. Mythical creature eyes may appear deep in the shadows, but they remain environmental storytelling rather than a change to the hero's personality.

## 10. Negative art direction

Never generate:

- Evil protagonist face.
- Demon/monster anatomy.
- Horns.
- Skull armor.
- Excessive spikes.
- Cursed/evil sword.
- Black corrupted armor.
- Sinister glowing eyes.
- Short primary sword.
- Dagger-like primary weapon.
- Cartoon/anime proportions.
- Generic medieval knight with no NARIS identity.

## 11. Production pipeline

Concept → Approved Concept → Asset ID → Source Art → Character Registry → High Poly → Retopo → UV → Texture → Material → Rig → Skin → Animation → Unreal Integration → Optimization → QA → Approved → Release.

The immutable Asset ID must persist across source art, registry metadata, Figma references, Adobe exports where practical, GitHub documentation, and Unreal metadata.

## 12. External tool contract

- **Higgsfield:** character concept generation and cinematic reference generation.
- **Adobe:** source art, texture studies, controlled visual production.
- **Figma:** visual reference boards, UI/UX and design-system dependencies.
- **Blender:** high-poly, retopology, UV, material authoring and technical asset preparation.
- **Unreal Engine:** skeletal mesh, materials, animation, gameplay integration, Niagara and runtime.
- **GitHub:** canonical versioned specifications, metadata, automation and review history.
- **MCP:** controlled orchestration, validation and evidence-backed project status.

## 13. Definition of Done

Ashen Vessel is not release-ready until the character identity is stable across all required views, the sword proportions are validated, the material language is preserved, the asset has its immutable ID, and the Unreal integration/QA gates have evidence.
