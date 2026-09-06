/**
 * Environment Director - مدير البيئة
 * التحكم في انتقالات البيئات والمؤثرات البصرية
 */

import { EventSystem, gameEvents } from './EventSystem';
import { WorldManager, worldManager } from './WorldManager';

export interface EnvironmentPreset {
  id: string;
  name: string;
  worldId: string;
  lighting: {
    ambientColor: { r: number; g: number; b: number };
    ambientIntensity: number;
    sunAngle: number;
    sunIntensity: number;
  };
  effects: {
    fogColor: { r: number; g: number; b: number };
    fogDensity: number;
    particleIntensity: number;
  };
  transitionDuration: number; // ms
}

export class EnvironmentDirector {
  private static instance: EnvironmentDirector;
  private presets: Map<string, EnvironmentPreset> = new Map();
  private currentPresetId: string | null = null;
  private isTransitioning: boolean = false;
  private transitionProgress: number = 0;

  private constructor() {}

  static getInstance(): EnvironmentDirector {
    if (!EnvironmentDirector.instance) {
      EnvironmentDirector.instance = new EnvironmentDirector();
    }
    return EnvironmentDirector.instance;
  }

  /**
   * تسجيل إعدادات مسبقة
   */
  registerPreset(preset: EnvironmentPreset): void {
    this.presets.set(preset.id, preset);
  }

  /**
   * الانتقال إلى إعدادات مسبقة
   */
  transitionToPreset(presetId: string): boolean {
    const preset = this.presets.get(presetId);
    if (!preset) return false;

    if (this.isTransitioning) {
      console.warn('Transition already in progress');
      return false;
    }

    this.isTransitioning = true;
    this.transitionProgress = 0;
    this.currentPresetId = presetId;

    gameEvents.emit('environment_transition_started', {
      presetId,
      duration: preset.transitionDuration,
    });

    // محاكاة الانتقال
    const steps = 10;
    const stepDuration = preset.transitionDuration / steps;

    let step = 0;
    const interval = setInterval(() => {
      step++;
      this.transitionProgress = (step / steps) * 100;

      gameEvents.emit('environment_transition_progress', {
        progress: this.transitionProgress,
        preset,
      });

      if (step >= steps) {
        clearInterval(interval);
        this.isTransitioning = false;
        this.transitionProgress = 100;

        gameEvents.emit('environment_transition_completed', { presetId });
        console.log(`✓ Environment transition completed: ${preset.name}`);
      }
    }, stepDuration);

    return true;
  }

  /**
   * الحصول على الإعداد الحالي
   */
  getCurrentPreset(): EnvironmentPreset | null {
    return this.currentPresetId ? this.presets.get(this.currentPresetId) || null : null;
  }

  /**
   * الحصول على إعداد مسبق
   */
  getPreset(presetId: string): EnvironmentPreset | undefined {
    return this.presets.get(presetId);
  }

  /**
   * جميع الإعدادات المسبقة
   */
  getAllPresets(): EnvironmentPreset[] {
    return Array.from(this.presets.values());
  }

  /**
   * هل نحن في انتقال
   */
  isTransitionActive(): boolean {
    return this.isTransitioning;
  }

  /**
   * تقدم الانتقال
   */
  getTransitionProgress(): number {
    return this.transitionProgress;
  }

  /**
   * تطبيق فلتر بيئي
   */
  applyEnvironmentFilter(filterId: string): void {
    gameEvents.emit('environment_filter_applied', { filterId });
    console.log(`✓ Environment filter applied: ${filterId}`);
  }

  /**
   * إزالة فلتر بيئي
   */
  removeEnvironmentFilter(filterId: string): void {
    gameEvents.emit('environment_filter_removed', { filterId });
    console.log(`✓ Environment filter removed: ${filterId}`);
  }
}

export const environmentDirector = EnvironmentDirector.getInstance();
