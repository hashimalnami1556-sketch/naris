/**
 * Blender Asset Integration Layer
 * Bridges Blender-exported assets with Babylon.js game engine
 *
 * Handles:
 * - Character mesh import (Demon King / Ren Ashwalker)
 * - Animation rigging and keyframe mapping
 * - Particle effect setup (rain, fog, fire, sparks)
 * - Creature patrol path conversion
 */

import * as BABYLON from 'babylonjs';
import { gameEvents } from '../core/EventSystem';
import { CHARACTER_REN_ASHWALKER, CHARACTER_BONE_BEAST } from '../core/CharacterCompendium';

export interface RiggedCharacterData {
  mesh: BABYLON.Mesh;
  skeleton: BABYLON.Skeleton;
  animations: Map<string, BABYLON.AnimationGroup>;
  armature: BABYLON.TransformNode;
}

export interface ParticleEffectConfig {
  name: string;
  type: 'rain' | 'fog' | 'fire_sparks' | 'splash';
  emitterPos: BABYLON.Vector3;
  particleCount: number;
  lifeTime: number;
  emitRate: number;
}

export interface CreaturePatrolRoute {
  name: string;
  points: BABYLON.Vector3[];
  targetMeshPatterns: string[]; // e.g., ["Crow", "Night_Crow"]
  duration: number;
  offset: number;
}

// ============================================================
// Blender Character Loader
// ============================================================
export class BlenderCharacterLoader {
  private static instance: BlenderCharacterLoader;
  private scene: BABYLON.Scene;
  private loadedCharacters: Map<string, RiggedCharacterData> = new Map();
  private assetFolder: string = 'assets/characters/blender-exports/';

  private constructor(scene: BABYLON.Scene) {
    this.scene = scene;
  }

  static getInstance(scene?: BABYLON.Scene): BlenderCharacterLoader {
    if (!BlenderCharacterLoader.instance && scene) {
      BlenderCharacterLoader.instance = new BlenderCharacterLoader(scene);
    }
    return BlenderCharacterLoader.instance;
  }

  /**
   * Load Ren the Ashwalker (Demon King equivalent) from Blender export
   * Based on: demon_king_base_mesh.py + naris_advanced_rigging_physics.py
   */
  async loadRenAshwalker(onProgress?: (progress: number) => void): Promise<RiggedCharacterData> {
    try {
      // Check if already loaded
      if (this.loadedCharacters.has('char_ren_ashwalker')) {
        return this.loadedCharacters.get('char_ren_ashwalker')!;
      }

      onProgress?.(0);

      // Import GLB with skeleton and animations
      const importMesh = await BABYLON.SceneLoader.ImportMeshAsync(
        '',
        this.assetFolder,
        'ren_ashwalker_rigged.glb',
        this.scene
      );

      onProgress?.(50);

      const mesh = importMesh.meshes[0] as BABYLON.Mesh;
      const skeleton = importMesh.skeletons[0];
      const animationGroups = importMesh.animationGroups;

      // Build animation map
      const animationMap = new Map<string, BABYLON.AnimationGroup>();
      animationGroups.forEach((anim) => {
        // Map Blender animation names to gameplay actions
        if (anim.name.includes('Idle') || anim.name.includes('Breathing')) {
          animationMap.set('idle', anim);
        } else if (anim.name.includes('Aether_Step') || anim.name.includes('Step')) {
          animationMap.set('aether_step', anim);
        } else if (anim.name.includes('Slash') || anim.name.includes('Attack')) {
          animationMap.set('attack', anim);
        } else if (anim.name.includes('Dual') || anim.name.includes('Sword')) {
          animationMap.set('dual_attack', anim);
        }
      });

      // Ensure key animations exist (create fallbacks if needed)
      if (!animationMap.has('idle')) {
        const idleAnim = this.createIdleAnimation('idle_fallback');
        animationMap.set('idle', idleAnim);
      }

      onProgress?.(90);

      const riggedData: RiggedCharacterData = {
        mesh,
        skeleton,
        animations: animationMap,
        armature: mesh.parent as BABYLON.TransformNode,
      };

      this.loadedCharacters.set('char_ren_ashwalker', riggedData);

      onProgress?.(100);

      gameEvents.emit('blender_character_loaded', {
        character: 'Ren Ashwalker',
        boneStat: {
          health: CHARACTER_REN_ASHWALKER.stats.health,
          maxHealth: CHARACTER_REN_ASHWALKER.stats.maxHealth,
          attackDamage: CHARACTER_REN_ASHWALKER.stats.attackDamage,
        },
      });

      return riggedData;
    } catch (error) {
      console.error('[BlenderCharacterLoader] Failed to load Ren Ashwalker:', error);
      throw error;
    }
  }

  /**
   * Load Bone Beast boss from Blender export
   */
  async loadBoneBeast(onProgress?: (progress: number) => void): Promise<RiggedCharacterData> {
    try {
      if (this.loadedCharacters.has('char_bone_beast_boss')) {
        return this.loadedCharacters.get('char_bone_beast_boss')!;
      }

      onProgress?.(0);

      const importMesh = await BABYLON.SceneLoader.ImportMeshAsync(
        '',
        this.assetFolder,
        'bone_beast_boss.glb',
        this.scene
      );

      onProgress?.(50);

      const mesh = importMesh.meshes[0] as BABYLON.Mesh;
      const skeleton = importMesh.skeletons[0];
      const animationGroups = importMesh.animationGroups;

      const animationMap = new Map<string, BABYLON.AnimationGroup>();
      animationGroups.forEach((anim) => {
        if (anim.name.includes('Idle') || anim.name.includes('Breathing')) {
          animationMap.set('idle_threatening', anim);
        } else if (anim.name.includes('Charge') || anim.name.includes('Slam')) {
          animationMap.set('ground_slam', anim);
        } else if (anim.name.includes('Claw') || anim.name.includes('Swipe')) {
          animationMap.set('claw_swipe', anim);
        } else if (anim.name.includes('Fire') || anim.name.includes('Breath')) {
          animationMap.set('fire_breath', anim);
        } else if (anim.name.includes('Defeat') || anim.name.includes('Collapse')) {
          animationMap.set('defeat', anim);
        }
      });

      onProgress?.(90);

      const riggedData: RiggedCharacterData = {
        mesh,
        skeleton,
        animations: animationMap,
        armature: mesh.parent as BABYLON.TransformNode,
      };

      this.loadedCharacters.set('char_bone_beast_boss', riggedData);
      onProgress?.(100);

      gameEvents.emit('blender_character_loaded', {
        character: 'Bone Beast Boss',
        stats: CHARACTER_BONE_BEAST.stats,
      });

      return riggedData;
    } catch (error) {
      console.error('[BlenderCharacterLoader] Failed to load Bone Beast:', error);
      throw error;
    }
  }

  /**
   * Get animation group by name
   */
  getAnimation(characterId: string, animationName: string): BABYLON.AnimationGroup | null {
    const character = this.loadedCharacters.get(characterId);
    return character?.animations.get(animationName) || null;
  }

  /**
   * Play animation on character
   */
  playAnimation(characterId: string, animationName: string, loopMode: number = 1): void {
    const animation = this.getAnimation(characterId, animationName);
    if (animation) {
      animation.play(loopMode === 1);
    }
  }

  /**
   * Stop all animations
   */
  stopAnimations(characterId: string): void {
    const character = this.loadedCharacters.get(characterId);
    if (character) {
      character.animations.forEach((anim) => anim.stop());
    }
  }

  /**
   * Create fallback idle animation
   */
  private createIdleAnimation(name: string): BABYLON.AnimationGroup {
    const animGroup = new BABYLON.AnimationGroup(name, this.scene);
    // Placeholder — real animation should come from Blender
    return animGroup;
  }

  /**
   * Dispose character resources
   */
  disposeCharacter(characterId: string): void {
    const character = this.loadedCharacters.get(characterId);
    if (character) {
      character.mesh.dispose();
      character.skeleton.dispose();
      character.animations.forEach((anim) => anim.dispose());
      this.loadedCharacters.delete(characterId);
    }
  }
}

// ============================================================
// Blender Particle Effect Loader
// ============================================================
export class BlenderParticleEffectLoader {
  private static instance: BlenderParticleEffectLoader;
  private scene: BABYLON.Scene;
  private particleSystems: Map<string, BABYLON.IParticleSystem> = new Map();

  private constructor(scene: BABYLON.Scene) {
    this.scene = scene;
  }

  static getInstance(scene?: BABYLON.Scene): BlenderParticleEffectLoader {
    if (!BlenderParticleEffectLoader.instance && scene) {
      BlenderParticleEffectLoader.instance = new BlenderParticleEffectLoader(scene);
    }
    return BlenderParticleEffectLoader.instance;
  }

  /**
   * Load rain system from Blender particle export
   * From: naris_particle_fx_upgrade.py (240 rain drops)
   */
  createRainSystem(config: ParticleEffectConfig): BABYLON.ParticleSystem {
    // Create emitter
    const emitter = BABYLON.MeshBuilder.CreateBox('rain_emitter', { size: 50 }, this.scene);
    emitter.position = config.emitterPos;
    emitter.isVisible = false;

    // Create particle system
    const particleSystem = new BABYLON.ParticleSystem('rain_system', config.particleCount, this.scene);
    particleSystem.emitter = emitter;

    // Rain appearance (thin cyan/blue drops)
    particleSystem.minSize = 0.01;
    particleSystem.maxSize = 0.015;

    // Lifetime and emission
    particleSystem.minLifeTime = 2;
    particleSystem.maxLifeTime = 4;
    particleSystem.emitRate = config.emitRate || 60;

    // Falling motion
    particleSystem.gravity = new BABYLON.Vector3(0, -9.8, 0);
    particleSystem.minEmitPower = 0.5;
    particleSystem.maxEmitPower = 1.5;

    // Color: rain blue
    particleSystem.addColorGradient(0, new BABYLON.Color4(0.2, 0.55, 0.9, 0.6));
    particleSystem.addColorGradient(1, new BABYLON.Color4(0.1, 0.35, 1.0, 0));

    this.particleSystems.set('rain', particleSystem);
    return particleSystem;
  }

  /**
   * Load animated fog system
   * From: naris_particle_fx_upgrade.py (animated fog + puffs)
   */
  createFogSystem(config: ParticleEffectConfig): BABYLON.ParticleSystem {
    const emitter = BABYLON.MeshBuilder.CreateBox('fog_emitter', { size: 60 }, this.scene);
    emitter.position = config.emitterPos;
    emitter.isVisible = false;

    const fogSystem = new BABYLON.ParticleSystem('fog_system', config.particleCount, this.scene);
    fogSystem.emitter = emitter;

    fogSystem.minSize = 0.5;
    fogSystem.maxSize = 1.5;
    fogSystem.minLifeTime = 4;
    fogSystem.maxLifeTime = 8;
    fogSystem.emitRate = config.emitRate || 20;

    // Fog floats upward slowly
    fogSystem.gravity = new BABYLON.Vector3(0, 0.5, 0);

    // Grey ash color
    fogSystem.addColorGradient(0, new BABYLON.Color4(0.15, 0.12, 0.1, 0.3));
    fogSystem.addColorGradient(0.5, new BABYLON.Color4(0.2, 0.15, 0.12, 0.5));
    fogSystem.addColorGradient(1, new BABYLON.Color4(0.1, 0.1, 0.1, 0));

    this.particleSystems.set('fog', fogSystem);
    return fogSystem;
  }

  /**
   * Load fire sparks system
   * From: naris_particle_fx_upgrade.py (90 sparks with upward spray)
   */
  createFireSparksSystem(config: ParticleEffectConfig): BABYLON.ParticleSystem {
    const emitter = BABYLON.MeshBuilder.CreateSphere('spark_emitter', { diameter: 2 }, this.scene);
    emitter.position = config.emitterPos;
    emitter.isVisible = false;

    const sparkSystem = new BABYLON.ParticleSystem('spark_system', config.particleCount, this.scene);
    sparkSystem.emitter = emitter;

    sparkSystem.minSize = 0.012;
    sparkSystem.maxSize = 0.032;
    sparkSystem.minLifeTime = 1;
    sparkSystem.maxLifeTime = 3;
    sparkSystem.emitRate = config.emitRate || 45;

    // Upward burst
    sparkSystem.minEmitPower = 2;
    sparkSystem.maxEmitPower = 5;
    sparkSystem.gravity = new BABYLON.Vector3(0, -2, 0);

    // Bright orange/red emission
    sparkSystem.addColorGradient(0, new BABYLON.Color4(1.0, 0.025, 0.001, 1));
    sparkSystem.addColorGradient(0.7, new BABYLON.Color4(1.0, 0.45, 0.1, 0.8));
    sparkSystem.addColorGradient(1, new BABYLON.Color4(1.0, 0.1, 0.001, 0));

    this.particleSystems.set('fire_sparks', sparkSystem);
    return sparkSystem;
  }

  /**
   * Dispose all particle systems
   */
  dispose(): void {
    this.particleSystems.forEach((system) => system.dispose());
    this.particleSystems.clear();
  }
}

// ============================================================
// Creature Patrol Route Manager
// ============================================================
export class CreaturePatrolManager {
  private static instance: CreaturePatrolManager;
  private scene: BABYLON.Scene;
  private patrolRoutes: Map<string, CreaturePatrolRoute> = new Map();
  private pathMeshes: Map<string, BABYLON.Mesh> = new Map();

  private constructor(scene: BABYLON.Scene) {
    this.scene = scene;
  }

  static getInstance(scene?: BABYLON.Scene): CreaturePatrolManager {
    if (!CreaturePatrolManager.instance && scene) {
      CreaturePatrolManager.instance = new CreaturePatrolManager(scene);
    }
    return CreaturePatrolManager.instance;
  }

  /**
   * Register creature patrol route from Blender path data
   * From: naris_creature_path_follow.py
   */
  registerPatrolRoute(route: CreaturePatrolRoute): void {
    this.patrolRoutes.set(route.name, route);

    // Create visual Bezier curve for debugging
    const curve = BABYLON.Curve3.CreateCatmullRomSpline(route.points, 20, true);
    const tubeData = BABYLON.MeshBuilder.CreateTube(
      `patrol_path_${route.name}`,
      {
        path: curve.getPoints(),
        radius: 0.2,
        updatable: false,
      },
      this.scene
    );

    tubeData.isVisible = false; // Hidden by default, enable for debugging
    const debugMat = new BABYLON.StandardMaterial(`debug_${route.name}`, this.scene);
    debugMat.emissiveColor = new BABYLON.Color3(1, 0.5, 0);
    tubeData.material = debugMat;

    this.pathMeshes.set(route.name, tubeData);

    gameEvents.emit('patrol_route_registered', {
      route: route.name,
      pointCount: route.points.length,
      duration: route.duration,
    });
  }

  /**
   * Get patrol route by name
   */
  getPatrolRoute(name: string): CreaturePatrolRoute | null {
    return this.patrolRoutes.get(name) || null;
  }

  /**
   * Register Crow patrol route
   */
  registerCrowPatrol(): void {
    this.registerPatrolRoute({
      name: 'Crow_Patrol',
      points: [
        new BABYLON.Vector3(-12, 14, 5.5),
        new BABYLON.Vector3(-5, 19, 6.5),
        new BABYLON.Vector3(4, 17, 5.8),
        new BABYLON.Vector3(11, 12, 6.2),
        new BABYLON.Vector3(4, 8, 5.4),
        new BABYLON.Vector3(-8, 10, 5.7),
      ],
      targetMeshPatterns: ['Crow', 'Night_Crow'],
      duration: 240,
      offset: 0,
    });
  }

  /**
   * Register Rat patrol route
   */
  registerRatPatrol(): void {
    this.registerPatrolRoute({
      name: 'Rat_Patrol',
      points: [
        new BABYLON.Vector3(-6, -15, 0.22),
        new BABYLON.Vector3(-3, -16, 0.22),
        new BABYLON.Vector3(1, -14, 0.22),
        new BABYLON.Vector3(4, -16, 0.22),
        new BABYLON.Vector3(1, -18, 0.22),
        new BABYLON.Vector3(-5, -18, 0.22),
      ],
      targetMeshPatterns: ['Rat', 'Night_Rat'],
      duration: 240,
      offset: 0,
    });
  }

  /**
   * Register Marsh Animal patrol route
   */
  registerMarshAnimalPatrol(): void {
    this.registerPatrolRoute({
      name: 'Marsh_Animal_Patrol',
      points: [
        new BABYLON.Vector3(-18, 2, 0.35),
        new BABYLON.Vector3(-13, 6, 0.3),
        new BABYLON.Vector3(-8, 4, 0.28),
        new BABYLON.Vector3(-10, -1, 0.3),
        new BABYLON.Vector3(-16, -4, 0.35),
      ],
      targetMeshPatterns: ['Bone_Hound', 'Animal', 'Fauna'],
      duration: 240,
      offset: 0,
    });
  }

  /**
   * Toggle debug visualization of patrol paths
   */
  togglePathVisualization(visible: boolean): void {
    this.pathMeshes.forEach((mesh) => {
      mesh.isVisible = visible;
    });
  }

  /**
   * Dispose all patrol routes
   */
  dispose(): void {
    this.pathMeshes.forEach((mesh) => mesh.dispose());
    this.pathMeshes.clear();
    this.patrolRoutes.clear();
  }
}

export default {
  BlenderCharacterLoader,
  BlenderParticleEffectLoader,
  CreaturePatrolManager,
};
