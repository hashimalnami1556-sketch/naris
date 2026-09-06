/**
 * VFX Manager - مدير المؤثرات البصية
 * يدير المؤثرات البصية المعقدة بدمج الجسيمات والرسوم المتحركة
 */

import { Vector3, Mesh, Scene } from 'babylonjs';
import { particleSystem, ParticleType } from './ParticleSystem';
import { animationSystem } from './AnimationSystem';
import { soundSystem } from './SoundSystem';
import { gameEvents } from './EventSystem';

export type VFXType =
  | 'hit'
  | 'explosion'
  | 'heal'
  | 'buff'
  | 'debuff'
  | 'critical'
  | 'level_up'
  | 'death'
  | 'teleport';

export interface VFXConfig {
  type: VFXType;
  position: Vector3;
  targetMesh?: Mesh;
  intensity?: number;
  sound?: string;
}

interface VFXDefinition {
  particleTypes: ParticleType[];
  duration: number;
  sound?: string;
  scale?: number;
  color?: { r: number; g: number; b: number };
}

export class VFXManager {
  private static instance: VFXManager;
  private scene: Scene | null = null;
  private vfxDefinitions: Record<VFXType, VFXDefinition> = {
    hit: {
      particleTypes: ['spark', 'dust'],
      duration: 0.5,
      sound: 'hit',
      scale: 1,
    },
    explosion: {
      particleTypes: ['fire', 'spark'],
      duration: 2,
      sound: 'explosion',
      scale: 2,
    },
    heal: {
      particleTypes: ['heal'],
      duration: 1,
      sound: 'heal',
      scale: 1.5,
    },
    buff: {
      particleTypes: ['lightning'],
      duration: 1.5,
      sound: 'buff',
      scale: 1,
    },
    debuff: {
      particleTypes: ['ice'],
      duration: 1.5,
      sound: 'debuff',
      scale: 1,
    },
    critical: {
      particleTypes: ['lightning', 'spark'],
      duration: 0.8,
      sound: 'critical',
      scale: 1.5,
    },
    level_up: {
      particleTypes: ['heal', 'lightning'],
      duration: 2,
      sound: 'level_up',
      scale: 2,
    },
    death: {
      particleTypes: ['blood', 'dust'],
      duration: 2,
      sound: 'death',
      scale: 2.5,
    },
    teleport: {
      particleTypes: ['lightning', 'spark'],
      duration: 0.6,
      sound: 'teleport',
      scale: 1.8,
    },
  };

  private constructor() {
    console.log('✨ VFXManager initialized');
  }

  /**
   * الحصول على نسخة واحدة من مدير المؤثرات
   */
  static getInstance(): VFXManager {
    if (!VFXManager.instance) {
      VFXManager.instance = new VFXManager();
    }
    return VFXManager.instance;
  }

  /**
   * تعيين المشهد
   */
  setScene(scene: Scene): void {
    this.scene = scene;
    console.log('✓ Scene assigned to VFXManager');
  }

  /**
   * تشغيل مؤثر بصري
   */
  playVFX(config: VFXConfig): void {
    const vfxDef = this.vfxDefinitions[config.type];
    if (!vfxDef) {
      console.warn(`VFX type not found: ${config.type}`);
      return;
    }

    const position = config.position || new Vector3(0, 0, 0);

    // Play particles
    vfxDef.particleTypes.forEach((particleType) => {
      particleSystem.createEmitter({
        type: particleType,
        position,
        duration: vfxDef.duration,
        intensity: config.intensity || 1,
      });
    });

    // Play animation on target mesh
    if (config.targetMesh) {
      this.playTargetAnimation(config.type, config.targetMesh);
    }

    // Play sound
    if (vfxDef.sound) {
      soundSystem.playSound(vfxDef.sound, 'sfx', 0.8);
    }

    gameEvents.emit('vfx_played', {
      type: config.type,
      position,
      targetMesh: config.targetMesh?.name || 'none',
    });
  }

  /**
   * تشغيل رسم متحرك على الهدف
   */
  private playTargetAnimation(vfxType: VFXType, targetMesh: Mesh): void {
    switch (vfxType) {
      case 'hit':
        animationSystem.createShakeAnimation(targetMesh, 0.15, 0.3);
        break;
      case 'explosion':
        animationSystem.createShakeAnimation(targetMesh, 0.3, 0.6);
        break;
      case 'heal':
        animationSystem.createPulseAnimation(targetMesh, 1.15, 0.8);
        break;
      case 'buff':
        animationSystem.createPulseAnimation(targetMesh, 1.2, 1);
        break;
      case 'debuff':
        animationSystem.createShakeAnimation(targetMesh, 0.1, 0.8);
        break;
      case 'critical':
        animationSystem.createPulseAnimation(targetMesh, 1.3, 0.6);
        break;
      case 'level_up':
        animationSystem.createPulseAnimation(targetMesh, 1.4, 1.5);
        break;
      case 'death':
        animationSystem.createShakeAnimation(targetMesh, 0.5, 1);
        break;
      case 'teleport':
        animationSystem.createPulseAnimation(targetMesh, 0.5, 0.5);
        break;
    }
  }

  /**
   * تشغيل مؤثر ضربة بسيطة
   */
  playSimpleHit(position: Vector3, intensity: number = 1): void {
    this.playVFX({
      type: 'hit',
      position,
      intensity,
    });
  }

  /**
   * تشغيل مؤثر شفاء
   */
  playHeal(position: Vector3, targetMesh?: Mesh): void {
    this.playVFX({
      type: 'heal',
      position,
      targetMesh,
    });
  }

  /**
   * تشغيل مؤثر انفجار
   */
  playExplosion(position: Vector3, intensity: number = 1.5): void {
    this.playVFX({
      type: 'explosion',
      position,
      intensity,
    });
  }

  /**
   * تشغيل مؤثر حرج
   */
  playCritical(position: Vector3, targetMesh?: Mesh): void {
    this.playVFX({
      type: 'critical',
      position,
      targetMesh,
    });
  }

  /**
   * تشغيل مؤثر رفع المستوى
   */
  playLevelUp(position: Vector3, targetMesh?: Mesh): void {
    this.playVFX({
      type: 'level_up',
      position,
      targetMesh,
    });
  }

  /**
   * تشغيل مؤثر الموت
   */
  playDeath(position: Vector3, targetMesh?: Mesh): void {
    this.playVFX({
      type: 'death',
      position,
      targetMesh,
    });
  }

  /**
   * تشغيل مؤثر النقل
   */
  playTeleport(position: Vector3, targetMesh?: Mesh): void {
    this.playVFX({
      type: 'teleport',
      position,
      targetMesh,
    });
  }

  /**
   * تشغيل مؤثر تعزيز
   */
  playBuff(position: Vector3, targetMesh?: Mesh): void {
    this.playVFX({
      type: 'buff',
      position,
      targetMesh,
    });
  }

  /**
   * تشغيل مؤثر إضعاف
   */
  playDebuff(position: Vector3, targetMesh?: Mesh): void {
    this.playVFX({
      type: 'debuff',
      position,
      targetMesh,
    });
  }

  /**
   * الحصول على إحصائيات VFX
   */
  getStats() {
    const particleStats = particleSystem.getStats();
    const animationStats = animationSystem.getStats();
    return {
      particles: particleStats,
      animations: animationStats,
      vfxTypes: Object.keys(this.vfxDefinitions).length,
    };
  }

  /**
   * تنظيف جميع المؤثرات
   */
  dispose(): void {
    particleSystem.dispose();
    animationSystem.dispose();
    console.log('🗑️ VFXManager disposed');
  }
}

// تصدير نسخة واحدة
export const vfxManager = VFXManager.getInstance();
