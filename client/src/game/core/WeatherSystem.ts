/**
 * Weather System - نظام الطقس
 * إدارة الطقس والتأثيرات البيئية والدورات
 */

import * as BABYLON from 'babylonjs';
import { WeatherType, DayNightCyclePhase } from '../../types/gameTypes';
import { gameEvents } from './EventSystem';
import { gameRenderer } from './GameRenderer';

export interface WeatherState {
  type: WeatherType;
  intensity: number; // 0-1
  duration: number; // ملي ثانية
  windSpeed: number;
  windDirection: BABYLON.Vector3;
  precipitation: number; // 0-1
  visibility: number; // 0-1
}

export interface DayNightState {
  timeOfDay: number; // 0-1440 (دقائق)
  phase: DayNightCyclePhase;
  sunIntensity: number;
  sunColor: BABYLON.Color3;
  ambientColor: BABYLON.Color3;
  fogDensity: number;
}

export class WeatherSystem {
  private static instance: WeatherSystem;
  private weatherState: WeatherState;
  private dayNightState: DayNightState;
  private weatherCycle: WeatherType[] = [];
  private cycleIndex: number = 0;
  private elapsedTime: number = 0;
  private dayNightCycleSpeed: number = 1; // تسريع دورة اليوم
  private particleSystem: BABYLON.ParticleSystem | null = null;

  private constructor() {
    this.weatherState = this.getDefaultWeatherState();
    this.dayNightState = this.getDefaultDayNightState();
    this.initializeWeatherCycle();
    console.log('🌤️ WeatherSystem initialized');
  }

  /**
   * الحصول على نسخة واحدة من نظام الطقس
   */
  static getInstance(): WeatherSystem {
    if (!WeatherSystem.instance) {
      WeatherSystem.instance = new WeatherSystem();
    }
    return WeatherSystem.instance;
  }

  /**
   * تهيئة نظام الطقس
   */
  initialize(): void {
    gameEvents.subscribe('frame_update', () => this.update());
    console.log('✓ WeatherSystem initialized');
  }

  /**
   * الحصول على حالة الطقس الافتراضية
   */
  private getDefaultWeatherState(): WeatherState {
    return {
      type: 'clear',
      intensity: 0,
      duration: 600000, // 10 دقائق
      windSpeed: 0,
      windDirection: BABYLON.Vector3.Forward(),
      precipitation: 0,
      visibility: 1,
    };
  }

  /**
   * الحصول على حالة اليوم والليل الافتراضية
   */
  private getDefaultDayNightState(): DayNightState {
    return {
      timeOfDay: 360, // الصباح (6:00 صباحاً)
      phase: 'dawn',
      sunIntensity: 0.6,
      sunColor: new BABYLON.Color3(1, 0.9, 0.7),
      ambientColor: new BABYLON.Color3(0.6, 0.6, 0.7),
      fogDensity: 0,
    };
  }

  /**
   * تهيئة دورة الطقس
   */
  private initializeWeatherCycle(): void {
    this.weatherCycle = ['clear', 'cloudy', 'rain', 'thunderstorm', 'clear'];
    this.cycleIndex = 0;
  }

  /**
   * تحديث نظام الطقس والليل/النهار
   */
  private update(): void {
    const deltaTime = 0.016; // ~60fps

    // تحديث دورة اليوم والليل
    this.updateDayNightCycle(deltaTime);

    // تحديث حالة الطقس
    this.updateWeatherState(deltaTime);

    // تطبيق التأثيرات البصرية
    this.applyWeatherEffects();
    this.applyLightingEffects();
  }

  /**
   * تحديث دورة اليوم والليل
   */
  private updateDayNightCycle(deltaTime: number): void {
    // إضافة الوقت (1 دقيقة حقيقية = 60 دقيقة لعبة)
    const timeIncrement = (deltaTime * 60) * this.dayNightCycleSpeed;
    this.dayNightState.timeOfDay = (this.dayNightState.timeOfDay + timeIncrement) % 1440;

    // تحديث المرحلة
    this.updateDayNightPhase();

    // بث حدث تحديث الوقت
    if (Math.floor(timeIncrement) > 0) {
      gameEvents.emit('time_changed', {
        timeOfDay: this.dayNightState.timeOfDay,
        phase: this.dayNightState.phase,
      });
    }
  }

  /**
   * تحديث مرحلة اليوم والليل
   */
  private updateDayNightPhase(): void {
    const time = this.dayNightState.timeOfDay;

    if (time >= 0 && time < 360) {
      // الليل (0:00 - 6:00)
      this.dayNightState.phase = 'night';
      this.dayNightState.sunIntensity = 0.1;
      this.dayNightState.sunColor = new BABYLON.Color3(0.3, 0.3, 0.5);
      this.dayNightState.ambientColor = new BABYLON.Color3(0.2, 0.2, 0.3);
    } else if (time >= 360 && time < 480) {
      // الفجر (6:00 - 8:00)
      this.dayNightState.phase = 'dawn';
      const progress = (time - 360) / 120;
      this.dayNightState.sunIntensity = BABYLON.Scalar.Lerp(0.1, 0.8, progress);
      this.dayNightState.sunColor = BABYLON.Color3.Lerp(
        new BABYLON.Color3(0.3, 0.3, 0.5),
        new BABYLON.Color3(1, 0.9, 0.7),
        progress
      );
      this.dayNightState.ambientColor = BABYLON.Color3.Lerp(
        new BABYLON.Color3(0.2, 0.2, 0.3),
        new BABYLON.Color3(0.8, 0.8, 0.9),
        progress
      );
    } else if (time >= 480 && time < 1080) {
      // اليوم (8:00 - 18:00)
      this.dayNightState.phase = 'day';
      this.dayNightState.sunIntensity = 1.0;
      this.dayNightState.sunColor = new BABYLON.Color3(1, 1, 0.9);
      this.dayNightState.ambientColor = new BABYLON.Color3(0.9, 0.9, 1);
    } else if (time >= 1080 && time < 1200) {
      // الغسق (18:00 - 20:00)
      this.dayNightState.phase = 'dusk';
      const progress = (time - 1080) / 120;
      this.dayNightState.sunIntensity = BABYLON.Scalar.Lerp(1.0, 0.1, progress);
      this.dayNightState.sunColor = BABYLON.Color3.Lerp(
        new BABYLON.Color3(1, 1, 0.9),
        new BABYLON.Color3(1, 0.6, 0.3),
        progress
      );
      this.dayNightState.ambientColor = BABYLON.Color3.Lerp(
        new BABYLON.Color3(0.9, 0.9, 1),
        new BABYLON.Color3(0.4, 0.4, 0.6),
        progress
      );
    } else {
      // الليل (20:00 - 0:00)
      this.dayNightState.phase = 'night';
      this.dayNightState.sunIntensity = 0.1;
      this.dayNightState.sunColor = new BABYLON.Color3(0.3, 0.3, 0.5);
      this.dayNightState.ambientColor = new BABYLON.Color3(0.2, 0.2, 0.3);
    }
  }

  /**
   * تحديث حالة الطقس
   */
  private updateWeatherState(deltaTime: number): void {
    this.elapsedTime += deltaTime;

    // التحقق من انتهاء فترة الطقس الحالية
    if (this.elapsedTime * 1000 >= this.weatherState.duration) {
      this.elapsedTime = 0;
      this.cycleToNextWeather();
    }

    // تحديث شدة الريح
    this.weatherState.windSpeed = Math.sin(this.elapsedTime * 2) * 5 + 10;
    this.weatherState.windDirection = new BABYLON.Vector3(
      Math.cos(this.elapsedTime * 0.5),
      0,
      Math.sin(this.elapsedTime * 0.5)
    );

    // تحديث الأمطار والرطوبة حسب نوع الطقس
    switch (this.weatherState.type) {
      case 'clear':
        this.weatherState.precipitation = 0;
        this.weatherState.visibility = 1;
        break;

      case 'cloudy':
        this.weatherState.precipitation = 0;
        this.weatherState.visibility = 0.9;
        break;

      case 'rain':
        this.weatherState.precipitation = BABYLON.Scalar.Clamp(
          Math.sin(this.elapsedTime * 3) * 0.5 + 0.5,
          0,
          1
        );
        this.weatherState.visibility = 0.7;
        break;

      case 'thunderstorm':
        this.weatherState.precipitation = 1;
        this.weatherState.visibility = 0.5;
        break;

      case 'snow':
        this.weatherState.precipitation = 0.8;
        this.weatherState.visibility = 0.6;
        break;

      case 'fog':
        this.weatherState.precipitation = 0;
        this.weatherState.visibility = 0.3;
        break;
    }
  }

  /**
   * الانتقال إلى الطقس التالي في الدورة
   */
  private cycleToNextWeather(): void {
    this.cycleIndex = (this.cycleIndex + 1) % this.weatherCycle.length;
    const nextWeather = this.weatherCycle[this.cycleIndex] as WeatherType;
    this.setWeather(nextWeather, 600000);
  }

  /**
   * تعيين نوع الطقس
   */
  setWeather(type: WeatherType, duration: number = 600000): void {
    this.weatherState.type = type;
    this.weatherState.duration = duration;
    this.elapsedTime = 0;

    gameEvents.emit('weather_changed', {
      type,
      intensity: this.weatherState.intensity,
    });

    console.log(`🌤️ Weather changed to: ${type}`);
  }

  /**
   * تطبيق التأثيرات البصرية للطقس
   */
  private applyWeatherEffects(): void {
    const scene = gameRenderer.getInstance().getScene();
    if (!scene) return;

    // تحديث حالة الضباب
    if (this.weatherState.type === 'fog') {
      scene.fogEnabled = true;
      scene.fogMode = BABYLON.Scene.FOGMODE_LINEAR;
      scene.fogStart = 10;
      scene.fogEnd = 50;
      scene.fogColor = new BABYLON.Color3(0.7, 0.7, 0.75);
    } else {
      scene.fogEnabled = false;
    }

    // تحديث شفافية السماء حسب الرؤية
    const skybox = scene.meshes.find((m) => m.name === 'skybox');
    if (skybox && skybox.material) {
      (skybox.material as any).alpha = this.weatherState.visibility;
    }
  }

  /**
   * تطبيق تأثيرات الإضاءة (اليوم والليل)
   */
  private applyLightingEffects(): void {
    const renderer = gameRenderer.getInstance();
    const scene = renderer.getScene();
    if (!scene) return;

    // تحديث الضوء الرئيسي
    const mainLight = scene.lights[0];
    if (mainLight && mainLight instanceof BABYLON.DirectionalLight) {
      mainLight.intensity = this.dayNightState.sunIntensity;
      mainLight.diffuse = this.dayNightState.sunColor.clone();
    }

    // تحديث الضوء المحيطي
    const ambientLight = scene.lights[1];
    if (ambientLight && ambientLight instanceof BABYLON.HemisphericLight) {
      ambientLight.intensity = BABYLON.Scalar.Clamp(this.dayNightState.sunIntensity * 0.7, 0.3, 1);
      ambientLight.diffuse = this.dayNightState.ambientColor.clone();
    }

    // تحديث لون خلفية المشهد
    scene.clearColor = BABYLON.Color3.Lerp(
      this.dayNightState.ambientColor,
      new BABYLON.Color3(0, 0, 0.1),
      1 - this.dayNightState.sunIntensity * 0.5
    );
  }

  /**
   * الحصول على حالة الطقس الحالية
   */
  getWeatherState(): WeatherState {
    return { ...this.weatherState };
  }

  /**
   * الحصول على حالة اليوم والليل الحالية
   */
  getDayNightState(): DayNightState {
    return { ...this.dayNightState };
  }

  /**
   * الحصول على الوقت الحالي بصيغة نصية
   */
  getTimeString(): string {
    const hours = Math.floor(this.dayNightState.timeOfDay / 60);
    const minutes = Math.floor(this.dayNightState.timeOfDay % 60);
    return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`;
  }

  /**
   * تعيين سرعة دورة اليوم والليل
   */
  setDayNightCycleSpeed(speed: number): void {
    this.dayNightCycleSpeed = Math.max(0.1, speed);
    console.log(`✓ Day/Night cycle speed set to: ${speed}x`);
  }

  /**
   * تعيين الوقت مباشرة
   */
  setTimeOfDay(minutes: number): void {
    this.dayNightState.timeOfDay = Math.max(0, Math.min(1440, minutes));
    this.updateDayNightPhase();
    gameEvents.emit('time_changed', {
      timeOfDay: this.dayNightState.timeOfDay,
      phase: this.dayNightState.phase,
    });
  }

  /**
   * طباعة معلومات الطقس
   */
  printWeatherInfo(): void {
    console.log(`
    🌤️ WEATHER INFO
    ─────────────────────
    Type: ${this.weatherState.type}
    Intensity: ${(this.weatherState.intensity * 100).toFixed(1)}%
    Precipitation: ${(this.weatherState.precipitation * 100).toFixed(1)}%
    Visibility: ${(this.weatherState.visibility * 100).toFixed(1)}%
    Wind Speed: ${this.weatherState.windSpeed.toFixed(1)} m/s
    Wind Direction: [${this.weatherState.windDirection.x.toFixed(2)}, ${this.weatherState.windDirection.z.toFixed(2)}]

    Day/Night:
      Time: ${this.getTimeString()}
      Phase: ${this.dayNightState.phase}
      Sun Intensity: ${(this.dayNightState.sunIntensity * 100).toFixed(1)}%
      Sun Color: RGB(${(this.dayNightState.sunColor.r * 255).toFixed(0)}, ${(this.dayNightState.sunColor.g * 255).toFixed(0)}, ${(this.dayNightState.sunColor.b * 255).toFixed(0)})

    ─────────────────────
    `);
  }
}

// تصدير نسخة واحدة
export const weatherSystem = WeatherSystem.getInstance();
