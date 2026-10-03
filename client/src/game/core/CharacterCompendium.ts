/**
 * Character Compendium — نسخة جرد الشخصيات
 * From CALL_OF_NARIS_World_Character_Compendium_v1.docx
 * Defines all NPCs, bosses, and rivals with gameplay specs
 */

export enum CharacterRole {
  PROTAGONIST = 'protagonist',
  ALLY = 'ally',
  NPC = 'npc',
  RIVAL = 'rival',
  BOSS = 'boss',
  VENDOR = 'vendor',
  SPIRIT = 'spirit',
}

export enum CharacterZone {
  W04_ASHEN_FOREST = 'W04_ashen_forest',
  W05_ASHEN_WASTES = 'W05_ashen_wastes',
  BOTH = 'both_zones',
}

export interface CharacterStats {
  health: number;
  maxHealth: number;
  energy?: number;
  maxEnergy?: number;
  attackDamage?: number;
  armor?: number;
  level?: number;
}

export interface CharacterSpec {
  id: string;
  name: string;
  role: CharacterRole;
  zones: CharacterZone[];
  stats: CharacterStats;
  design: {
    silhouette: string;
    colors: string[];
    equipment?: string[];
    distinguishingFeatures: string[];
  };
  personality: {
    archetype: string;
    traits: string[];
    speakingStyle: string;
  };
  voicelines: string[];
  gameplayRole: string;
  meshPath?: string;
  animationPaths?: Record<string, string>;
}

// ============================================================
// 1. ASHEN VESSEL (Protagonist)
// ============================================================
export const CHARACTER_ASHEN_VESSEL: CharacterSpec = {
  id: 'char_ashen_vessel',
  name: 'Ashen Vessel',
  role: CharacterRole.PROTAGONIST,
  zones: [CharacterZone.BOTH],
  stats: {
    health: 100,
    maxHealth: 100,
    energy: 100,
    maxEnergy: 100,
    level: 1,
  },
  design: {
    silhouette: 'Humanoid, slight, moves with conserved motion',
    colors: ['#2A2621', '#504A44', '#FF5F14', '#00BFFF'],
    distinguishingFeatures: [
      'Left eye: permanent amber/ember glow (hunger inheritance)',
      'Right eye: cyan aether, visible only on blink (memory inheritance, always half-second too late)',
      'No visible armor or equipment — bare hand, arriving with nothing',
      'Grief-worn bearing, moves like someone conserving strength',
    ],
  },
  personality: {
    archetype: 'The Cipher / The Fractured One',
    traits: [
      'Economical with words',
      'Watches more than speaks',
      'Grieving but armored',
      'Conserves strength for something larger than immediate conflict',
    ],
    speakingStyle: 'Sparse, measured, carries weight in silence',
  },
  voicelines: [
    'Not yet. Not yet.',
    'You remember too much to die quietly. Good. Neither do I.',
    '[Silent observation, eyes tracking enemy movement]',
  ],
  gameplayRole:
    'Player character. Embodies the Sundering: carrying fragments of both memory (W04) and hunger (W05). Every choice pulls toward one wound or the other.',
  meshPath: 'assets/characters/ashen_vessel_rigged.glb',
  animationPaths: {
    idle_breathing: 'Naris_Idle_Breathing',
    aether_step: 'Naris_Aether_Step',
    attack: 'combat_slash',
    dodge: 'evasive_roll',
  },
};

// ============================================================
// 2. CINDER WARDEN (W05 Gatekeeper NPC)
// ============================================================
export const CHARACTER_CINDER_WARDEN: CharacterSpec = {
  id: 'char_cinder_warden',
  name: 'The Cinder Warden',
  role: CharacterRole.NPC,
  zones: [CharacterZone.W05_ASHEN_WASTES],
  stats: {
    health: 300,
    maxHealth: 300,
    armor: 50,
  },
  design: {
    silhouette: 'Tall, impassive, metallic',
    colors: ['#2A2621', '#FF5F14'],
    equipment: [
      'Armor fused with cooled black glass',
      'Bronze-black war-mask, fixed shut',
      'No visible face',
    ],
    distinguishingFeatures: [
      'Cracks along every joint glow with faint ember',
      'Voice sounds underwater or through metal',
      'Eternal stance — neither alive nor consumed',
      'Positioned at Fortress Tower entrance (NARIS-PRP-W05-0001)',
    ],
  },
  personality: {
    archetype: 'The Cursed Guardian',
    traits: ['Weary formality', 'Speaks in warnings phrased as courtesy', 'Resigned to eternal duty'],
    speakingStyle: 'Formal, cautious, speaks as if from underwater',
  },
  voicelines: [
    'The fire does not lie to you. It simply does not care if you understand it.',
    'You will not return the way you came.',
    'The door opens. Do not ask it to open again.',
  ],
  gameplayRole:
    'W05 guide and gatekeeper. Opens the Heavy Door (NARIS-PRP-W05-0002). Provides first warning about the Lava River crossing. Optional: grants fire-resistance blessing if befriended.',
  meshPath: 'assets/characters/cinder_warden_armored.glb',
};

// ============================================================
// 3. WHISPER OF THE LAKE (W04 Lore Spirit)
// ============================================================
export const CHARACTER_WHISPER_OF_LAKE: CharacterSpec = {
  id: 'char_whisper_lake',
  name: 'Whisper of the Lake',
  role: CharacterRole.SPIRIT,
  zones: [CharacterZone.W04_ASHEN_FOREST],
  stats: {
    health: 1,
    maxHealth: 1, // Cannot be harmed — pure spirit
  },
  design: {
    silhouette: 'Shape barely visible in fog, humanoid outline woven from cyan aether threads',
    colors: ['#00BFFF', '#00E5FF', '#504A44'],
    distinguishingFeatures: [
      'No fixed face — features shift depending on viewer',
      'Composed of same cyan aether threads as Ash Gate runes',
      'Hovers over Whisper Lake surface',
      'Overlapping voices — accumulated echo',
    ],
  },
  personality: {
    archetype: 'The Chorus of the Dead',
    traits: [
      'Gentle and sorrowful',
      'Speaks in fragments and overlapping sentences',
      'Collectively conscious — many souls in one form',
      'Compassionate toward those seeking the Ash Gate',
    ],
    speakingStyle: 'Overlapping voices, trailing thoughts, soft echoes',
  },
  voicelines: [
    'We were close. We were so— we were close. Are you close?',
    'The gate remembers. Do you?',
    'We could not carry both. Perhaps you— perhaps you—',
  ],
  gameplayRole:
    'Optional lore delivery. Provides hints at the Sundering myth. May offer cyan-aligned blessing or memory recall ability. Non-hostile.',
  meshPath: 'assets/vfx/whisper_lake_spirit.glb',
};

// ============================================================
// 4. REN THE ASHWALKER (Rival / Antagonist)
// ============================================================
export const CHARACTER_REN_ASHWALKER: CharacterSpec = {
  id: 'char_ren_ashwalker',
  name: 'Ren the Ashwalker',
  role: CharacterRole.RIVAL,
  zones: [CharacterZone.BOTH],
  stats: {
    health: 120,
    maxHealth: 120,
    attackDamage: 18,
    armor: 25,
    level: 4,
  },
  design: {
    silhouette: 'Human-scale, lean, moves with predatory grace',
    colors: ['#2A2621', '#504A44', '#FF5F14', '#00BFFF'],
    equipment: [
      'Dark grey-green travel cloak',
      'Patchwork armor scavenged from both zones',
      'Obsidian Cinder-Warden-style plate on left shoulder',
      'Cyan rune-stone fragment worn as pendant',
      'Dual-wielding sword',
    ],
    distinguishingFeatures: [
      'Armor mix signals: wants both halves, belongs to neither',
      'Scarred face, hungry eyes',
      'Moves like someone running out of time',
      'Slowly less human with each encounter',
    ],
  },
  personality: {
    archetype: 'The Thwarted Chosen',
    traits: [
      'Charismatic and resentful',
      'Genuinely believes forced power-taking is mercy',
      'Intelligent, tactical thinker',
      'Desperation masked as confidence',
    ],
    speakingStyle: 'Smooth and persuasive, underlaid with bitter edge',
  },
  voicelines: [
    "They picked you. Empty-handed, memory-less you. I've bled for this. Move.",
    'We could rule both wounds together. Why do you resist?',
    "You're slow. Slower than I expected. Slower than you should be.",
  ],
  gameplayRole:
    'Recurring rival. Encountered in both zones as an escalating threat. Foreshadows final confrontation beyond the teaser. Can be defeated multiple times, returns stronger.',
  meshPath: 'assets/characters/ren_ashwalker_rival.glb',
  animationPaths: {
    idle: 'ren_idle_pacing',
    attack: 'ren_dual_slash',
    special: 'ren_shadow_step',
  },
};

// ============================================================
// 5. KESSA EMBERFORGE (Vendor NPC)
// ============================================================
export const CHARACTER_KESSA_EMBERFORGE: CharacterSpec = {
  id: 'char_kessa_emberforge',
  name: 'Kessa Emberforge',
  role: CharacterRole.VENDOR,
  zones: [CharacterZone.W05_ASHEN_WASTES],
  stats: {
    health: 60,
    maxHealth: 60,
    armor: 20,
  },
  design: {
    silhouette: 'Squat, broad-shouldered, heavily scarred',
    colors: ['#2A2621', '#FF5F14', '#504A44'],
    equipment: [
      'Leather apron reinforced with charred-stone plating',
      'Forge hammer hanging at hip',
      'Bandaged forearms, heavily scarred from smithing',
      'One mechanical eye (lens glows faint ember when appraising)',
    ],
    distinguishingFeatures: [
      'Mechanical left eye glows when examining loot',
      'Burn scars covering both forearms',
      'Practical, no-nonsense bearing',
      'Portable forge setup wherever stationed',
    ],
  },
  personality: {
    archetype: 'The Scarred Craftsperson',
    traits: [
      'Blunt and transactional',
      'Secretly protective of capable adventurers',
      'Cynical about survival odds',
      'Respect for craftsmanship above all',
    ],
    speakingStyle: 'Terse, direct, occasional dark humor',
  },
  voicelines: [
    "The last three like you never came back to sell me anything. Don't disappoint me.",
    'Ember coal or aether shard? I work both. Fewer smiths do.',
    'Quality materials. Fair prices. Live long enough to use them.',
  ],
  gameplayRole:
    'Merchant and crafter NPC. Ties world lore to item economy. Can forge/enchant items using Ember Coal (W05) or Aether Shards (W04). Reputation-based: better prices/items as player returns with loot.',
  meshPath: 'assets/characters/kessa_emberforge_vendor.glb',
};

// ============================================================
// 6. BONE BEAST (Boss)
// ============================================================
export const CHARACTER_BONE_BEAST: CharacterSpec = {
  id: 'char_bone_beast_boss',
  name: 'The Bone Beast',
  role: CharacterRole.BOSS,
  zones: [CharacterZone.W05_ASHEN_WASTES],
  stats: {
    health: 400,
    maxHealth: 400,
    attackDamage: 45,
    armor: 60,
    level: 8,
  },
  design: {
    silhouette: 'Colossal quadrupedal creature, 8m shoulder height',
    colors: ['#2A2621', '#FF5F14', '#504A44'],
    equipment: [],
    distinguishingFeatures: [
      'Skeletal frame fused with ember-heated bone',
      'Lava-cracked skin reveals glowing orange fissures',
      'Horns curve backward (similar to Demon King design)',
      'Eyes burn with pure hunger — no consciousness visible',
      'Trails ash and glowing embers with every movement',
    ],
  },
  personality: {
    archetype: 'The Hunger Given Form',
    traits: ['Pure instinct', 'No language', 'Relentless', 'Affected by arena hazards'],
    speakingStyle: 'Roars, growls, ground-shaking impacts — no language',
  },
  voicelines: [
    '[Bone-cracking roar echoing across arena]',
    '[Lava geyser erupts as Beast steps — synchronized attack pattern]',
    '[Final defiant shriek as defeated]',
  ],
  gameplayRole:
    'W05 climactic boss encounter. Inhabits Boss Arena Platform (NARIS-PRP-W05-0009). Multi-phase fight. Arena hazards (lava geysers, cracked ground) dynamically activate during combat. Defeat grants access to final gate or realm transition.',
  meshPath: 'assets/characters/bone_beast_boss.glb',
  animationPaths: {
    idle: 'bone_beast_idle_threatening',
    charge: 'bone_beast_ground_slam',
    attack: 'bone_beast_claw_swipe',
    special: 'bone_beast_fire_breath',
    defeat: 'bone_beast_collapse',
  },
};

// ============================================================
// Character Registry
// ============================================================
export const CHARACTER_REGISTRY: Record<string, CharacterSpec> = {
  [CHARACTER_ASHEN_VESSEL.id]: CHARACTER_ASHEN_VESSEL,
  [CHARACTER_CINDER_WARDEN.id]: CHARACTER_CINDER_WARDEN,
  [CHARACTER_WHISPER_OF_LAKE.id]: CHARACTER_WHISPER_OF_LAKE,
  [CHARACTER_REN_ASHWALKER.id]: CHARACTER_REN_ASHWALKER,
  [CHARACTER_KESSA_EMBERFORGE.id]: CHARACTER_KESSA_EMBERFORGE,
  [CHARACTER_BONE_BEAST.id]: CHARACTER_BONE_BEAST,
};

// ============================================================
// Sundering Mythology
// ============================================================
export const SUNDERING_LORE = {
  coreMyth: `Before the ash, before the fire, there was only Naris — not a god in the way mortals name gods, but a single unbroken light that held memory and hunger in perfect balance. The oldest carvings call it "the First Ember, the First Water" — the twin nature of all things, undivided.`,

  theBreaking: `No one agrees on what broke it. Some say a war. Some say a choice. Some say Naris broke itself, unable to bear what it remembered. What is certain is the Sundering: the light tore into two wounds upon the world.`,

  w04_origin: `Where memory pooled and could not move on, the ash grew cold and the forest of W04 rose in permanent dusk, threaded with cyan aether — grief given geography. Tagline: "The gate remembers."`,

  w05_origin: `Where hunger pooled and could not be sated, the ground cracked open and the wastes of W05 burned without consuming — need given geography. Tagline: "The wastes hunger."`,

  vesselNature: `Between the two wounds walks the Ashen Vessel: not a survivor of the Sundering, but its aftermath made flesh. Neither half remembers being whole. The left eye carries an ember that never dims — hunger's inheritance. The right eye holds nothing until it blinks, and then, for an instant, aether answers — memory's inheritance, always a half-second too late to be trusted.`,

  coreConflict: `The Vessel exists only in the tension between both halves. Every step toward remembering (W04) pulls toward dissolution into pure memory, becoming a ghost like the gate itself. Every step toward hunger (W05) pulls toward becoming a consuming thing with no self left.`,
};

// ============================================================
// Character System Utilities
// ============================================================
export class CharacterCompendium {
  static getCharacter(id: string): CharacterSpec | null {
    return CHARACTER_REGISTRY[id] || null;
  }

  static getCharactersByZone(zone: CharacterZone): CharacterSpec[] {
    return Object.values(CHARACTER_REGISTRY).filter((char) => char.zones.includes(zone) || char.zones.includes(CharacterZone.BOTH));
  }

  static getCharactersByRole(role: CharacterRole): CharacterSpec[] {
    return Object.values(CHARACTER_REGISTRY).filter((char) => char.role === role);
  }

  static getLoreContext(): string {
    return `
    THE SUNDERING — Core Mythology
    ══════════════════════════════════════════════════════════
    ${SUNDERING_LORE.coreMyth}

    THE BREAKING:
    ${SUNDERING_LORE.theBreaking}

    W04 — ASHEN FOREST (Memory / Cyan):
    ${SUNDERING_LORE.w04_origin}

    W05 — ASHEN WASTES (Hunger / Ember):
    ${SUNDERING_LORE.w05_origin}

    THE ASHEN VESSEL (You):
    ${SUNDERING_LORE.vesselNature}

    CORE CONFLICT:
    ${SUNDERING_LORE.coreConflict}
    ══════════════════════════════════════════════════════════
    `;
  }
}
