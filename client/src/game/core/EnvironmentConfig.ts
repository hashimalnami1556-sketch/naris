/**
 * Environment Configuration - إعدادات البيئات
 * تعريف وتكوين العوالم والمستويات والبيئات المختلفة
 */

export interface EnvironmentAsset {
  id: string;
  name: string;
  path: string;
  type: 'mesh' | 'material' | 'texture' | 'skybox' | 'cinematic';
  category: string;
}

export interface EnvironmentSpawnPoint {
  id: string;
  position: { x: number; y: number; z: number };
  direction: { x: number; y: number; z: number };
  characterType?: string;
}

export interface EnvironmentZone {
  id: string;
  name: string;
  position: { x: number; y: number; z: number };
  radius: number;
  type: 'combat' | 'safe' | 'boss_arena' | 'puzzle' | 'treasure';
  musicIntensity: 'calm' | 'exploration' | 'combat' | 'boss';
  ambience: string;
}

export interface EnvironmentLighting {
  ambientColor: { r: number; g: number; b: number };
  sunColor: { r: number; g: number; b: number };
  sunDirection: { x: number; y: number; z: number };
  fogColor: { r: number; g: number; b: number };
  fogDensity: number;
  fogStart: number;
  fogEnd: number;
}

export interface EnvironmentData {
  id: string;
  name: string;
  displayName: string;
  type: 'realm' | 'dungeon' | 'boss_arena' | 'hub';
  assets: EnvironmentAsset[];
  spawnPoints: EnvironmentSpawnPoint[];
  zones: EnvironmentZone[];
  lighting: EnvironmentLighting;
  weather?: {
    type: string;
    intensity: number;
  };
  cinematicCameras: string[];
  navMeshPath?: string;
  musicTrack: string;
  description: string;
}

// ═══════════════════════════════════════════════════════════════
// ASHEN FOREST ENVIRONMENT - بيئة غابة الرماد
// ═══════════════════════════════════════════════════════════════

export const ASHEN_FOREST_ENVIRONMENT: EnvironmentData = {
  id: 'ashen_forest',
  name: 'AshenForest',
  displayName: 'Ashen Forest - غابة الرماد',
  type: 'realm',

  // المواد والعناصر
  assets: [
    // Skeletal Meshes
    {
      id: 'mesh_player',
      name: 'Player Character',
      path: 'assets/characters/player/skeletal_meshes',
      type: 'mesh',
      category: 'characters/player',
    },
    {
      id: 'mesh_bone_beast',
      name: 'Bone Beast Enemy',
      path: 'assets/characters/enemies/bone_beast',
      type: 'mesh',
      category: 'characters/enemies',
    },
    {
      id: 'mesh_aether_beast',
      name: 'Aether Beast Enemy',
      path: 'assets/characters/enemies/aether_beast',
      type: 'mesh',
      category: 'characters/enemies',
    },
    {
      id: 'mesh_root_wraith',
      name: 'Root Wraith Enemy',
      path: 'assets/characters/enemies/root_wraith',
      type: 'mesh',
      category: 'characters/enemies',
    },
    {
      id: 'mesh_goblin',
      name: 'Goblin Enemy',
      path: 'assets/characters/enemies/goblin',
      type: 'mesh',
      category: 'characters/enemies',
    },

    // Static Meshes - Entry Area
    {
      id: 'mesh_entry_gate',
      name: 'Entrance Gate',
      path: 'assets/environment/ashen_forest/00_entry/gate',
      type: 'mesh',
      category: 'static/entry',
    },
    {
      id: 'mesh_entry_bridge',
      name: 'Entry Bridge',
      path: 'assets/environment/ashen_forest/00_entry/bridge',
      type: 'mesh',
      category: 'static/entry',
    },

    // Static Meshes - Ruined Path
    {
      id: 'mesh_ruined_path',
      name: 'Ruined Path',
      path: 'assets/environment/ashen_forest/01_ruined_path/path',
      type: 'mesh',
      category: 'static/path',
    },
    {
      id: 'mesh_dead_trees',
      name: 'Dead Trees',
      path: 'assets/environment/ashen_forest/01_ruined_path/trees',
      type: 'mesh',
      category: 'static/vegetation',
    },
    {
      id: 'mesh_fallen_logs',
      name: 'Fallen Logs',
      path: 'assets/environment/ashen_forest/01_ruined_path/logs',
      type: 'mesh',
      category: 'static/vegetation',
    },

    // Static Meshes - Root Tunnel
    {
      id: 'mesh_root_tunnel_entrance',
      name: 'Root Tunnel Entrance',
      path: 'assets/environment/ashen_forest/02_root_tunnel/entrance',
      type: 'mesh',
      category: 'static/tunnel',
    },
    {
      id: 'mesh_root_tunnel_passage',
      name: 'Root Tunnel Passage',
      path: 'assets/environment/ashen_forest/02_root_tunnel/passage',
      type: 'mesh',
      category: 'static/tunnel',
    },
    {
      id: 'mesh_root_tunnel_vines',
      name: 'Root Tunnel Vines',
      path: 'assets/environment/ashen_forest/02_root_tunnel/vines',
      type: 'mesh',
      category: 'static/tunnel',
    },

    // Static Meshes - Whisper Clearing
    {
      id: 'mesh_clearing_ground',
      name: 'Clearing Ground',
      path: 'assets/environment/ashen_forest/03_whisper_clearing/ground',
      type: 'mesh',
      category: 'static/clearing',
    },
    {
      id: 'mesh_clearing_stones',
      name: 'Clearing Stones',
      path: 'assets/environment/ashen_forest/03_whisper_clearing/stones',
      type: 'mesh',
      category: 'static/clearing',
    },

    // Static Meshes - Aether Shrine
    {
      id: 'mesh_aether_shrine',
      name: 'Aether Shrine',
      path: 'assets/environment/ashen_forest/04_aether_shrine/shrine',
      type: 'mesh',
      category: 'static/shrine',
    },
    {
      id: 'mesh_shrine_pillars',
      name: 'Shrine Pillars',
      path: 'assets/environment/ashen_forest/04_aether_shrine/pillars',
      type: 'mesh',
      category: 'static/shrine',
    },

    // Static Meshes - Bone Crypt
    {
      id: 'mesh_bone_crypt_entrance',
      name: 'Bone Crypt Entrance',
      path: 'assets/environment/ashen_forest/05_bone_crypt/entrance',
      type: 'mesh',
      category: 'static/crypt',
    },
    {
      id: 'mesh_bone_crypt_chamber',
      name: 'Bone Crypt Chamber',
      path: 'assets/environment/ashen_forest/05_bone_crypt/chamber',
      type: 'mesh',
      category: 'static/crypt',
    },
    {
      id: 'mesh_bone_crypt_sarcophagus',
      name: 'Bone Crypt Sarcophagus',
      path: 'assets/environment/ashen_forest/05_bone_crypt/sarcophagus',
      type: 'mesh',
      category: 'static/crypt',
    },

    // Static Meshes - Boss Arena
    {
      id: 'mesh_beast_arena_ground',
      name: 'Beast Arena Ground',
      path: 'assets/environment/ashen_forest/06_bone_beast_arena/ground',
      type: 'mesh',
      category: 'static/arena',
    },
    {
      id: 'mesh_beast_arena_walls',
      name: 'Beast Arena Walls',
      path: 'assets/environment/ashen_forest/06_bone_beast_arena/walls',
      type: 'mesh',
      category: 'static/arena',
    },

    // Materials
    {
      id: 'mat_ancient_stone',
      name: 'Ancient Stone Material',
      path: 'assets/materials/ancient_stone',
      type: 'material',
      category: 'materials/stone',
    },
    {
      id: 'mat_bone_white',
      name: 'Bone White Material',
      path: 'assets/materials/bone_white',
      type: 'material',
      category: 'materials/bone',
    },
    {
      id: 'mat_aether_glow',
      name: 'Aether Glow Material',
      path: 'assets/materials/aether_glow',
      type: 'material',
      category: 'materials/aether',
    },
    {
      id: 'mat_ash_ground',
      name: 'Ash Ground Material',
      path: 'assets/materials/ash_ground',
      type: 'material',
      category: 'materials/ground',
    },

    // Skybox
    {
      id: 'skybox_ashen_forest',
      name: 'Ashen Forest Skybox',
      path: 'assets/environment/ashen_forest/skybox',
      type: 'skybox',
      category: 'environment/skybox',
    },

    // VFX
    {
      id: 'vfx_ember_ash',
      name: 'Ember Ash VFX',
      path: 'assets/vfx/ember_ash',
      type: 'mesh',
      category: 'vfx/particles',
    },
    {
      id: 'vfx_aether_veins',
      name: 'Aether Veins VFX',
      path: 'assets/vfx/aether_veins',
      type: 'mesh',
      category: 'vfx/particles',
    },
  ],

  // نقاط بدء الشخصيات
  spawnPoints: [
    {
      id: 'spawn_player_entry',
      position: { x: -50, y: 5, z: 0 },
      direction: { x: 1, y: 0, z: 0 },
      characterType: 'player',
    },
    {
      id: 'spawn_player_checkpoint_1',
      position: { x: 20, y: 10, z: 50 },
      direction: { x: 1, y: 0, z: 1 },
      characterType: 'player',
    },
    {
      id: 'spawn_player_checkpoint_2',
      position: { x: 80, y: 15, z: 100 },
      direction: { x: 1, y: 0, z: 1 },
      characterType: 'player',
    },

    {
      id: 'spawn_goblin_patrol_1',
      position: { x: 10, y: 5, z: 30 },
      direction: { x: -1, y: 0, z: 0 },
      characterType: 'goblin',
    },
    {
      id: 'spawn_bone_beast_patrol',
      position: { x: 40, y: 10, z: 60 },
      direction: { x: -1, y: 0, z: -1 },
      characterType: 'bone_beast',
    },
    {
      id: 'spawn_root_wraith_patrol',
      position: { x: 50, y: 8, z: 80 },
      direction: { x: 0, y: 0, z: 1 },
      characterType: 'root_wraith',
    },
    {
      id: 'spawn_aether_beast_boss',
      position: { x: 100, y: 20, z: 150 },
      direction: { x: -1, y: 0, z: -1 },
      characterType: 'aether_beast',
    },
  ],

  // مناطق البيئة
  zones: [
    {
      id: 'zone_entry_gateway',
      name: 'Entry Gateway',
      position: { x: -30, y: 5, z: 0 },
      radius: 40,
      type: 'safe',
      musicIntensity: 'calm',
      ambience: 'wind_forest',
    },
    {
      id: 'zone_ruined_path',
      name: 'Ruined Path',
      position: { x: 15, y: 8, z: 40 },
      radius: 50,
      type: 'safe',
      musicIntensity: 'exploration',
      ambience: 'forest_ambient',
    },
    {
      id: 'zone_root_tunnel',
      name: 'Root Tunnel',
      position: { x: 50, y: 12, z: 80 },
      radius: 45,
      type: 'combat',
      musicIntensity: 'combat',
      ambience: 'tunnel_dripping',
    },
    {
      id: 'zone_whisper_clearing',
      name: 'Whisper Clearing',
      position: { x: 70, y: 10, z: 60 },
      radius: 35,
      type: 'puzzle',
      musicIntensity: 'exploration',
      ambience: 'whisper_ambient',
    },
    {
      id: 'zone_aether_shrine',
      name: 'Aether Shrine',
      position: { x: 85, y: 15, z: 95 },
      radius: 40,
      type: 'safe',
      musicIntensity: 'calm',
      ambience: 'aether_resonance',
    },
    {
      id: 'zone_bone_crypt',
      name: 'Bone Crypt',
      position: { x: 120, y: 18, z: 120 },
      radius: 50,
      type: 'combat',
      musicIntensity: 'combat',
      ambience: 'crypt_echo',
    },
    {
      id: 'zone_beast_arena',
      name: 'Bone Beast Arena',
      position: { x: 150, y: 20, z: 160 },
      radius: 60,
      type: 'boss_arena',
      musicIntensity: 'boss',
      ambience: 'boss_ambient',
    },
  ],

  // الإضاءة
  lighting: {
    ambientColor: { r: 0.4, g: 0.35, b: 0.3 },
    sunColor: { r: 1.0, g: 0.8, b: 0.6 },
    sunDirection: { x: 1, y: 1, z: 0.5 },
    fogColor: { r: 0.3, g: 0.25, b: 0.2 },
    fogDensity: 0.05,
    fogStart: 50,
    fogEnd: 300,
  },

  // الطقس
  weather: {
    type: 'ash_fall',
    intensity: 0.6,
  },

  // كاميرات سينمائية
  cinematicCameras: [
    'cinematic_entry_22',
    'cinematic_boss_reveal',
    'cinematic_victory',
  ],

  // مسار الخريطة
  navMeshPath: 'assets/environment/ashen_forest/navmesh',

  // مسار الموسيقى
  musicTrack: 'music_ashen_forest_exploration',

  // الوصف
  description:
    'The Ashen Forest - غابة الرماد - A desolate realm consumed by ancient magic and death. The ground is covered in volcanic ash, skeletal remains litter the path, and the air crackles with ethereal energy. The Bone Beast lurks in the deepest parts, guarding secrets of the fallen realm.',
};

// ═══════════════════════════════════════════════════════════════
// ENVIRONMENT REGISTRY - سجل البيئات
// ═══════════════════════════════════════════════════════════════

export const ENVIRONMENT_REGISTRY: Record<string, EnvironmentData> = {
  [ASHEN_FOREST_ENVIRONMENT.id]: ASHEN_FOREST_ENVIRONMENT,
};

export function getEnvironment(environmentId: string): EnvironmentData | undefined {
  return ENVIRONMENT_REGISTRY[environmentId];
}

export function getAllEnvironments(): EnvironmentData[] {
  return Object.values(ENVIRONMENT_REGISTRY);
}

export function getEnvironmentAssets(
  environmentId: string,
  category?: string
): EnvironmentAsset[] {
  const env = getEnvironment(environmentId);
  if (!env) return [];

  if (category) {
    return env.assets.filter((asset) => asset.category === category);
  }
  return env.assets;
}

export function getEnvironmentZones(
  environmentId: string,
  type?: string
): EnvironmentZone[] {
  const env = getEnvironment(environmentId);
  if (!env) return [];

  if (type) {
    return env.zones.filter((zone) => zone.type === type);
  }
  return env.zones;
}
