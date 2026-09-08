/**
 * Cinematics Manager - مدير المشاهد السينمائية
 * إدارة تسلسلات الكاميرا والسينما والانتقالات بين المشاهد
 */

import * as BABYLON from 'babylonjs';
import { gameEvents } from './EventSystem';

export interface CinematicKeyframe {
  time: number;
  cameraPosition: BABYLON.Vector3;
  cameraTarget: BABYLON.Vector3;
  fov?: number;
  intensity?: number;
}

export interface CinematicSequence {
  id: string;
  name: string;
  duration: number;
  keyframes: CinematicKeyframe[];
  isPlaying: boolean;
  currentTime: number;
  loop: boolean;
}

export interface CinematicOverlay {
  id: string;
  type: 'black_bars' | 'fade' | 'text' | 'vignette';
  startTime: number;
  endTime: number;
  intensity: number;
}

export interface CinematicEvent {
  type: 'start' | 'end' | 'keyframe' | 'overlay';
  sequenceId: string;
  timestamp: number;
  data?: any;
}

export class CinematicsManager {
  private static instance: CinematicsManager;
  private scene: BABYLON.Scene | null = null;
  private camera: BABYLON.UniversalCamera | null = null;
  private cinematicSequences: Map<string, CinematicSequence> = new Map();
  private activeSequence: CinematicSequence | null = null;
  private overlays: CinematicOverlay[] = [];
  private cinematicHistory: CinematicEvent[] = [];
  private maxHistorySize: number = 100;
  private isInCinematic: boolean = false;
  private originalCameraState: {
    position: BABYLON.Vector3;
    target: BABYLON.Vector3;
    fov: number;
  } | null = null;
  private animationFrameHandle: number | null = null;

  private constructor(scene?: BABYLON.Scene, camera?: BABYLON.UniversalCamera) {
    this.scene = scene || null;
    this.camera = camera || null;
    console.log('🎬 CinematicsManager initialized');
  }

  /**
   * الحصول على نسخة واحدة من مدير السينما
   */
  static getInstance(): CinematicsManager {
    if (!CinematicsManager.instance) {
      CinematicsManager.instance = new CinematicsManager();
    }
    return CinematicsManager.instance;
  }

  /**
   * تعيين المشهد والكاميرا
   */
  setSceneAndCamera(scene: BABYLON.Scene, camera: BABYLON.UniversalCamera): void {
    this.scene = scene;
    this.camera = camera;
    console.log('✓ Scene and camera assigned to CinematicsManager');
  }

  /**
   * إنشاء تسلسل سينمائي جديد
   */
  createSequence(id: string, name: string, duration: number): CinematicSequence {
    const sequence: CinematicSequence = {
      id,
      name,
      duration,
      keyframes: [],
      isPlaying: false,
      currentTime: 0,
      loop: false,
    };

    this.cinematicSequences.set(id, sequence);
    console.log(`✓ Cinematic sequence created: ${id} (${duration}s)`);

    return sequence;
  }

  /**
   * إضافة Keyframe إلى التسلسل
   */
  addKeyframe(
    sequenceId: string,
    time: number,
    cameraPosition: BABYLON.Vector3,
    cameraTarget: BABYLON.Vector3,
    fov?: number
  ): void {
    const sequence = this.cinematicSequences.get(sequenceId);
    if (!sequence) {
      console.warn(`⚠️ Sequence not found: ${sequenceId}`);
      return;
    }

    const keyframe: CinematicKeyframe = {
      time,
      cameraPosition,
      cameraTarget,
      fov: fov || 45,
    };

    sequence.keyframes.push(keyframe);
    sequence.keyframes.sort((a, b) => a.time - b.time);

    console.log(
      `✓ Keyframe added to ${sequenceId} at ${time}s [${cameraPosition.x.toFixed(1)}, ${cameraPosition.y.toFixed(1)}, ${cameraPosition.z.toFixed(1)}]`
    );
  }

  /**
   * تشغيل التسلسل السينمائي
   */
  playSequence(sequenceId: string, loop: boolean = false): boolean {
    if (!this.scene || !this.camera) {
      console.warn('⚠️ Scene or camera not initialized');
      return false;
    }

    const sequence = this.cinematicSequences.get(sequenceId);
    if (!sequence) {
      console.warn(`⚠️ Sequence not found: ${sequenceId}`);
      return false;
    }

    if (sequence.keyframes.length < 2) {
      console.warn(`⚠️ Sequence needs at least 2 keyframes: ${sequenceId}`);
      return false;
    }

    // Save original camera state
    this.originalCameraState = {
      position: this.camera.position.clone(),
      target: this.camera.target.clone(),
      fov: this.camera.fov,
    };

    this.activeSequence = sequence;
    sequence.isPlaying = true;
    sequence.currentTime = 0;
    sequence.loop = loop;
    this.isInCinematic = true;

    // Emit cinematic start event
    gameEvents.emit('cinematic_started', {
      sequenceId,
      duration: sequence.duration,
      name: sequence.name,
    });

    this.recordCinematicEvent({
      type: 'start',
      sequenceId,
      timestamp: Date.now(),
    });

    // Start animation loop
    this.playSequenceFrame();

    console.log(`🎬 Cinematic sequence started: ${sequence.name}`);
    return true;
  }

  /**
   * تحديث إطار التسلسل السينمائي
   */
  private playSequenceFrame(): void {
    if (!this.activeSequence || !this.camera || !this.scene) return;

    const sequence = this.activeSequence;
    const deltaTime = 16.67 / 1000; // ~60fps

    sequence.currentTime += deltaTime;

    // Check if sequence is finished
    if (sequence.currentTime >= sequence.duration) {
      if (sequence.loop) {
        sequence.currentTime = 0;
      } else {
        this.stopSequence();
        return;
      }
    }

    // Find surrounding keyframes for interpolation
    const keyframes = sequence.keyframes;
    let keyframe1 = keyframes[0];
    let keyframe2 = keyframes[keyframes.length - 1];

    for (let i = 0; i < keyframes.length - 1; i++) {
      if (
        sequence.currentTime >= keyframes[i].time &&
        sequence.currentTime <= keyframes[i + 1].time
      ) {
        keyframe1 = keyframes[i];
        keyframe2 = keyframes[i + 1];
        break;
      }
    }

    // Calculate interpolation factor
    const timeDiff = keyframe2.time - keyframe1.time;
    const t = timeDiff > 0 ? (sequence.currentTime - keyframe1.time) / timeDiff : 0;
    const smoothT = this.easeInOutCubic(t);

    // Interpolate camera position and target
    const interpolatedPosition = BABYLON.Vector3.Lerp(
      keyframe1.cameraPosition,
      keyframe2.cameraPosition,
      smoothT
    );

    const interpolatedTarget = BABYLON.Vector3.Lerp(
      keyframe1.cameraTarget,
      keyframe2.cameraTarget,
      smoothT
    );

    const interpolatedFov = keyframe1.fov && keyframe2.fov
      ? keyframe1.fov + (keyframe2.fov - keyframe1.fov) * smoothT
      : this.camera.fov;

    // Apply camera updates
    this.camera.position = interpolatedPosition;
    this.camera.target = interpolatedTarget;
    this.camera.fov = interpolatedFov;

    // Continue animation loop
    this.animationFrameHandle = requestAnimationFrame(() => this.playSequenceFrame());
  }

  /**
   * دالة easing: Ease In-Out Cubic
   */
  private easeInOutCubic(t: number): number {
    return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
  }

  /**
   * إيقاف التسلسل السينمائي
   */
  stopSequence(): void {
    if (!this.activeSequence) return;

    this.activeSequence.isPlaying = false;

    if (this.animationFrameHandle !== null) {
      cancelAnimationFrame(this.animationFrameHandle);
      this.animationFrameHandle = null;
    }

    // Restore original camera state
    if (this.camera && this.originalCameraState) {
      this.camera.position = this.originalCameraState.position;
      this.camera.target = this.originalCameraState.target;
      this.camera.fov = this.originalCameraState.fov;
    }

    const sequenceId = this.activeSequence.id;

    gameEvents.emit('cinematic_ended', {
      sequenceId,
      duration: this.activeSequence.duration,
    });

    this.recordCinematicEvent({
      type: 'end',
      sequenceId,
      timestamp: Date.now(),
    });

    this.activeSequence = null;
    this.isInCinematic = false;

    console.log(`✓ Cinematic sequence stopped: ${sequenceId}`);
  }

  /**
   * توقيف مؤقت للتسلسل
   */
  pauseSequence(): void {
    if (this.activeSequence) {
      this.activeSequence.isPlaying = false;
      if (this.animationFrameHandle !== null) {
        cancelAnimationFrame(this.animationFrameHandle);
        this.animationFrameHandle = null;
      }
      gameEvents.emit('cinematic_paused', {
        sequenceId: this.activeSequence.id,
      });
      console.log('⏸️ Cinematic paused');
    }
  }

  /**
   * استئناف التسلسل المتوقف
   */
  resumeSequence(): void {
    if (this.activeSequence && !this.activeSequence.isPlaying) {
      this.activeSequence.isPlaying = true;
      this.playSequenceFrame();
      gameEvents.emit('cinematic_resumed', {
        sequenceId: this.activeSequence.id,
      });
      console.log('▶️ Cinematic resumed');
    }
  }

  /**
   * إضافة overlay سينمائي
   */
  addOverlay(
    type: CinematicOverlay['type'],
    startTime: number,
    endTime: number,
    intensity: number = 1.0
  ): string {
    const overlay: CinematicOverlay = {
      id: `overlay_${type}_${Date.now()}`,
      type,
      startTime,
      endTime,
      intensity,
    };

    this.overlays.push(overlay);
    console.log(`✓ Overlay added: ${type} (${startTime}s - ${endTime}s)`);

    return overlay.id;
  }

  /**
   * إزالة overlay
   */
  removeOverlay(overlayId: string): void {
    this.overlays = this.overlays.filter((o) => o.id !== overlayId);
    console.log(`✓ Overlay removed: ${overlayId}`);
  }

  /**
   * عرض شاشة سوداء (Black Fade)
   */
  showBlackFade(duration: number = 1.0): void {
    this.addOverlay('fade', 0, duration, 1.0);
    gameEvents.emit('cinematic_fade', {
      type: 'black',
      duration,
    });
    console.log(`🌑 Black fade started (${duration}s)`);
  }

  /**
   * عرض شريط سينمائي (Cinematic Bars)
   */
  showCinematicBars(intensity: number = 0.15): void {
    gameEvents.emit('cinematic_bars_show', {
      topIntensity: intensity,
      bottomIntensity: intensity,
    });
    console.log(`📹 Cinematic bars shown (${(intensity * 100).toFixed(0)}%)`);
  }

  /**
   * إخفاء شريط سينمائي
   */
  hideCinematicBars(): void {
    gameEvents.emit('cinematic_bars_hide', {});
    console.log('📹 Cinematic bars hidden');
  }

  /**
   * عرض نص سينمائي (Cinematic Text)
   */
  showCinematicText(text: string, duration: number = 3.0, position: 'top' | 'center' | 'bottom' = 'bottom'): void {
    gameEvents.emit('cinematic_text_show', {
      text,
      duration,
      position,
    });
    console.log(`📝 Cinematic text shown: "${text}"`);
  }

  /**
   * تسجيل حدث سينمائي
   */
  private recordCinematicEvent(event: CinematicEvent): void {
    this.cinematicHistory.push(event);

    if (this.cinematicHistory.length > this.maxHistorySize) {
      this.cinematicHistory.shift();
    }
  }

  /**
   * الحصول على حالة السينما الحالية
   */
  isPlayingCinematic(): boolean {
    return this.isInCinematic;
  }

  /**
   * الحصول على التسلسل النشط
   */
  getActiveSequence(): CinematicSequence | null {
    return this.activeSequence ? { ...this.activeSequence } : null;
  }

  /**
   * الحصول على سجل السينما
   */
  getCinematicHistory(limit: number = 20): CinematicEvent[] {
    return this.cinematicHistory.slice(-limit);
  }

  /**
   * إنشاء تسلسل entry-level (دخول المرحلة)
   */
  createLevelEntrySequence(
    sequenceId: string,
    startPosition: BABYLON.Vector3,
    endPosition: BABYLON.Vector3,
    targetPosition: BABYLON.Vector3,
    duration: number = 3.0
  ): void {
    this.createSequence(sequenceId, `Level Entry: ${sequenceId}`, duration);

    // Add keyframes for smooth entry
    this.addKeyframe(sequenceId, 0, startPosition, targetPosition, 30);
    this.addKeyframe(sequenceId, duration * 0.5, startPosition, targetPosition, 40);
    this.addKeyframe(sequenceId, duration, endPosition, targetPosition, 50);

    console.log(`✓ Level entry sequence created: ${sequenceId}`);
  }

  /**
   * إنشاء تسلسل boss encounter
   */
  createBossEncounterSequence(
    sequenceId: string,
    bossPosition: BABYLON.Vector3,
    duration: number = 4.0
  ): void {
    this.createSequence(
      sequenceId,
      `Boss Encounter: ${sequenceId}`,
      duration
    );

    // Create dramatic reveal sequence
    const cameraStart = new BABYLON.Vector3(
      bossPosition.x - 15,
      bossPosition.y + 10,
      bossPosition.z + 20
    );
    const cameraMiddle = new BABYLON.Vector3(
      bossPosition.x,
      bossPosition.y + 8,
      bossPosition.z + 15
    );
    const cameraEnd = new BABYLON.Vector3(
      bossPosition.x + 5,
      bossPosition.y + 5,
      bossPosition.z + 8
    );

    this.addKeyframe(sequenceId, 0, cameraStart, bossPosition, 35);
    this.addKeyframe(sequenceId, duration * 0.5, cameraMiddle, bossPosition, 45);
    this.addKeyframe(sequenceId, duration, cameraEnd, bossPosition, 50);

    console.log(`✓ Boss encounter sequence created: ${sequenceId}`);
  }

  /**
   * إنشاء تسلصل انتصار
   */
  createVictorySequence(
    sequenceId: string,
    victoryPosition: BABYLON.Vector3,
    duration: number = 3.0
  ): void {
    this.createSequence(
      sequenceId,
      `Victory: ${sequenceId}`,
      duration
    );

    const cameraStart = new BABYLON.Vector3(
      victoryPosition.x - 10,
      victoryPosition.y + 3,
      victoryPosition.z + 10
    );
    const cameraEnd = new BABYLON.Vector3(
      victoryPosition.x + 5,
      victoryPosition.y + 5,
      victoryPosition.z - 5
    );

    this.addKeyframe(sequenceId, 0, cameraStart, victoryPosition, 40);
    this.addKeyframe(sequenceId, duration, cameraEnd, victoryPosition, 50);

    console.log(`✓ Victory sequence created: ${sequenceId}`);
  }

  /**
   * طباعة معلومات السينما
   */
  printCinematicsInfo(): void {
    console.log(`
    🎬 CINEMATICS MANAGER STATUS
    ─────────────────────
    Is In Cinematic: ${this.isInCinematic}
    Active Sequence: ${this.activeSequence?.name || 'None'}
    Total Sequences: ${this.cinematicSequences.size}
    Active Overlays: ${this.overlays.length}
    History Events: ${this.cinematicHistory.length}

    Sequences:
    ${Array.from(this.cinematicSequences.values())
      .map((s) => `  - ${s.name} (${s.duration}s, ${s.keyframes.length} keyframes)`)
      .join('\n')}
    ─────────────────────
    `);
  }

  /**
   * تنظيف مدير السينما
   */
  cleanup(): void {
    this.stopSequence();
    this.cinematicSequences.clear();
    this.overlays = [];
    this.cinematicHistory = [];
    console.log('✓ CinematicsManager cleaned up');
  }
}

// تصدير نسخة واحدة
export const cinematicsManager = CinematicsManager.getInstance();
