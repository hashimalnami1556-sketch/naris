/**
 * Animation System - نظام الرسوم المتحركة
 * إدارة تحريك الشخصيات والعناصر
 */

import { Scene, Animation, AnimationGroup, Mesh } from 'babylonjs';
import { gameEvents } from './EventSystem';

export type AnimationState = 'idle' | 'walk' | 'run' | 'attack' | 'ability' | 'hit' | 'death' | 'jump';

export interface AnimationConfig {
  target: Mesh;
  property: string;
  frames: number;
  duration: number;
  loopMode?: number;
  easing?: (x: number) => number;
}

export class AnimationSystem {
  private static instance: AnimationSystem;
  private scene: Scene | null = null;
  private animationGroups: Map<string, AnimationGroup> = new Map();
  private characterAnimations: Map<string, Map<AnimationState, AnimationGroup>> = new Map();

  private constructor() {
    console.log('🎬 AnimationSystem initialized');
  }

  /**
   * الحصول على نسخة واحدة من نظام الرسوم المتحركة
   */
  static getInstance(): AnimationSystem {
    if (!AnimationSystem.instance) {
      AnimationSystem.instance = new AnimationSystem();
    }
    return AnimationSystem.instance;
  }

  /**
   * تعيين المشهد
   */
  setScene(scene: Scene): void {
    this.scene = scene;
    console.log('✓ Scene assigned to AnimationSystem');
  }

  /**
   * إنشاء رسم متحرك
   */
  createAnimation(config: AnimationConfig): Animation {
    const animation = new Animation(
      `anim_${config.property}`,
      config.property,
      config.frames,
      Animation.ANIMATIONTYPE_FLOAT,
      config.loopMode || Animation.LOOPMODE_CYCLE
    );

    // Add simple key frames
    animation.setKeys([
      { frame: 0, value: 0 },
      { frame: config.frames, value: 1 },
    ]);

    config.target.animations.push(animation);
    return animation;
  }

  /**
   * تشغيل رسم متحرك
   */
  playAnimation(target: Mesh, animationName: string): void {
    if (!this.scene) return;

    const animation = target.animations.find((a) => a.name === animationName);
    if (animation) {
      this.scene.beginAnimation(target, 0, animation.getHighestFrame(), true);
      gameEvents.emit('animation_started', { target: target.name, animation: animationName });
    }
  }

  /**
   * توقيف الرسم المتحرك
   */
  stopAnimation(target: Mesh): void {
    if (!this.scene) return;
    this.scene.stopAnimation(target);
    gameEvents.emit('animation_stopped', { target: target.name });
  }

  /**
   * إنشاء رسم متحرك للسقوط
   */
  createFallAnimation(target: Mesh, fallHeight: number, duration: number): void {
    if (!this.scene) return;

    const keys = [
      { frame: 0, value: 0 },
      { frame: duration * 60, value: fallHeight },
    ];

    const fallAnimation = new Animation(
      'fall',
      'position.y',
      60,
      Animation.ANIMATIONTYPE_FLOAT,
      Animation.LOOPMODE_CLAMP
    );

    fallAnimation.setKeys(keys);
    target.animations.push(fallAnimation);
    this.scene.beginAnimation(target, 0, duration * 60, false);
  }

  /**
   * إنشاء رسم متحرك للقفز
   */
  createJumpAnimation(target: Mesh, jumpHeight: number, duration: number): void {
    if (!this.scene) return;

    const totalFrames = duration * 60;
    const keys = [
      { frame: 0, value: target.position.y },
      { frame: totalFrames / 2, value: target.position.y + jumpHeight },
      { frame: totalFrames, value: target.position.y },
    ];

    const jumpAnimation = new Animation(
      'jump',
      'position.y',
      60,
      Animation.ANIMATIONTYPE_FLOAT,
      Animation.LOOPMODE_CLAMP
    );

    jumpAnimation.setKeys(keys);
    target.animations.push(jumpAnimation);
    this.scene.beginAnimation(target, 0, totalFrames, false);

    gameEvents.emit('jump_animation_started', { target: target.name });
  }

  /**
   * إنشاء رسم متحرك للدوران
   */
  createRotationAnimation(target: Mesh, rotationAmount: number, duration: number): void {
    if (!this.scene) return;

    const totalFrames = duration * 60;
    const keys = [
      { frame: 0, value: 0 },
      { frame: totalFrames, value: rotationAmount },
    ];

    const rotationAnimation = new Animation(
      'rotation',
      'rotation.y',
      60,
      Animation.ANIMATIONTYPE_FLOAT,
      Animation.LOOPMODE_CLAMP
    );

    rotationAnimation.setKeys(keys);
    target.animations.push(rotationAnimation);
    this.scene.beginAnimation(target, 0, totalFrames, false);
  }

  /**
   * إنشاء رسم متحرك للتوهج
   */
  createPulseAnimation(target: Mesh, pulseIntensity: number = 1.2, duration: number = 0.5): void {
    if (!this.scene) return;

    const totalFrames = duration * 60;
    const originalScale = target.scaling.x;

    const keys = [
      { frame: 0, value: originalScale },
      { frame: totalFrames / 2, value: originalScale * pulseIntensity },
      { frame: totalFrames, value: originalScale },
    ];

    const pulseAnimation = new Animation(
      'pulse',
      'scaling.x',
      60,
      Animation.ANIMATIONTYPE_FLOAT,
      Animation.LOOPMODE_CLAMP
    );

    pulseAnimation.setKeys(keys);
    target.animations.push(pulseAnimation);

    const pulseAnimY = new Animation(
      'pulseY',
      'scaling.y',
      60,
      Animation.ANIMATIONTYPE_FLOAT,
      Animation.LOOPMODE_CLAMP
    );
    pulseAnimY.setKeys(keys);
    target.animations.push(pulseAnimY);

    const pulseAnimZ = new Animation(
      'pulseZ',
      'scaling.z',
      60,
      Animation.ANIMATIONTYPE_FLOAT,
      Animation.LOOPMODE_CLAMP
    );
    pulseAnimZ.setKeys(keys);
    target.animations.push(pulseAnimZ);

    this.scene.beginAnimation(target, 0, totalFrames, false);
  }

  /**
   * إنشاء رسم متحرك للاهتزاز (shake)
   */
  createShakeAnimation(target: Mesh, shakeAmount: number = 0.1, duration: number = 0.3): void {
    if (!this.scene) return;

    const totalFrames = duration * 60;
    const originalX = target.position.x;
    const originalY = target.position.y;

    const xKeys = [];
    const yKeys = [];

    for (let i = 0; i <= totalFrames; i++) {
      const t = i / totalFrames;
      const shakeX = (Math.random() - 0.5) * shakeAmount * (1 - t); // Decay over time
      const shakeY = (Math.random() - 0.5) * shakeAmount * (1 - t);

      xKeys.push({ frame: i, value: originalX + shakeX });
      yKeys.push({ frame: i, value: originalY + shakeY });
    }

    const shakeXAnimation = new Animation(
      'shakeX',
      'position.x',
      60,
      Animation.ANIMATIONTYPE_FLOAT,
      Animation.LOOPMODE_CLAMP
    );
    shakeXAnimation.setKeys(xKeys);
    target.animations.push(shakeXAnimation);

    const shakeYAnimation = new Animation(
      'shakeY',
      'position.y',
      60,
      Animation.ANIMATIONTYPE_FLOAT,
      Animation.LOOPMODE_CLAMP
    );
    shakeYAnimation.setKeys(yKeys);
    target.animations.push(shakeYAnimation);

    this.scene.beginAnimation(target, 0, totalFrames, false);
  }

  /**
   * إنشاء رسم متحرك للانجراف (drift)
   */
  createDriftAnimation(target: Mesh, driftDirection: number, duration: number = 1): void {
    if (!this.scene) return;

    const totalFrames = duration * 60;
    const driftDistance = 2; // units

    const keys = [
      { frame: 0, value: target.position.x },
      { frame: totalFrames, value: target.position.x + driftDistance * Math.cos(driftDirection) },
    ];

    const driftXAnimation = new Animation(
      'driftX',
      'position.x',
      60,
      Animation.ANIMATIONTYPE_FLOAT,
      Animation.LOOPMODE_CLAMP
    );
    driftXAnimation.setKeys(keys);
    target.animations.push(driftXAnimation);

    const driftZKeys = [
      { frame: 0, value: target.position.z },
      { frame: totalFrames, value: target.position.z + driftDistance * Math.sin(driftDirection) },
    ];

    const driftZAnimation = new Animation(
      'driftZ',
      'position.z',
      60,
      Animation.ANIMATIONTYPE_FLOAT,
      Animation.LOOPMODE_CLAMP
    );
    driftZAnimation.setKeys(driftZKeys);
    target.animations.push(driftZAnimation);

    this.scene.beginAnimation(target, 0, totalFrames, false);
  }

  /**
   * الحصول على إحصائيات الرسوم المتحركة
   */
  getStats(): { animationGroups: number; characterAnimations: number } {
    return {
      animationGroups: this.animationGroups.size,
      characterAnimations: this.characterAnimations.size,
    };
  }

  /**
   * تنظيف جميع الرسوم المتحركة
   */
  dispose(): void {
    this.animationGroups.forEach((group) => group.dispose());
    this.animationGroups.clear();
    this.characterAnimations.clear();
    console.log('🗑️ AnimationSystem disposed');
  }
}

// تصدير نسخة واحدة
export const animationSystem = AnimationSystem.getInstance();
