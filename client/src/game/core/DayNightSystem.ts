/**
 * Day/Night System - نظام الليل والنهار
 * محاكاة دورة اليوم والليل مع تغيير الإضاءة
 */

import { EventSystem, gameEvents } from './EventSystem';

export type TimeOfDay = 'dawn' | 'morning' | 'noon' | 'evening' | 'dusk' | 'night' | 'midnight';

export interface TimeConfig {
  dayDuration: number; // ms
  nightDuration: number; // ms
  transitionDuration: number; // ms
}

export class DayNightSystem {
  private static instance: DayNightSystem;
  private currentTime: number = 0; // 0-1 (0 = midnight, 0.5 = noon)
  private isEnabled: boolean = false;
  private timeOfDay: TimeOfDay = 'midnight';
  private config: TimeConfig = {
    dayDuration: 300000, // 5 minutes
    nightDuration: 300000, // 5 minutes
    transitionDuration: 30000, // 30 seconds
  };
  private updateInterval: NodeJS.Timeout | null = null;

  private constructor() {}

  static getInstance(): DayNightSystem {
    if (!DayNightSystem.instance) {
      DayNightSystem.instance = new DayNightSystem();
    }
    return DayNightSystem.instance;
  }

  /**
   * تشغيل النظام
   */
  enable(): void {
    if (this.isEnabled) return;

    this.isEnabled = true;
    this.startCycle();

    gameEvents.emit('day_night_system_enabled', {});
    console.log('✓ Day/Night System enabled');
  }

  /**
   * إيقاف النظام
   */
  disable(): void {
    if (!this.isEnabled) return;

    this.isEnabled = false;
    if (this.updateInterval) {
      clearInterval(this.updateInterval);
      this.updateInterval = null;
    }

    gameEvents.emit('day_night_system_disabled', {});
    console.log('✓ Day/Night System disabled');
  }

  /**
   * بدء الدورة
   */
  private startCycle(): void {
    const fullCycle = this.config.dayDuration + this.config.nightDuration;

    this.updateInterval = setInterval(() => {
      this.currentTime = (this.currentTime + 0.01) % 1;

      const newTimeOfDay = this.getTimeOfDay(this.currentTime);
      if (newTimeOfDay !== this.timeOfDay) {
        this.timeOfDay = newTimeOfDay;

        gameEvents.emit('time_of_day_changed', {
          timeOfDay: this.timeOfDay,
          time: this.currentTime,
        });
      }

      gameEvents.emit('game_time_updated', {
        time: this.currentTime,
        timeOfDay: this.timeOfDay,
      });
    }, 100);
  }

  /**
   * تحديد وقت اليوم من القيمة الرقمية
   */
  private getTimeOfDay(time: number): TimeOfDay {
    if (time >= 0 && time < 0.1) return 'midnight';
    if (time >= 0.1 && time < 0.2) return 'dawn';
    if (time >= 0.2 && time < 0.4) return 'morning';
    if (time >= 0.4 && time < 0.5) return 'noon';
    if (time >= 0.5 && time < 0.7) return 'evening';
    if (time >= 0.7 && time < 0.8) return 'dusk';
    return 'night';
  }

  /**
   * الحصول على وقت اليوم الحالي
   */
  getCurrentTimeOfDay(): TimeOfDay {
    return this.timeOfDay;
  }

  /**
   * الحصول على الوقت كنسبة (0-1)
   */
  getTimeAsRatio(): number {
    return this.currentTime;
  }

  /**
   * تعيين الوقت
   */
  setTime(time: number): void {
    this.currentTime = Math.max(0, Math.min(1, time));
    this.timeOfDay = this.getTimeOfDay(this.currentTime);

    gameEvents.emit('game_time_set', {
      time: this.currentTime,
      timeOfDay: this.timeOfDay,
    });
  }

  /**
   * تقدم الوقت
   */
  advanceTime(amount: number): void {
    this.currentTime = (this.currentTime + amount) % 1;
    this.timeOfDay = this.getTimeOfDay(this.currentTime);

    gameEvents.emit('game_time_advanced', {
      time: this.currentTime,
      timeOfDay: this.timeOfDay,
    });
  }

  /**
   * هل هو نهار
   */
  isDay(): boolean {
    return this.currentTime >= 0.25 && this.currentTime < 0.75;
  }

  /**
   * هل هو ليل
   */
  isNight(): boolean {
    return !this.isDay();
  }

  /**
   * شدة الإضاءة
   */
  getLightIntensity(): number {
    if (this.currentTime >= 0.2 && this.currentTime < 0.8) {
      // نهار
      return 1;
    } else if (this.currentTime >= 0.1 && this.currentTime < 0.2) {
      // الفجر
      return (this.currentTime - 0.1) / 0.1;
    } else if (this.currentTime >= 0.8 && this.currentTime < 0.9) {
      // الغسق
      return 1 - (this.currentTime - 0.8) / 0.1;
    } else {
      // ليل
      return 0.2;
    }
  }

  /**
   * تعيين إعدادات الدورة
   */
  setConfig(config: Partial<TimeConfig>): void {
    this.config = { ...this.config, ...config };
  }
}

export const dayNightSystem = DayNightSystem.getInstance();
