/**
 * W05 Ashen Wastes — Environment Configuration
 * Based on official canon: CALL_OF_NARIS_Production_Bible_v3.1 § Section 22
 * Replaces generic EnvironmentConfig.ts with canon-compliant W05 setup
 */

import * as BABYLON from 'babylonjs';
import { W05_ASSETS, W05_PALETTE } from './AshenWastesCanon';
import { gameEvents } from '../core/EventSystem';

export interface W05ZoneData {
  id: string;
  name: string;
  position: { x: number; y: number; z: number };
  radius: number;
  musicIntensity: 'calm' | 'exploration' | 'combat' | 'boss';
  ambience: string;
  hazards: string[];
  assets: string[]; // Asset IDs from W05_ASSETS
}

export interface W05LightingConfig {
  ambientColor: BABYLON.Color3;
  ambientIntensity: number;
  sunDirection: BABYLON.Vector3;
  sunIntensity: number;
  fogDensity: number;
  fogStart: number;
  fogEnd: number;
  fogColor: BABYLON.Color3;
}

// ============================================================
// W05 LIGHTING — Official Specifications
// ============================================================
export const W05_LIGHTING: W05LightingConfig = {
  // Deep ember-red haze with heavy ash particulate
  ambientColor: new BABYLON.Color3(0.4, 0.35, 0.3), // Warm dust tone
  ambientIntensity: 0.6,

  // Sun: muted, filtered through ash
  sunDirection: new BABYLON.Vector3(-0.2, -0.7, 0.3), // Low, angled, through smoke
  sunIntensity: 0.5,

  // Dense ash fog from ground up
  fogDensity: 0.05,
  fogStart: 50,
  fogEnd: 300,
  fogColor: new BABYLON.Color3(0.15, 0.12, 0.1), // Black-grey ash smoke
};

// ============================================================
// W05 ZONES — Spatial Organization
// ============================================================
export const W05_ZONES: Record<string, W05ZoneData> = {
  FORTRESS_ENTRANCE: {
    id: 'zone_fortress_entrance',
    name: 'Fortress Entrance - Stone Pillar & Tower',
    position: { x: 0, y: 0, z: 0 },
    radius: 25,
    musicIntensity: 'calm',
    ambience: 'distant_wind_howl',
    hazards: [],
    assets: ['STONE_PILLAR', 'FORTRESS_TOWER'],
  },

  HEAVY_DOOR_CROSSING: {
    id: 'zone_heavy_door',
    name: 'Heavy Door Checkpoint',
    position: { x: 30, y: 0, z: 0 },
    radius: 20,
    musicIntensity: 'exploration',
    ambience: 'metal_creaking',
    hazards: [],
    assets: ['HEAVY_DOOR', 'TORCH_INTERACTABLE'],
  },

  TORCH_FLANKED_PATH: {
    id: 'zone_torch_path',
    name: 'Torch-Flanked Crossing',
    position: { x: 60, y: 0, z: 0 },
    radius: 30,
    musicIntensity: 'exploration',
    ambience: 'torch_crackling',
    hazards: [],
    assets: ['TORCH_INTERACTABLE', 'LARGE_ROCK', 'TORCH_INTERACTABLE'],
  },

  LAVA_RIVER_CROSSING: {
    id: 'zone_lava_river',
    name: 'Lava River Crossing - Broken Bridge',
    position: { x: 90, y: 0, z: 5 },
    radius: 40,
    musicIntensity: 'combat',
    ambience: 'lava_bubbling_intense',
    hazards: ['LAVA_RIVER_CHANNEL', 'BROKEN_BRIDGE'],
    assets: ['BROKEN_BRIDGE', 'LAVA_RIVER_CHANNEL', 'LARGE_ROCK', 'TORCH_INTERACTABLE'],
  },

  GEYSER_FIELD: {
    id: 'zone_geyser_field',
    name: 'Lava Geyser Field - Hazard Zone',
    position: { x: 130, y: 0, z: 8 },
    radius: 50,
    musicIntensity: 'combat',
    ambience: 'geysers_erupting',
    hazards: ['LAVA_GEYSER', 'LAVA_GEYSER', 'LAVA_GEYSER'],
    assets: ['LAVA_GEYSER', 'LAVA_GEYSER', 'LAVA_GEYSER', 'LARGE_ROCK'],
  },

  BOSS_ARENA_ZONE: {
    id: 'zone_boss_arena',
    name: 'Boss Arena Platform - Bone Beast Lair',
    position: { x: 180, y: 0, z: 10 },
    radius: 60,
    musicIntensity: 'boss',
    ambience: 'bone_beast_breathing',
    hazards: ['LAVA_GEYSER', 'CRACKED_GROUND'],
    assets: ['BOSS_ARENA_PLATFORM', 'LAVA_GEYSER'],
  },
};

// ============================================================
// W05 Spawn Points — Character Placement
// ============================================================
export interface SpawnPoint {
  id: string;
  characterType: 'player' | 'npc' | 'enemy' | 'boss';
  position: BABYLON.Vector3;
  zone: string;
}

export const W05_SPAWN_POINTS: SpawnPoint[] = [
  // Player checkpoints
  {
    id: 'spawn_checkpoint_1_fortress_entrance',
    characterType: 'player',
    position: new BABYLON.Vector3(5, 2, 0),
    zone: 'zone_fortress_entrance',
  },
  {
    id: 'spawn_checkpoint_2_after_bridge',
    characterType: 'player',
    position: new BABYLON.Vector3(100, 2, 5),
    zone: 'zone_lava_river',
  },
  {
    id: 'spawn_checkpoint_3_boss_arena_entrance',
    characterType: 'player',
    position: new BABYLON.Vector3(175, 2, 10),
    zone: 'zone_boss_arena',
  },

  // NPC placements
  {
    id: 'spawn_cinder_warden',
    characterType: 'npc',
    position: new BABYLON.Vector3(32, 1, 0),
    zone: 'zone_heavy_door',
  },
  {
    id: 'spawn_kessa_emberforge',
    characterType: 'npc',
    position: new BABYLON.Vector3(140, 1, 8),
    zone: 'zone_geyser_field',
  },

  // Enemy patrol spawn points
  {
    id: 'spawn_ren_encounter_1',
    characterType: 'enemy',
    position: new BABYLON.Vector3(50, 1, 0),
    zone: 'zone_torch_path',
  },
  {
    id: 'spawn_ren_encounter_2',
    characterType: 'enemy',
    position: new BABYLON.Vector3(95, 1, 5),
    zone: 'zone_lava_river',
  },

  // Boss spawn
  {
    id: 'spawn_bone_beast_arena',
    characterType: 'boss',
    position: new BABYLON.Vector3(180, 3, 10),
    zone: 'zone_boss_arena',
  },
];

// ============================================================
// W05 Cinematic Camera Presets
// ============================================================
export interface CinematicCameraPreset {
  name: string;
  position: BABYLON.Vector3;
  target: BABYLON.Vector3;
  fov: number;
  usage: string;
}

export const W05_CINEMATIC_CAMERAS: CinematicCameraPreset[] = [
  {
    name: 'Fortress_Approach',
    position: new BABYLON.Vector3(-20, 15, -30),
    target: new BABYLON.Vector3(0, 5, 0),
    fov: 60,
    usage: 'Opening cinematic — player approaches Fortress Tower from distance',
  },
  {
    name: 'Bridge_Hazard_Reveal',
    position: new BABYLON.Vector3(85, 20, -40),
    target: new BABYLON.Vector3(95, 2, 5),
    fov: 50,
    usage: 'Player discovers Lava River crossing — dramatic reveal of hazard',
  },
  {
    name: 'Boss_Arena_Entrance',
    position: new BABYLON.Vector3(160, 25, -50),
    target: new BABYLON.Vector3(180, 3, 10),
    fov: 55,
    usage: 'Boss encounter intro — camera pulls back to reveal full arena',
  },
];

// ============================================================
// W05 Asset Placement by Zone
// ============================================================
export interface AssetPlacement {
  assetId: string;
  zone: string;
  position: BABYLON.Vector3;
  rotation?: BABYLON.Vector3;
  scale?: number;
}

export const W05_ASSET_PLACEMENTS: AssetPlacement[] = [
  // Fortress Entrance
  {
    assetId: 'STONE_PILLAR',
    zone: 'zone_fortress_entrance',
    position: new BABYLON.Vector3(-8, 0, 0),
    scale: 1,
  },
  {
    assetId: 'FORTRESS_TOWER',
    zone: 'zone_fortress_entrance',
    position: new BABYLON.Vector3(8, 0, 0),
    scale: 1,
  },

  // Heavy Door
  {
    assetId: 'HEAVY_DOOR',
    zone: 'zone_heavy_door',
    position: new BABYLON.Vector3(30, 0, 0),
    rotation: new BABYLON.Vector3(0, 0, 0),
  },

  // Torch-Flanked Path
  {
    assetId: 'TORCH_INTERACTABLE',
    zone: 'zone_torch_path',
    position: new BABYLON.Vector3(55, 0, -5),
  },
  {
    assetId: 'TORCH_INTERACTABLE',
    zone: 'zone_torch_path',
    position: new BABYLON.Vector3(65, 0, 5),
  },
  {
    assetId: 'LARGE_ROCK',
    zone: 'zone_torch_path',
    position: new BABYLON.Vector3(60, 0, 0),
    scale: 1.2,
  },

  // Lava River Crossing
  {
    assetId: 'BROKEN_BRIDGE',
    zone: 'zone_lava_river',
    position: new BABYLON.Vector3(90, 1, 0),
  },
  {
    assetId: 'LAVA_RIVER_CHANNEL',
    zone: 'zone_lava_river',
    position: new BABYLON.Vector3(90, 0, 3),
  },

  // Geyser Field
  {
    assetId: 'LAVA_GEYSER',
    zone: 'zone_geyser_field',
    position: new BABYLON.Vector3(115, 0, 0),
  },
  {
    assetId: 'LAVA_GEYSER',
    zone: 'zone_geyser_field',
    position: new BABYLON.Vector3(135, 0, -10),
  },
  {
    assetId: 'LAVA_GEYSER',
    zone: 'zone_geyser_field',
    position: new BABYLON.Vector3(145, 0, 15),
  },

  // Boss Arena
  {
    assetId: 'BOSS_ARENA_PLATFORM',
    zone: 'zone_boss_arena',
    position: new BABYLON.Vector3(180, 0, 10),
    scale: 1,
  },
];

// ============================================================
// W05 Environment Manager
// ============================================================
export class W05EnvironmentManager {
  private static instance: W05EnvironmentManager;
  private scene: BABYLON.Scene;
  private loadedAssets: Map<string, BABYLON.AbstractMesh> = new Map();
  private activeZones: Set<string> = new Set();

  private constructor(scene: BABYLON.Scene) {
    this.scene = scene;
  }

  static getInstance(scene?: BABYLON.Scene): W05EnvironmentManager {
    if (!W05EnvironmentManager.instance && scene) {
      W05EnvironmentManager.instance = new W05EnvironmentManager(scene);
    }
    return W05EnvironmentManager.instance;
  }

  /**
   * Apply W05 environment lighting
   */
  applyLighting(): void {
    // Ambient light
    const ambient = new BABYLON.HemisphericLight('w05_ambient', new BABYLON.Vector3(0, 1, 0), this.scene);
    ambient.intensity = W05_LIGHTING.ambientIntensity;
    ambient.diffuse = W05_LIGHTING.ambientColor;

    // Sun (directional light filtered through ash)
    const sun = new BABYLON.PointLight('w05_sun', new BABYLON.Vector3(100, 50, 100), this.scene);
    sun.intensity = W05_LIGHTING.sunIntensity;

    // Fog
    this.scene.fogMode = BABYLON.Scene.FOGMODE_LINEAR;
    this.scene.fogColor = W05_LIGHTING.fogColor;
    this.scene.fogStart = W05_LIGHTING.fogStart;
    this.scene.fogEnd = W05_LIGHTING.fogEnd;

    gameEvents.emit('environment_lighting_applied', { environment: 'W05', lighting: 'canonical' });
  }

  /**
   * Load and position all assets for a zone
   */
  loadZone(zoneId: string): void {
    const zone = W05_ZONES[zoneId];
    if (!zone) {
      console.error(`[W05] Zone not found: ${zoneId}`);
      return;
    }

    this.activeZones.add(zoneId);

    // Load zone assets
    zone.assets.forEach((assetId) => {
      const asset = W05_ASSETS[assetId];
      if (!asset) return;

      // Find placements for this asset in this zone
      const placements = W05_ASSET_PLACEMENTS.filter(
        (p) => p.assetId === assetId && p.zone === zoneId
      );

      placements.forEach((placement) => {
        this.createAssetMesh(asset, placement);
      });
    });

    gameEvents.emit('zone_loaded', { zone: zoneId, zoneData: zone });
  }

  /**
   * Create a mesh for an asset
   */
  private createAssetMesh(asset: typeof W05_ASSETS[keyof typeof W05_ASSETS], placement: AssetPlacement): BABYLON.AbstractMesh {
    let mesh: BABYLON.AbstractMesh;

    // Create geometry based on asset type
    if (asset.dimensions.radius !== undefined && asset.dimensions.height !== undefined) {
      // Cylinder-based asset
      mesh = BABYLON.MeshBuilder.CreateCylinder(
        `mesh_${asset.id}`,
        {
          diameter: asset.dimensions.radius * 2,
          height: asset.dimensions.height,
          tessellation: 8,
        },
        this.scene
      );
    } else {
      // Box-based asset
      mesh = BABYLON.MeshBuilder.CreateBox(
        `mesh_${asset.id}`,
        {
          width: asset.dimensions.width || 1,
          height: asset.dimensions.height || 1,
          depth: asset.dimensions.depth || 1,
        },
        this.scene
      );
    }

    // Position and transform
    mesh.position = placement.position;
    if (placement.rotation) {
      mesh.rotation = placement.rotation;
    }
    if (placement.scale) {
      mesh.scaling = new BABYLON.Vector3(placement.scale, placement.scale, placement.scale);
    }

    // Apply material with correct palette
    const material = new BABYLON.StandardMaterial(`mat_${asset.id}`, this.scene);
    (material as any).diffuse = this.hexToColor3(asset.hazard ? W05_PALETTE.emberLava : W05_PALETTE.charredStone);

    if (asset.glowColor) {
      material.emissiveColor = this.hexToColor3(asset.glowColor);
    }

    mesh.material = material;

    // Store reference
    this.loadedAssets.set(`${placement.assetId}_${placement.zone}`, mesh);

    return mesh;
  }

  /**
   * Convert hex color to BABYLON.Color3
   */
  private hexToColor3(hex: string): BABYLON.Color3 {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    if (!result) return BABYLON.Color3.White();

    return new BABYLON.Color3(
      parseInt(result[1], 16) / 255,
      parseInt(result[2], 16) / 255,
      parseInt(result[3], 16) / 255
    );
  }

  /**
   * Get all active zones
   */
  getActiveZones(): string[] {
    return Array.from(this.activeZones);
  }

  /**
   * Unload zone resources
   */
  unloadZone(zoneId: string): void {
    this.activeZones.delete(zoneId);
    // Dispose meshes as needed
  }

  /**
   * Dispose all resources
   */
  dispose(): void {
    this.loadedAssets.forEach((mesh) => mesh.dispose());
    this.loadedAssets.clear();
    this.activeZones.clear();
  }
}

export default W05EnvironmentManager;
