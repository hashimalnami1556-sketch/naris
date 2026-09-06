/**
 * Particle System - نظام الجسيمات
 * إدارة المؤثرات البصية والجسيمات
 */

import { Vector3, Scene, ParticleSystem as BabylonParticleSystem, Texture } from 'babylonjs';
import { gameEvents } from './EventSystem';

export type ParticleType = 'fire' | 'lightning' | 'ice' | 'blood' | 'heal' | 'dust' | 'spark';

export interface ParticleEmitterConfig {
  type: ParticleType;
  position: Vector3;
  duration?: number;
  intensity?: number;
  velocity?: Vector3;
}

export class ParticleSystem {
  private static instance: ParticleSystem;
  private activeEmitters: Map<string, BabylonParticleSystem> = new Map();
  private emitterIdCounter: number = 0;
  private scene: Scene | null = null;
  private maxParticles: number = 2000;
  private particleCount: number = 0;

  private constructor() {
    console.log('✨ ParticleSystem initialized');
  }

  /**
   * الحصول على نسخة واحدة من نظام الجسيمات
   */
  static getInstance(): ParticleSystem {
    if (!ParticleSystem.instance) {
      ParticleSystem.instance = new ParticleSystem();
    }
    return ParticleSystem.instance;
  }

  /**
   * تعيين المشهد
   */
  setScene(scene: Scene): void {
    this.scene = scene;
    console.log('✓ Scene assigned to ParticleSystem');
  }

  /**
   * إنشاء باعث جسيمات
   */
  createEmitter(config: ParticleEmitterConfig): string {
    if (!this.scene) {
      console.warn('Scene not initialized for ParticleSystem');
      return '';
    }

    const emitterId = `emitter_${this.emitterIdCounter++}`;
    const particleSystem = this.createParticleSystem(config.type, this.scene, config.position);

    if (particleSystem) {
      this.activeEmitters.set(emitterId, particleSystem);
      particleSystem.start();

      // Auto-cleanup after duration
      if (config.duration) {
        setTimeout(() => {
          this.stopEmitter(emitterId);
        }, config.duration * 1000);
      }

      this.particleCount += particleSystem.getCapacity();
      gameEvents.emit('particle_emitter_created', { emitterId, type: config.type });
    }

    return emitterId;
  }

  /**
   * إنشاء نظام جسيمات بناءً على النوع
   */
  private createParticleSystem(
    type: ParticleType,
    scene: Scene,
    position: Vector3
  ): BabylonParticleSystem | null {
    const particleSystem = new BabylonParticleSystem('particles', 500, scene);

    switch (type) {
      case 'fire':
        return this.configureFireParticles(particleSystem, position);
      case 'lightning':
        return this.configureLightningParticles(particleSystem, position);
      case 'ice':
        return this.configureIceParticles(particleSystem, position);
      case 'blood':
        return this.configureBloodParticles(particleSystem, position);
      case 'heal':
        return this.configureHealParticles(particleSystem, position);
      case 'dust':
        return this.configureDustParticles(particleSystem, position);
      case 'spark':
        return this.configureSparkParticles(particleSystem, position);
      default:
        return null;
    }
  }

  /**
   * تكوين جسيمات النار
   */
  private configureFireParticles(
    ps: BabylonParticleSystem,
    position: Vector3
  ): BabylonParticleSystem {
    ps.emitter = position;
    ps.minEmitBox = new Vector3(-0.5, 0, -0.5);
    ps.maxEmitBox = new Vector3(0.5, 0, 0.5);

    ps.particleTexture = new Texture('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==', this.scene);

    ps.addColorGradient(0, 1, 0.5, 0);
    ps.addColorGradient(1, 1, 0, 0);
    ps.addAlphaGradient(0, 1);
    ps.addAlphaGradient(0.5, 0.7);
    ps.addAlphaGradient(1, 0);

    ps.minLifeTime = 0.2;
    ps.maxLifeTime = 1;
    ps.emitRate = 100;
    ps.gravity = new Vector3(0, 2, 0);
    ps.minEmitPower = 1;
    ps.maxEmitPower = 3;
    ps.minSize = 0.1;
    ps.maxSize = 0.5;
    ps.minScaleX = 0.8;
    ps.maxScaleX = 1.5;
    ps.minScaleY = 0.8;
    ps.maxScaleY = 1.5;

    return ps;
  }

  /**
   * تكوين جسيمات البرق
   */
  private configureLightningParticles(
    ps: BabylonParticleSystem,
    position: Vector3
  ): BabylonParticleSystem {
    ps.emitter = position;
    ps.minEmitBox = new Vector3(-0.2, 0, -0.2);
    ps.maxEmitBox = new Vector3(0.2, 1, 0.2);

    ps.addColorGradient(0, 0.3, 0.8, 1);
    ps.addColorGradient(0.5, 0.5, 0.9, 1);
    ps.addColorGradient(1, 0.2, 0.4, 1);
    ps.addAlphaGradient(0, 1);
    ps.addAlphaGradient(0.7, 0.5);
    ps.addAlphaGradient(1, 0);

    ps.minLifeTime = 0.1;
    ps.maxLifeTime = 0.5;
    ps.emitRate = 50;
    ps.gravity = new Vector3(0, -5, 0);
    ps.minEmitPower = 2;
    ps.maxEmitPower = 5;
    ps.minSize = 0.05;
    ps.maxSize = 0.2;

    return ps;
  }

  /**
   * تكوين جسيمات الجليد
   */
  private configureIceParticles(
    ps: BabylonParticleSystem,
    position: Vector3
  ): BabylonParticleSystem {
    ps.emitter = position;
    ps.minEmitBox = new Vector3(-1, 0, -1);
    ps.maxEmitBox = new Vector3(1, 2, 1);

    ps.addColorGradient(0, 0.7, 0.9, 1);
    ps.addColorGradient(1, 0.5, 0.8, 1);
    ps.addAlphaGradient(0, 0.8);
    ps.addAlphaGradient(0.5, 0.4);
    ps.addAlphaGradient(1, 0);

    ps.minLifeTime = 0.5;
    ps.maxLifeTime = 2;
    ps.emitRate = 30;
    ps.gravity = new Vector3(0, -1, 0);
    ps.minEmitPower = 0.5;
    ps.maxEmitPower = 2;
    ps.minSize = 0.1;
    ps.maxSize = 0.4;

    return ps;
  }

  /**
   * تكوين جسيمات الدم
   */
  private configureBloodParticles(
    ps: BabylonParticleSystem,
    position: Vector3
  ): BabylonParticleSystem {
    ps.emitter = position;
    ps.minEmitBox = new Vector3(-0.3, 0, -0.3);
    ps.maxEmitBox = new Vector3(0.3, 0.5, 0.3);

    ps.addColorGradient(0, 0.8, 0.1, 0.1);
    ps.addColorGradient(1, 0.4, 0.05, 0.05);
    ps.addAlphaGradient(0, 1);
    ps.addAlphaGradient(0.7, 0.5);
    ps.addAlphaGradient(1, 0);

    ps.minLifeTime = 0.5;
    ps.maxLifeTime = 2;
    ps.emitRate = 40;
    ps.gravity = new Vector3(0, -5, 0);
    ps.minEmitPower = 1;
    ps.maxEmitPower = 4;
    ps.minSize = 0.05;
    ps.maxSize = 0.2;

    return ps;
  }

  /**
   * تكوين جسيمات الشفاء
   */
  private configureHealParticles(
    ps: BabylonParticleSystem,
    position: Vector3
  ): BabylonParticleSystem {
    ps.emitter = position;
    ps.minEmitBox = new Vector3(-0.5, 0, -0.5);
    ps.maxEmitBox = new Vector3(0.5, 0, 0.5);

    ps.addColorGradient(0, 0.3, 1, 0.3);
    ps.addColorGradient(0.5, 0.5, 1, 0.5);
    ps.addColorGradient(1, 0.2, 0.8, 0.2);
    ps.addAlphaGradient(0, 1);
    ps.addAlphaGradient(0.5, 0.7);
    ps.addAlphaGradient(1, 0);

    ps.minLifeTime = 0.5;
    ps.maxLifeTime = 1.5;
    ps.emitRate = 50;
    ps.gravity = new Vector3(0, 2, 0);
    ps.minEmitPower = 1;
    ps.maxEmitPower = 3;
    ps.minSize = 0.1;
    ps.maxSize = 0.3;

    return ps;
  }

  /**
   * تكوين جسيمات الغبار
   */
  private configureDustParticles(
    ps: BabylonParticleSystem,
    position: Vector3
  ): BabylonParticleSystem {
    ps.emitter = position;
    ps.minEmitBox = new Vector3(-1, 0, -1);
    ps.maxEmitBox = new Vector3(1, 0.5, 1);

    ps.addColorGradient(0, 0.9, 0.85, 0.75);
    ps.addColorGradient(1, 0.7, 0.65, 0.55);
    ps.addAlphaGradient(0, 0.6);
    ps.addAlphaGradient(0.5, 0.3);
    ps.addAlphaGradient(1, 0);

    ps.minLifeTime = 1;
    ps.maxLifeTime = 3;
    ps.emitRate = 20;
    ps.gravity = new Vector3(0, 0.5, 0);
    ps.minEmitPower = 0.5;
    ps.maxEmitPower = 1.5;
    ps.minSize = 0.2;
    ps.maxSize = 0.8;

    return ps;
  }

  /**
   * تكوين جسيمات الشرارات
   */
  private configureSparkParticles(
    ps: BabylonParticleSystem,
    position: Vector3
  ): BabylonParticleSystem {
    ps.emitter = position;
    ps.minEmitBox = new Vector3(-0.2, 0, -0.2);
    ps.maxEmitBox = new Vector3(0.2, 0, 0.2);

    ps.addColorGradient(0, 1, 1, 0.5);
    ps.addColorGradient(0.5, 1, 0.7, 0.2);
    ps.addColorGradient(1, 1, 0.3, 0);
    ps.addAlphaGradient(0, 1);
    ps.addAlphaGradient(0.7, 0.3);
    ps.addAlphaGradient(1, 0);

    ps.minLifeTime = 0.2;
    ps.maxLifeTime = 0.8;
    ps.emitRate = 60;
    ps.gravity = new Vector3(0, -3, 0);
    ps.minEmitPower = 2;
    ps.maxEmitPower = 6;
    ps.minSize = 0.03;
    ps.maxSize = 0.15;

    return ps;
  }

  /**
   * إيقاف باعث الجسيمات
   */
  stopEmitter(emitterId: string): void {
    const ps = this.activeEmitters.get(emitterId);
    if (ps) {
      ps.stop();
      setTimeout(() => {
        ps.dispose();
        this.activeEmitters.delete(emitterId);
        this.particleCount -= ps.getCapacity();
      }, 100);

      gameEvents.emit('particle_emitter_stopped', { emitterId });
    }
  }

  /**
   * الحصول على عدد الجسيمات النشطة
   */
  getActiveParticleCount(): number {
    let count = 0;
    this.activeEmitters.forEach((ps) => {
      if (ps.isPlaying) {
        count += ps.getCapacity();
      }
    });
    return count;
  }

  /**
   * الحصول على إحصائيات الجسيمات
   */
  getStats(): { active: number; total: number; maxParticles: number } {
    return {
      active: this.activeEmitters.size,
      total: this.particleCount,
      maxParticles: this.maxParticles,
    };
  }

  /**
   * تنظيف جميع الجسيمات
   */
  dispose(): void {
    this.activeEmitters.forEach((ps) => {
      ps.dispose();
    });
    this.activeEmitters.clear();
    this.particleCount = 0;
    console.log('🗑️ ParticleSystem disposed');
  }
}

// تصدير نسخة واحدة
export const particleSystem = ParticleSystem.getInstance();
