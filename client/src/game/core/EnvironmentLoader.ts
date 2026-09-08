/**
 * Environment Loader - مُحمِّل البيئات
 * تحميل وإدارة العناصر والمستويات المختلفة في اللعبة
 */

import * as BABYLON from 'babylonjs';
import {
  EnvironmentData,
  EnvironmentAsset,
  EnvironmentZone,
  getEnvironment,
  ENVIRONMENT_REGISTRY,
} from './EnvironmentConfig';
import { gameEvents } from './EventSystem';

export interface LoadedEnvironmentAssets {
  meshes: Map<string, BABYLON.AbstractMesh>;
  materials: Map<string, BABYLON.Material>;
  textures: Map<string, BABYLON.Texture>;
}

export class EnvironmentLoader {
  private static instance: EnvironmentLoader;
  private scene: BABYLON.Scene | null = null;
  private currentEnvironment: EnvironmentData | null = null;
  private loadedAssets: LoadedEnvironmentAssets = {
    meshes: new Map(),
    materials: new Map(),
    textures: new Map(),
  };
  private activeZones: Set<string> = new Set();
  private loadingProgress: number = 0;
  private maxConcurrentLoads: number = 5;
  private loadQueue: Array<() => Promise<void>> = [];
  private isLoading: boolean = false;

  private constructor(scene?: BABYLON.Scene) {
    this.scene = scene || null;
    console.log('📦 EnvironmentLoader initialized');
  }

  /**
   * الحصول على نسخة واحدة من محمِّل البيئات
   */
  static getInstance(): EnvironmentLoader {
    if (!EnvironmentLoader.instance) {
      EnvironmentLoader.instance = new EnvironmentLoader();
    }
    return EnvironmentLoader.instance;
  }

  /**
   * تعيين المشهد
   */
  setScene(scene: BABYLON.Scene): void {
    this.scene = scene;
    console.log('✓ Scene assigned to EnvironmentLoader');
  }

  /**
   * تحميل بيئة كاملة
   */
  async loadEnvironment(environmentId: string): Promise<boolean> {
    if (!this.scene) {
      console.warn('⚠️ Scene not initialized');
      return false;
    }

    const environment = getEnvironment(environmentId);
    if (!environment) {
      console.warn(`⚠️ Environment not found: ${environmentId}`);
      return false;
    }

    this.isLoading = true;
    this.loadingProgress = 0;
    this.currentEnvironment = environment;

    gameEvents.emit('environment_loading_start', {
      environmentId,
      name: environment.displayName,
    });

    try {
      // Setup lighting
      this.setupLighting(environment);

      // Setup skybox
      this.setupSkybox(environment);

      // Queue asset loads
      this.queueAssetLoads(environment.assets);

      // Process load queue
      await this.processLoadQueue();

      // Setup zones
      this.setupZones(environment.zones);

      // Setup music
      this.setupMusic(environment);

      gameEvents.emit('environment_loading_complete', {
        environmentId,
        name: environment.displayName,
        assetsLoaded: this.loadedAssets.meshes.size,
      });

      console.log(`✓ Environment loaded: ${environment.displayName}`);
      this.isLoading = false;
      return true;
    } catch (error) {
      console.error(`✗ Failed to load environment: ${error}`);
      gameEvents.emit('environment_loading_failed', {
        environmentId,
        error: String(error),
      });
      this.isLoading = false;
      return false;
    }
  }

  /**
   * إعداد الإضاءة
   */
  private setupLighting(environment: EnvironmentData): void {
    if (!this.scene) return;

    const lighting = environment.lighting;

    // Ambient light
    this.scene.ambientColor = new BABYLON.Color3(
      lighting.ambientColor.r,
      lighting.ambientColor.g,
      lighting.ambientColor.b
    );

    // Directional light (Sun)
    const sunLight = new BABYLON.HemisphericLight(
      'sun_light',
      new BABYLON.Vector3(
        lighting.sunDirection.x,
        lighting.sunDirection.y,
        lighting.sunDirection.z
      ),
      this.scene
    );

    sunLight.intensity = 0.8;
    sunLight.diffuse = new BABYLON.Color3(
      lighting.sunColor.r,
      lighting.sunColor.g,
      lighting.sunColor.b
    );

    // Fog
    this.scene.fogMode = BABYLON.Scene.FOGMODE_LINEAR;
    this.scene.fogColor = new BABYLON.Color3(
      lighting.fogColor.r,
      lighting.fogColor.g,
      lighting.fogColor.b
    );
    this.scene.fogStart = lighting.fogStart;
    this.scene.fogEnd = lighting.fogEnd;

    console.log('✓ Lighting configured');
  }

  /**
   * إعداد Skybox
   */
  private setupSkybox(environment: EnvironmentData): void {
    if (!this.scene) return;

    const skyboxAsset = environment.assets.find((a) => a.type === 'skybox');
    if (!skyboxAsset) return;

    // Create skybox material
    const skyboxMaterial = new BABYLON.StandardMaterial('skybox_material', this.scene);
    skyboxMaterial.emissiveColor = new BABYLON.Color3(0.8, 0.6, 0.4);
    skyboxMaterial.backFaceCulling = false;

    // Create skybox mesh
    const skybox = BABYLON.MeshBuilder.CreateBox('skybox', { size: 1000 }, this.scene);
    skybox.material = skyboxMaterial;

    // Attach skybox to camera
    if (this.scene.activeCamera) {
      skybox.parent = this.scene.activeCamera;
    }

    console.log('✓ Skybox configured');
  }

  /**
   * صف تحميل المواد
   */
  private queueAssetLoads(assets: EnvironmentAsset[]): void {
    // Group assets by category for optimized loading
    const assetsByCategory = this.groupAssetsByCategory(assets);

    // Queue category loads in priority order
    const categoryOrder = ['materials', 'textures', 'mesh', 'vfx'];

    for (const category of categoryOrder) {
      const categoryAssets = assetsByCategory[category] || [];

      for (const asset of categoryAssets) {
        this.loadQueue.push(() => this.loadAsset(asset));
      }
    }

    console.log(`📋 Queued ${this.loadQueue.length} assets for loading`);
  }

  /**
   * تجميع المواد حسب الفئة
   */
  private groupAssetsByCategory(
    assets: EnvironmentAsset[]
  ): Record<string, EnvironmentAsset[]> {
    const grouped: Record<string, EnvironmentAsset[]> = {};

    for (const asset of assets) {
      const mainCategory = asset.category.split('/')[0];
      if (!grouped[mainCategory]) {
        grouped[mainCategory] = [];
      }
      grouped[mainCategory].push(asset);
    }

    return grouped;
  }

  /**
   * تحميل مادة واحدة
   */
  private async loadAsset(asset: EnvironmentAsset): Promise<void> {
    try {
      switch (asset.type) {
        case 'mesh':
          await this.loadMesh(asset);
          break;
        case 'material':
          await this.loadMaterial(asset);
          break;
        case 'texture':
          await this.loadTexture(asset);
          break;
        case 'skybox':
          // Skybox handled separately
          break;
        default:
          console.warn(`⚠️ Unknown asset type: ${asset.type}`);
      }

      this.loadingProgress += 1;
      gameEvents.emit('asset_loaded', {
        assetId: asset.id,
        progress: this.loadingProgress,
      });
    } catch (error) {
      console.warn(`⚠️ Failed to load asset ${asset.id}:`, error);
    }
  }

  /**
   * تحميل mesh
   */
  private async loadMesh(asset: EnvironmentAsset): Promise<void> {
    if (!this.scene) return;

    // Simulate mesh loading
    const mesh = BABYLON.MeshBuilder.CreateBox(asset.id, { size: 1 }, this.scene);
    mesh.name = asset.name;
    mesh.metadata = { assetId: asset.id, category: asset.category };

    this.loadedAssets.meshes.set(asset.id, mesh);
  }

  /**
   * تحميل مادة
   */
  private async loadMaterial(asset: EnvironmentAsset): Promise<void> {
    if (!this.scene) return;

    const material = new BABYLON.StandardMaterial(asset.id, this.scene);
    material.name = asset.name;

    // Apply material based on category
    switch (asset.category) {
      case 'materials/stone':
        (material as any).diffuse = new BABYLON.Color3(0.5, 0.5, 0.5);
        material.specularColor = new BABYLON.Color3(0.3, 0.3, 0.3);
        break;
      case 'materials/bone':
        (material as any).diffuse = new BABYLON.Color3(0.9, 0.85, 0.8);
        material.specularColor = new BABYLON.Color3(0.5, 0.5, 0.5);
        break;
      case 'materials/aether':
        material.emissiveColor = new BABYLON.Color3(0.2, 0.6, 0.8);
        (material as any).diffuse = new BABYLON.Color3(0.1, 0.3, 0.5);
        break;
      case 'materials/ground':
        (material as any).diffuse = new BABYLON.Color3(0.6, 0.5, 0.4);
        (material as any).roughness = 0.8;
        break;
    }

    this.loadedAssets.materials.set(asset.id, material);
  }

  /**
   * تحميل نسيج
   */
  private async loadTexture(asset: EnvironmentAsset): Promise<void> {
    if (!this.scene) return;

    // Create placeholder texture
    const texture = new BABYLON.DynamicTexture(asset.id, 512, this.scene);
    texture.name = asset.name;

    this.loadedAssets.textures.set(asset.id, texture);
  }

  /**
   * معالجة قائمة التحميل
   */
  private async processLoadQueue(): Promise<void> {
    const batchSize = this.maxConcurrentLoads;

    while (this.loadQueue.length > 0) {
      const batch = this.loadQueue.splice(0, batchSize);
      await Promise.all(batch.map((load) => load()));
    }
  }

  /**
   * إعداد المناطق
   */
  private setupZones(zones: EnvironmentZone[]): void {
    for (const zone of zones) {
      gameEvents.emit('zone_registered', {
        zoneId: zone.id,
        name: zone.name,
        type: zone.type,
        position: zone.position,
        radius: zone.radius,
      });
    }

    console.log(`✓ ${zones.length} zones configured`);
  }

  /**
   * إعداد الموسيقى
   */
  private setupMusic(environment: EnvironmentData): void {
    gameEvents.emit('environment_music_set', {
      trackId: environment.musicTrack,
      intensity: 'exploration',
    });

    console.log(`🎵 Music track set: ${environment.musicTrack}`);
  }

  /**
   * تفريغ بيئة
   */
  async unloadEnvironment(): Promise<void> {
    if (!this.currentEnvironment) return;

    // Dispose meshes
    for (const mesh of this.loadedAssets.meshes.values()) {
      mesh.dispose();
    }

    // Dispose materials
    for (const material of this.loadedAssets.materials.values()) {
      material.dispose();
    }

    // Dispose textures
    for (const texture of this.loadedAssets.textures.values()) {
      texture.dispose();
    }

    this.loadedAssets = {
      meshes: new Map(),
      materials: new Map(),
      textures: new Map(),
    };

    this.activeZones.clear();
    this.currentEnvironment = null;

    gameEvents.emit('environment_unloaded', {});
    console.log('✓ Environment unloaded');
  }

  /**
   * الحصول على البيئة الحالية
   */
  getCurrentEnvironment(): EnvironmentData | null {
    return this.currentEnvironment;
  }

  /**
   * الحصول على المواد المُحمّلة
   */
  getLoadedAssets(): LoadedEnvironmentAssets {
    return this.loadedAssets;
  }

  /**
   * الحصول على تقدم التحميل
   */
  getLoadingProgress(): number {
    return this.loadingProgress;
  }

  /**
   * التحقق من اكتمال التحميل
   */
  isEnvironmentLoaded(): boolean {
    return !this.isLoading && this.currentEnvironment !== null;
  }

  /**
   * طباعة معلومات البيئة
   */
  printEnvironmentInfo(): void {
    if (!this.currentEnvironment) {
      console.log('No environment loaded');
      return;
    }

    const env = this.currentEnvironment;
    console.log(`
    📦 ENVIRONMENT LOADER STATUS
    ─────────────────────
    Current Environment: ${env.displayName}
    Type: ${env.type}

    Loaded Assets:
      Meshes: ${this.loadedAssets.meshes.size}
      Materials: ${this.loadedAssets.materials.size}
      Textures: ${this.loadedAssets.textures.size}

    Zones: ${env.zones.length}
    Spawn Points: ${env.spawnPoints.length}
    Cinematic Cameras: ${env.cinematicCameras.length}

    Loading Progress: ${this.loadingProgress}%
    ─────────────────────
    `);
  }

  /**
   * قائمة البيئات المتاحة
   */
  listAvailableEnvironments(): string[] {
    return Object.keys(ENVIRONMENT_REGISTRY);
  }
}

// تصدير نسخة واحدة
export const environmentLoader = EnvironmentLoader.getInstance();
