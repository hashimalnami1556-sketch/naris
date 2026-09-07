/**
 * Advanced VFX System - نظام التأثيرات البصرية المتقدمة
 * إنشاء وإدارة تأثيرات بصرية متقدمة وديناميكية
 */

import * as BABYLON from 'babylonjs';
import { gameEvents } from './EventSystem';

export type VFXEffectType =
  | 'explosion'
  | 'impact'
  | 'spell_cast'
  | 'heal'
  | 'buff'
  | 'debuff'
  | 'elemental_fire'
  | 'elemental_ice'
  | 'elemental_lightning'
  | 'elemental_poison'
  | 'portal'
  | 'teleport'
  | 'shield'
  | 'blood_splash'
  | 'dust_cloud'
  | 'water_splash';

export interface VFXEmitterConfig {
  type: VFXEffectType;
  position: BABYLON.Vector3;
  direction?: BABYLON.Vector3;
  intensity: number; // 0-1
  duration: number; // milliseconds
  scale: number;
  autoStart?: boolean;
}

export interface VFXEmitterInstance {
  id: string;
  type: VFXEffectType;
  emitter: BABYLON.ParticleSystem | null;
  mesh: BABYLON.AbstractMesh | null;
  light: BABYLON.Light | null;
  startTime: number;
  duration: number;
  isPlaying: boolean;
}

export class AdvancedVFXSystem {
  private static instance: AdvancedVFXSystem;
  private scene: BABYLON.Scene | null = null;
  private emitters: Map<string, VFXEmitterInstance> = new Map();
  private emitterCounter: number = 0;
  private maxEmitters: number = 50;
  private updateInterval: NodeJS.Timeout | null = null;

  private constructor() {
    console.log('✨ AdvancedVFXSystem initialized');
  }

  /**
   * الحصول على نسخة واحدة من نظام التأثيرات البصرية
   */
  static getInstance(): AdvancedVFXSystem {
    if (!AdvancedVFXSystem.instance) {
      AdvancedVFXSystem.instance = new AdvancedVFXSystem();
    }
    return AdvancedVFXSystem.instance;
  }

  /**
   * تعيين المشهد
   */
  setScene(scene: BABYLON.Scene): void {
    this.scene = scene;
    this.startUpdateLoop();
    console.log('✓ Scene assigned to AdvancedVFXSystem');
  }

  /**
   * بدء حلقة التحديث
   */
  private startUpdateLoop(): void {
    if (this.updateInterval) return;

    this.updateInterval = setInterval(() => {
      this.updateEmitters();
    }, 16); // ~60fps
  }

  /**
   * تحديث المصدرات
   */
  private updateEmitters(): void {
    const now = Date.now();
    const emittersToRemove: string[] = [];

    this.emitters.forEach((emitter, id) => {
      const elapsedTime = now - emitter.startTime;

      if (elapsedTime >= emitter.duration) {
        this.stopEmitter(id);
        emittersToRemove.push(id);
      }
    });

    emittersToRemove.forEach((id) => {
      this.emitters.delete(id);
    });
  }

  /**
   * تشغيل تأثير بصري
   */
  playEffect(config: VFXEmitterConfig): string {
    if (!this.scene) {
      console.warn('Scene not initialized in AdvancedVFXSystem');
      return '';
    }

    if (this.emitters.size >= this.maxEmitters) {
      console.warn('Max emitters reached, removing oldest');
      const firstKey = Array.from(this.emitters.keys())[0];
      if (firstKey) {
        this.stopEmitter(firstKey);
        this.emitters.delete(firstKey);
      }
    }

    const emitterId = `vfx_${this.emitterCounter++}`;
    const particleSystem = this.createParticleSystem(config, emitterId);
    const light = this.createLight(config);
    const mesh = particleSystem?.emitter as BABYLON.AbstractMesh | null;

    const emitterInstance: VFXEmitterInstance = {
      id: emitterId,
      type: config.type,
      emitter: particleSystem,
      mesh,
      light,
      startTime: Date.now(),
      duration: config.duration,
      isPlaying: true,
    };

    this.emitters.set(emitterId, emitterInstance);

    gameEvents.emit('vfx_started', {
      id: emitterId,
      type: config.type,
      position: config.position,
    });

    console.log(`✨ VFX started: ${config.type} (${emitterId})`);
    return emitterId;
  }

  /**
   * إنشاء نظام الجزيئات
   */
  private createParticleSystem(
    config: VFXEmitterConfig,
    emitterId: string
  ): BABYLON.ParticleSystem | null {
    if (!this.scene) return null;

    const particleSystem = new BABYLON.ParticleSystem(`particles_${emitterId}`, 500, this.scene);

    const emitterMesh = BABYLON.MeshBuilder.CreateSphere(
      `emitter_${emitterId}`,
      { segments: 4 },
      this.scene
    );
    emitterMesh.position = config.position;
    emitterMesh.isVisible = false;

    particleSystem.emitter = emitterMesh;

    // تكوين الجزيئات بناءً على النوع
    this.configureParticlesForType(particleSystem, config.type, config);

    // تطبيق الكثافة والمدة
    particleSystem.emitRate =
      20 * config.intensity * (config.duration / 1000);
    particleSystem.targetStopDuration = config.duration / 1000;

    particleSystem.start();

    return particleSystem;
  }

  /**
   * تكوين الجزيئات حسب النوع
   */
  private configureParticlesForType(
    system: BABYLON.ParticleSystem,
    type: VFXEffectType,
    config: VFXEmitterConfig
  ): void {
    // إعدادات عامة
    system.gravity = new BABYLON.Vector3(0, 0, 0);
    system.minEmitBox = new BABYLON.Vector3(-1, -1, -1).scale(config.scale);
    system.maxEmitBox = new BABYLON.Vector3(1, 1, 1).scale(config.scale);

    // حياة الجزيء
    system.minLifeTime = 0.2;
    system.maxLifeTime = 3.0;

    // حجم الجزيء
    system.minSize = 0.1 * config.scale;
    system.maxSize = 0.5 * config.scale;

    // السرعة
    system.minEmitPower = 1;
    system.maxEmitPower = 3;

    switch (type) {
      case 'explosion':
        this.configureExplosion(system, config);
        break;
      case 'impact':
        this.configureImpact(system, config);
        break;
      case 'spell_cast':
        this.configureSpellCast(system, config);
        break;
      case 'heal':
        this.configureHeal(system, config);
        break;
      case 'elemental_fire':
        this.configureElementalFire(system, config);
        break;
      case 'elemental_ice':
        this.configureElementalIce(system, config);
        break;
      case 'elemental_lightning':
        this.configureElementalLightning(system, config);
        break;
      case 'blood_splash':
        this.configureBloodSplash(system, config);
        break;
      case 'dust_cloud':
        this.configureDustCloud(system, config);
        break;
      default:
        this.configureDefault(system, config);
    }
  }

  /**
   * تكوين انفجار
   */
  private configureExplosion(
    system: BABYLON.ParticleSystem,
    config: VFXEmitterConfig
  ): void {
    system.minEmitPower = 5;
    system.maxEmitPower = 10;
    system.minSize = 0.3 * config.scale;
    system.maxSize = 1.0 * config.scale;
    system.minLifeTime = 0.5;
    system.maxLifeTime = 2.0;

    system.addColorGradient(0, new BABYLON.Color4(1, 0.8, 0, 1));
    system.addColorGradient(0.5, new BABYLON.Color4(1, 0.5, 0, 1));
    system.addColorGradient(1.0, new BABYLON.Color4(0.2, 0.2, 0.2, 1));
  }

  /**
   * تكوين تأثير التأثير
   */
  private configureImpact(system: BABYLON.ParticleSystem, config: VFXEmitterConfig): void {
    system.minEmitPower = 2;
    system.maxEmitPower = 4;
    system.minSize = 0.15 * config.scale;
    system.maxSize = 0.4 * config.scale;
    system.minLifeTime = 0.3;
    system.maxLifeTime = 1.5;

    system.addColorGradient(0, new BABYLON.Color4(0.8, 0.7, 0.5, 1));
  }

  /**
   * تكوين تأثير استدعاء التعويذة
   */
  private configureSpellCast(system: BABYLON.ParticleSystem, config: VFXEmitterConfig): void {
    system.minEmitPower = 3;
    system.maxEmitPower = 6;
    system.minSize = 0.2 * config.scale;
    system.maxSize = 0.6 * config.scale;
    system.gravity = new BABYLON.Vector3(0, -1, 0);

    system.addColorGradient(0, new BABYLON.Color4(0.5, 0.5, 1, 1));
    system.addColorGradient(0.5, new BABYLON.Color4(0.8, 0.8, 1, 1));
    system.addColorGradient(1.0, new BABYLON.Color4(0.3, 0.3, 0.8, 1));
  }

  /**
   * تكوين التأثير الشفائي
   */
  private configureHeal(system: BABYLON.ParticleSystem, config: VFXEmitterConfig): void {
    system.minEmitPower = 1;
    system.maxEmitPower = 3;
    system.minSize = 0.2 * config.scale;
    system.maxSize = 0.5 * config.scale;
    system.gravity = new BABYLON.Vector3(0, 2, 0);

    system.addColorGradient(0, new BABYLON.Color4(0, 1, 0.5, 1));
    system.addColorGradient(0.5, new BABYLON.Color4(0.5, 1, 0.7, 1));
    system.addColorGradient(1.0, new BABYLON.Color4(0, 0.8, 0.4, 1));
  }

  /**
   * تكوين النار العنصرية
   */
  private configureElementalFire(system: BABYLON.ParticleSystem, config: VFXEmitterConfig): void {
    system.minEmitPower = 4;
    system.maxEmitPower = 8;
    system.minSize = 0.25 * config.scale;
    system.maxSize = 0.8 * config.scale;

    system.addColorGradient(0, new BABYLON.Color4(1, 0.5, 0, 1));
    system.addColorGradient(0.5, new BABYLON.Color4(1, 0.3, 0, 1));
    system.addColorGradient(1.0, new BABYLON.Color4(0.5, 0, 0, 1));
  }

  /**
   * تكوين الثلج العنصري
   */
  private configureElementalIce(system: BABYLON.ParticleSystem, config: VFXEmitterConfig): void {
    system.minEmitPower = 2;
    system.maxEmitPower = 5;
    system.minSize = 0.15 * config.scale;
    system.maxSize = 0.4 * config.scale;
    system.gravity = new BABYLON.Vector3(0, -0.5, 0);

    system.addColorGradient(0, new BABYLON.Color4(0.7, 0.9, 1, 1));
    system.addColorGradient(0.5, new BABYLON.Color4(0.8, 0.95, 1, 1));
    system.addColorGradient(1.0, new BABYLON.Color4(0.3, 0.7, 1, 1));
  }

  /**
   * تكوين البرق العنصري
   */
  private configureElementalLightning(
    system: BABYLON.ParticleSystem,
    config: VFXEmitterConfig
  ): void {
    system.minEmitPower = 6;
    system.maxEmitPower = 10;
    system.minSize = 0.1 * config.scale;
    system.maxSize = 0.3 * config.scale;

    system.addColorGradient(0, new BABYLON.Color4(1, 1, 0.5, 1));
    system.addColorGradient(0.5, new BABYLON.Color4(0.8, 0.8, 1, 1));
    system.addColorGradient(1.0, new BABYLON.Color4(0.3, 0.3, 1, 1));
  }

  /**
   * تكوين رش الدم
   */
  private configureBloodSplash(system: BABYLON.ParticleSystem, config: VFXEmitterConfig): void {
    system.minEmitPower = 3;
    system.maxEmitPower = 6;
    system.minSize = 0.1 * config.scale;
    system.maxSize = 0.3 * config.scale;
    system.gravity = new BABYLON.Vector3(0, -5, 0);

    system.addColorGradient(0, new BABYLON.Color4(0.8, 0, 0, 1));
  }

  /**
   * تكوين سحابة الغبار
   */
  private configureDustCloud(system: BABYLON.ParticleSystem, config: VFXEmitterConfig): void {
    system.minEmitPower = 1;
    system.maxEmitPower = 3;
    system.minSize = 0.3 * config.scale;
    system.maxSize = 1.0 * config.scale;
    system.gravity = new BABYLON.Vector3(0, -0.5, 0);

    system.addColorGradient(0, new BABYLON.Color4(0.7, 0.6, 0.5, 1));
    system.addColorGradient(0.5, new BABYLON.Color4(0.8, 0.7, 0.6, 1));
    system.addColorGradient(1.0, new BABYLON.Color4(0.5, 0.5, 0.5, 1));
  }

  /**
   * تكوين افتراضي
   */
  private configureDefault(system: BABYLON.ParticleSystem, _config: VFXEmitterConfig): void {
    system.addColorGradient(0, new BABYLON.Color4(1, 1, 1, 1));
  }

  /**
   * إنشاء ضوء للتأثير
   */
  private createLight(config: VFXEmitterConfig): BABYLON.Light | null {
    if (!this.scene) return null;

    let light: BABYLON.Light | null = null;

    switch (config.type) {
      case 'explosion':
      case 'elemental_fire':
        light = new BABYLON.PointLight('light_fire', config.position, this.scene);
        (light as BABYLON.PointLight).range = 30 * config.scale;
        (light as BABYLON.PointLight).intensity = 1.5 * config.intensity;
        (light as BABYLON.PointLight).diffuse = new BABYLON.Color3(1, 0.5, 0);
        break;

      case 'spell_cast':
      case 'elemental_lightning':
        light = new BABYLON.PointLight('light_magic', config.position, this.scene);
        (light as BABYLON.PointLight).range = 25 * config.scale;
        (light as BABYLON.PointLight).intensity = 1.2 * config.intensity;
        (light as BABYLON.PointLight).diffuse = new BABYLON.Color3(0.5, 0.5, 1);
        break;

      case 'heal':
        light = new BABYLON.PointLight('light_heal', config.position, this.scene);
        (light as BABYLON.PointLight).range = 20 * config.scale;
        (light as BABYLON.PointLight).intensity = 1.0 * config.intensity;
        (light as BABYLON.PointLight).diffuse = new BABYLON.Color3(0, 1, 0.5);
        break;
    }

    return light;
  }

  /**
   * إيقاف مصدر
   */
  private stopEmitter(id: string): void {
    const emitter = this.emitters.get(id);
    if (!emitter) return;

    if (emitter.emitter) {
      emitter.emitter.stop();
      emitter.emitter.dispose();
    }

    if (emitter.light) {
      emitter.light.dispose();
    }

    if (emitter.mesh) {
      emitter.mesh.dispose();
    }

    emitter.isPlaying = false;

    gameEvents.emit('vfx_stopped', {
      id,
      type: emitter.type,
    });
  }

  /**
   * إيقاف تأثير معين
   */
  stopEffect(id: string): void {
    this.stopEmitter(id);
    this.emitters.delete(id);
  }

  /**
   * إيقاف جميع التأثيرات
   */
  stopAllEffects(): void {
    this.emitters.forEach((_emitter, id) => {
      this.stopEmitter(id);
    });
    this.emitters.clear();
  }

  /**
   * الحصول على عدد التأثيرات النشطة
   */
  getActiveEffectCount(): number {
    return this.emitters.size;
  }

  /**
   * طباعة معلومات النظام
   */
  printSystemInfo(): void {
    console.log(`
    ✨ ADVANCED VFX SYSTEM
    ─────────────────────
    Active Effects: ${this.emitters.size}/${this.maxEmitters}
    Scene: ${this.scene ? 'Initialized' : 'Not initialized'}

    Active Effect Types:
    ${
      Array.from(this.emitters.values())
        .map((e) => `  - ${e.type}`)
        .join('\n') || '  None'
    }
    ─────────────────────
    `);
  }
}

// تصدير نسخة واحدة
export const advancedVFXSystem = AdvancedVFXSystem.getInstance();
