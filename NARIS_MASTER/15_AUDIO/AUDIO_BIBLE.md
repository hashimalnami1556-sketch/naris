# NARIS Audio Bible v2.1

## Audio identity
NARIS uses one coherent leitmotif system across exploration, combat, bosses, cinematics and UI.

### Leitmotifs
- **NARIS:** four-note core motif; incomplete early, fully stated near the finale.
- **Ashen Vessel:** low cello / burned-metal resonance variation.
- **Celestial Wolf:** glassy strings, air and spectral resonance.
- **Corruption:** distorted tritone treatment and unstable low pulse.
- **Ancient Power:** French horn + ancient bell.

## Music state machine
`EXPLORE → SUSPICION → COMBAT → COMBAT_CRITICAL → BOSS_INTRO → BOSS_PHASE_1 → BOSS_PHASE_2 → BOSS_PHASE_3 → VICTORY`

Transitions should be beat/bar aligned where possible. Hard cuts are reserved for authored cinematic impacts.

## OST production slate
| Cue | BPM | Target | Purpose |
|---|---:|---:|---|
| The Gate Remembers | 72 | 0:20 | Teaser / logo reveal |
| Call of Naris | 76 | 3:20 | Main theme |
| Beneath the Ash | 58 | 4:00 | Ashen Forest exploration |
| First Blood | 118 | 2:30 | Adaptive combat |
| Celestial Echo | 68 | 2:10 | Celestial Wolf |
| Bone Beast | 132 | 3:40 | Three-phase boss |
| Fallen Warden | 104 | 4:00 | Royal tragedy boss |
| Mother of the Veil | 64→128 | 4:20 | Corruption boss |
| The Last Dragon | 138 | 4:30 | Large-scale battle |
| Naris Awakens | 82→146 | 5:00 | Finale |
| Forgotten Memory | 54 | 2:40 | Lore / sorrow |
| Beyond the Gate | 70 | 4:00 | Credits |

## Bone Beast
Required music events:
`Intro / P1_Loop / P1toP2 / P2_Loop / P2toP3 / P3_Loop / Execution / Victory`.

Breakable armor events require distinct SFX for shoulder armor, jaw plates, back spikes and chest cage. Corrupted Core uses a low pulse that intensifies with encounter state.

## Celestial Wolf
Required SFX: Summon, Dismiss, AstralDash, SoulVision, EchoLink, CelestialRoar and 6 ethereal footstep variations.
Design = organic wolf source + spectral resonance + restrained reverse tail.

## Player
Movement: Walk, Run, Sprint, Dodge, Land_Light, Land_Heavy.
Combat: Sword_Light, Sword_Heavy, Sword_Charge, Parry, Perfect_Parry, Block, Critical, Execution.
Naris: Flame_Ignite, Flame_Loop, Flame_Burst, Rune_Charge, Rune_Release.
Use 3–6 variations for frequent events.

## Ashen Forest soundscape
Layered ambience: Wind Bed + Ash Particles + Distant Wildlife + Ruin Resonance + Naris Energy + Regional One-shots.
Snapshots: FOREST_ENTRANCE, BROKEN_SHRINE, WHISPER_LAKE, ASH_GATE, BONE_BEAST_ARENA.

## Bus architecture
`Master / Music / SFX / UI / Voice / Ambience`
Dialogue may duck Music/Ambience. Boss states may duck Ambience. Parry, perfect dodge and telegraphs remain intelligible.

## Trailer master
Separate stems: MUS_TheGateRemembers, AMB_AshWind, SFX_Gate_StoneGrind, SFX_Gate_MagicHum, SFX_Sword_Resonance, SFX_Ember_Crackle, SFX_Wolf_GhostBreath, SFX_Dragon_WingPass, SFX_Dragon_DistantRoar, SFX_Logo_FinalImpact.

## Naming
`MUS_BOSS_BoneBeast_P2_Loop_v01.wav`
`SFX_WPN_Sword_Heavy_03.wav`
`AMB_AshenForest_BrokenShrine_Loop_v01.wav`

## Definition of done
Source asset → import settings → runtime event → bus routing → loop/transition validation → QA.
Generated placeholders are never final production audio without listening review and provenance/license metadata.

See `AUDIO_EVENT_MAP.json` and `AUDIO_PRODUCTION_CHECKLIST.md`.
