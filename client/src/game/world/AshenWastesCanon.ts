/**
 * Ashen Wastes Canon (W05) — النفايات المحترقة
 * Official specifications from CALL_OF_NARIS_Production_Bible_v3.1
 * Section 22: W05 Environment & Asset Hierarchy
 */

export interface W05Asset {
  id: string;
  name: string;
  dimensions: { width: number; height: number; depth?: number; radius?: number };
  hazard: boolean;
  glowColor?: string;
  glowIntensity?: number;
  isDestructible?: boolean;
  interactable?: boolean;
}

export interface W05ColorPalette {
  emberLava: string;      // #FF5F14 — hazard/light sources ONLY
  charredStone: string;   // #2A2621 — primary architecture
  ashGrey: string;        // #504A44 — weathering/dust
}

export interface W05SpatialLayout {
  entrance: string;
  path: string[];
  bossBridge: string;
  bossArena: string;
}

// ============================================================
// Official W05 Color Palette
// ============================================================
export const W05_PALETTE: W05ColorPalette = {
  emberLava: '#FF5F14',    // RGB(255, 95, 20) — used on hazard/light props only
  charredStone: '#2A2621', // RGB(42, 38, 33) — base architecture
  ashGrey: '#504A44',      // RGB(80, 74, 68) — weathering accents
};

// ============================================================
// Official W05 Asset Inventory (Section 22)
// ============================================================
export const W05_ASSETS: Record<string, W05Asset> = {
  // Structural Landmarks
  STONE_PILLAR: {
    id: 'NARIS-PRP-W05-0000',
    name: 'Stone Pillar',
    dimensions: { radius: 0.55, height: 3.2 },
    hazard: false,
    interactable: false,
  },
  FORTRESS_TOWER: {
    id: 'NARIS-PRP-W05-0001',
    name: 'Fortress Tower',
    dimensions: { radius: 2.0, height: 9.0 },
    hazard: false,
    interactable: false,
  },
  HEAVY_DOOR: {
    id: 'NARIS-PRP-W05-0002',
    name: 'Heavy Door',
    dimensions: { width: 2.6, height: 3.6, depth: 0.5 },
    hazard: false,
    interactable: true,
  },

  // Destructibles & Interactables
  BREAKABLE_BARREL: {
    id: 'NARIS-PRP-W05-0003',
    name: 'Breakable Barrel',
    dimensions: { radius: 0.32, height: 0.9 },
    hazard: false,
    isDestructible: true,
  },
  TORCH_INTERACTABLE: {
    id: 'NARIS-PRP-W05-0004',
    name: 'Torch Interactable',
    dimensions: { width: 0.4, height: 1.6 },
    hazard: false,
    glowColor: W05_PALETTE.emberLava,
    glowIntensity: 1.0,
    interactable: true,
  },

  // Hazard Elements
  BROKEN_BRIDGE: {
    id: 'NARIS-PRP-W05-0005',
    name: 'Broken Bridge',
    dimensions: { width: 12.0, height: 2.8, depth: 2.8 },
    hazard: true,
  },
  LAVA_RIVER_CHANNEL: {
    id: 'NARIS-PRP-W05-0006',
    name: 'Lava River Channel',
    dimensions: { width: 10.0, height: 1.0, depth: 3.2 },
    hazard: true,
    glowColor: W05_PALETTE.emberLava,
    glowIntensity: 1.0,
  },
  LAVA_GEYSER: {
    id: 'NARIS-PRP-W05-0007',
    name: 'Lava Geyser',
    dimensions: { radius: 1.5, height: 2.5 },
    hazard: true,
    glowColor: W05_PALETTE.emberLava,
    glowIntensity: 1.0,
  },

  // Environmental Props
  LARGE_ROCK: {
    id: 'NARIS-PRP-W05-0008',
    name: 'Large Rock',
    dimensions: { width: 5.0, height: 5.0, depth: 5.0 },
    hazard: false,
  },
  BOSS_ARENA_PLATFORM: {
    id: 'NARIS-PRP-W05-0009',
    name: 'Boss Arena Platform',
    dimensions: { radius: 9.0, height: 1.2 },
    hazard: false,
    glowColor: W05_PALETTE.emberLava,
    glowIntensity: 0.6,
  },
};

// ============================================================
// W05 Spatial Layout
// ============================================================
export const W05_LAYOUT: W05SpatialLayout = {
  entrance: 'Stone Pillar + Fortress Tower',
  path: [
    'Heavy Door entrance',
    'Torch-flanked crossing',
    'Rocks scattered along path',
    'Broken Bridge / Lava River crossing',
    'Lava Geyser Field',
  ],
  bossBridge: 'Broken Bridge',
  bossArena: 'Boss Arena Platform (⌀18m with 6 rim spikes)',
};

// ============================================================
// W05 Environmental Rules
// ============================================================
export const W05_RULES = {
  SKY: 'Permanent smoke-choked dusk: deep ember-red haze, heavy ash particulate, no stars',
  GROUND: 'All surfaces charred black, cracked, with glowing fissures at hazard points ONLY',
  GROUND_HAZE: 'Dense black-grey ash smoke, warm underglow limited to lava-adjacent areas',
  COLOR_RULE: 'Ember/lava orange (#FF5F14) ONLY on functional hazard & light-source props — NEVER on ambient architecture',
  AETHER_PROHIBITION: 'Cyan aether is explicitly ABSENT from W05 (reserved exclusively for W04)',
} as const;

// ============================================================
// Boss Arena Configuration
// ============================================================
export interface BossArenaConfig {
  platformRadius: number;
  rimSpikes: number;
  arenaCenter: { x: number; y: number; z: number };
  hazardZones: Array<{
    type: 'lava_geyser' | 'cracked_ground' | 'ash_storm';
    position: { x: number; y: number; z: number };
    radius: number;
    damagePerSecond: number;
  }>;
}

export const BOSS_ARENA: BossArenaConfig = {
  platformRadius: 9.0,
  rimSpikes: 6,
  arenaCenter: { x: 0, y: 0, z: 0 },
  hazardZones: [
    {
      type: 'lava_geyser',
      position: { x: 0, y: 0, z: 0 },
      radius: 3.0,
      damagePerSecond: 25,
    },
  ],
};

// ============================================================
// Ashen Vessel Specifications (Player Character)
// ============================================================
export interface AshenVesselSpec {
  maxHealth: number;
  maxEnergy: number;
  eyeLeft: {
    color: string;
    meaning: string;
    state: 'always_on';
  };
  eyeRight: {
    color: string;
    meaning: string;
    state: 'on_blink';
  };
  baseMovementSpeed: number;
  coreConflict: string;
}

export const ASHEN_VESSEL_SPECS: AshenVesselSpec = {
  maxHealth: 100,
  maxEnergy: 100,
  eyeLeft: {
    color: '#FF5F14', // Ember — Hunger's inheritance
    meaning: 'Hunger (W05 nature)',
    state: 'always_on',
  },
  eyeRight: {
    color: '#00BFFF', // Cyan — Memory's inheritance, half-second too late
    meaning: 'Memory (W04 nature)',
    state: 'on_blink',
  },
  baseMovementSpeed: 5.5,
  coreConflict:
    'Every step toward memory (W04) risks dissolution into pure memory. Every step toward hunger (W05) risks becoming a consuming void. The Vessel exists only in the tension between both.',
};

// ============================================================
// Quality Tier
// ============================================================
export const W05_QUALITY_TIER = 'block-out (procedural geometry + vertex color)' as const;
export const W05_TEXTURE_SUPPORT = 'No PBR textures, no rigging, no VFX yet' as const;
