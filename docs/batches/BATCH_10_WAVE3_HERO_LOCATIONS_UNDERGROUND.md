# CALL OF NARIS — BATCH 10 / WAVE 3
## Hero Locations & Underground Production

**Status:** ACTIVE / PRODUCTION
**Primary biome:** W04 Ashen Forest
**Purpose:** Turn the Ashen Forest vertical slice into a layered, navigable environment with memorable hero locations, underground spaces, traversal loops, secrets, combat arenas and environmental storytelling.

### Production zones

1. Ashen Forest Outer Ring — exploration and first combat readability.
2. Buried Naris Temple — vertical ruin with broken sanctum, crypt and ritual chamber.
3. Ash Gate Interior — fortified transition space with gate machinery and guardian staging area.
4. Ritual Arena — circular boss-capable combat space with destructible dressing and safe traversal lanes.
5. Whisper Lake Undercrypt — submerged/underground ruin with water channels, roots and aether glow.
6. Rootbound Tunnels — narrow traversal network with alternate routes and ambush pockets.
7. Forgotten Watchtower — vertical landmark visible from the forest and used for navigation.
8. Bone Beast Den — enemy ecosystem space with pack routes, remains and scent/tracking cues.
9. Hidden Reliquary — optional reward room gated by environmental puzzle logic.
10. Aether Fault — supernatural pocket space used for traversal, lore and VFX escalation.

### Spatial design rules

- Every hero location has a readable silhouette from at least one exterior approach.
- Main traversal always has a safe readable route; optional routes provide reward, lore or combat advantage.
- Combat arenas reserve a minimum clear combat footprint and avoid unreadable prop density.
- Underground spaces use controlled compression/expansion: narrow approach -> reveal -> encounter -> reward/shortcut.
- Landmarks provide orientation before the player reaches them.
- Secrets must be discoverable through environmental affordances rather than arbitrary invisible walls.

### Environment storytelling grammar

Use five layers: silhouette -> architecture -> prop evidence -> material evidence -> lighting/VFX evidence.

Examples:
- Broken chains + deep claw marks -> former containment site.
- Burned prayer cloth + collapsed shrine -> failed ritual.
- Bone trails + scrape marks -> active Bone Hound den.
- Aether residue + warped roots -> supernatural contamination.
- Repeated symbols near Waystones -> ancient Naris travel network.

### Encounter integration

Hero locations expose stable anchors for:
- enemy spawn volumes
- boss phase boundaries
- patrol paths
- pack routes
- ambush sockets
- loot sockets
- dialogue/lore sockets
- checkpoint/Waystone interaction
- streaming cell activation

### Performance targets

- Modular architecture follows the Batch 10 grid contract.
- Hero assets receive dedicated LOD0/LOD1/LOD2 treatment.
- Repeated dressing is instanced where the runtime supports it.
- Underground cells stream independently from the exterior where possible.
- VFX and fog remain budgeted so combat readability is never sacrificed.

### Wave 3 acceptance

- All ten locations have machine-readable layout specifications.
- Main/optional traversal loops are defined.
- Encounter anchors are spatially named and deterministic.
- Hero landmarks have unique silhouette requirements.
- Underground spaces contain lighting, collision, navigation and streaming metadata.
- No concept image is considered a final runtime asset until mesh/material/LOD/collision/engine QA passes.
