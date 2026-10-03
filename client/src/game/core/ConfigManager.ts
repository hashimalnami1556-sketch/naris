/**
 * Config Manager - مدير التكوين
 * إدارة الإعدادات والتكوينات المختلفة للعبة
 */

import { AppConfig, DebugSettings, RenderSettings } from '../../types/gameTypes';

export class ConfigManager {
  private static instance: ConfigManager;
  private config: AppConfig;

  private constructor() {
    this.config = this.loadConfig();
    console.log('⚙️ ConfigManager initialized');
  }

  /**
   * الحصول على نسخة واحدة من مدير التكوين
   */
  static getInstance(): ConfigManager {
    if (!ConfigManager.instance) {
      ConfigManager.instance = new ConfigManager();
    }
    return ConfigManager.instance;
  }

  /**
   * تحميل التكوين من localStorage أو استخدام الافتراضي
   */
  private loadConfig(): AppConfig {
    const stored = localStorage.getItem('narsis_config');
    if (stored) {
      try {
        return JSON.parse(stored);
      } catch (error) {
        console.error('Failed to load config from localStorage', error);
      }
    }

    // التكوين الافتراضي
    return {
      version: '1.0.0',
      buildDate: new Date().toISOString(),
      environment: 'development',
      debug: true,
      debugSettings: this.getDefaultDebugSettings(),
      renderSettings: this.getDefaultRenderSettings(),
      audioEnabled: true,
      maxFrameRate: 144,
      targetFrameRate: 60,
      useWorkers: true,
    };
  }

  /**
   * الحصول على إعدادات التصحيح الافتراضية
   */
  private getDefaultDebugSettings(): DebugSettings {
    return {
      showBounds: false,
      showColliders: false,
      showPerformance: false,
      showLights: false,
      showCamera: false,
      pauseAI: false,
      infiniteEnergy: false,
      instantAbilities: false,
    };
  }

  /**
   * الحصول على إعدادات الرسومات الافتراضية
   */
  private getDefaultRenderSettings(): RenderSettings {
    const width = window.innerWidth;
    const height = window.innerHeight;

    return {
      resolution: { x: width, y: height },
      dpi: window.devicePixelRatio,
      targetFPS: 60,
      vSync: true,
      shadowQuality: 'high',
      particleQuality: 'high',
      textureQuality: 'high',
    };
  }

  /**
   * الحصول على التكوين الكامل
   */
  getConfig(): AppConfig {
    return { ...this.config };
  }

  /**
   * تحديث التكوين
   */
  updateConfig(updates: Partial<AppConfig>): void {
    this.config = {
      ...this.config,
      ...updates,
    };
    this.saveConfig();
    console.log('✓ Config updated');
  }

  /**
   * حفظ التكوين في localStorage
   */
  private saveConfig(): void {
    try {
      localStorage.setItem('narsis_config', JSON.stringify(this.config));
    } catch (error) {
      console.error('Failed to save config to localStorage', error);
    }
  }

  /**
   * تحديث إعدادات التصحيح
   */
  updateDebugSettings(updates: Partial<DebugSettings>): void {
    this.config.debugSettings = {
      ...this.config.debugSettings,
      ...updates,
    };
    this.saveConfig();
    console.log('✓ Debug settings updated');
  }

  /**
   * الحصول على إعدادات التصحيح
   */
  getDebugSettings(): DebugSettings {
    return { ...this.config.debugSettings };
  }

  /**
   * تحديث إعدادات الرسومات
   */
  updateRenderSettings(updates: Partial<RenderSettings>): void {
    this.config.renderSettings = {
      ...this.config.renderSettings,
      ...updates,
    };
    this.saveConfig();
    console.log('✓ Render settings updated');
  }

  /**
   * الحصول على إعدادات الرسومات
   */
  getRenderSettings(): RenderSettings {
    return { ...this.config.renderSettings };
  }

  /**
   * تعيين بيئة التشغيل
   */
  setEnvironment(env: 'development' | 'staging' | 'production'): void {
    this.config.environment = env;
    this.saveConfig();
    console.log(`✓ Environment set to: ${env}`);
  }

  /**
   * الحصول على بيئة التشغيل
   */
  getEnvironment(): 'development' | 'staging' | 'production' {
    return this.config.environment;
  }

  /**
   * فعّل/عطّل وضع التصحيح
   */
  setDebugMode(enabled: boolean): void {
    this.config.debug = enabled;
    this.saveConfig();
    console.log(`✓ Debug mode: ${enabled ? 'ON' : 'OFF'}`);
  }

  /**
   * فحص وضع التصحيح
   */
  isDebugMode(): boolean {
    return this.config.debug;
  }

  /**
   * تفعيل/تعطيل الصوت
   */
  setAudioEnabled(enabled: boolean): void {
    this.config.audioEnabled = enabled;
    this.saveConfig();
    console.log(`✓ Audio: ${enabled ? 'ON' : 'OFF'}`);
  }

  /**
   * فحص الصوت
   */
  isAudioEnabled(): boolean {
    return this.config.audioEnabled;
  }

  /**
   * تعيين معدل الإطارات المستهدف
   */
  setTargetFrameRate(fps: number): void {
    this.config.targetFrameRate = Math.min(fps, this.config.maxFrameRate);
    this.saveConfig();
    console.log(`✓ Target FPS set to: ${this.config.targetFrameRate}`);
  }

  /**
   * الحصول على معدل الإطارات المستهدف
   */
  getTargetFrameRate(): number {
    return this.config.targetFrameRate;
  }

  /**
   * الحصول على الحد الأقصى لمعدل الإطارات
   */
  getMaxFrameRate(): number {
    return this.config.maxFrameRate;
  }

  /**
   * تعيين جودة الظلال
   */
  setShadowQuality(quality: 'low' | 'medium' | 'high'): void {
    this.config.renderSettings.shadowQuality = quality;
    this.saveConfig();
    console.log(`✓ Shadow quality set to: ${quality}`);
  }

  /**
   * تعيين جودة الجسيمات
   */
  setParticleQuality(quality: 'low' | 'medium' | 'high'): void {
    this.config.renderSettings.particleQuality = quality;
    this.saveConfig();
    console.log(`✓ Particle quality set to: ${quality}`);
  }

  /**
   * تعيين جودة النسيج
   */
  setTextureQuality(quality: 'low' | 'medium' | 'high'): void {
    this.config.renderSettings.textureQuality = quality;
    this.saveConfig();
    console.log(`✓ Texture quality set to: ${quality}`);
  }

  /**
   * الحصول على موافقة استخدام Web Workers
   */
  useWebWorkers(): boolean {
    return this.config.useWorkers;
  }

  /**
   * طباعة التكوين الحالي
   */
  printConfig(): void {
    console.log('⚙️ Current Configuration:');
    console.log(this.config);
  }

  /**
   * طباعة ملخص التكوين
   */
  printSummary(): void {
    const cfg = this.config;
    console.log(`
    ⚙️ CONFIG SUMMARY
    ─────────────────────
    Version: ${cfg.version}
    Environment: ${cfg.environment}
    Debug Mode: ${cfg.debug ? 'ON' : 'OFF'}
    Audio: ${cfg.audioEnabled ? 'ON' : 'OFF'}
    Target FPS: ${cfg.targetFrameRate}
    Max FPS: ${cfg.maxFrameRate}
    Resolution: ${cfg.renderSettings.resolution.x}x${cfg.renderSettings.resolution.y}
    DPI: ${cfg.renderSettings.dpi}
    VSync: ${cfg.renderSettings.vSync ? 'ON' : 'OFF'}
    Shadow Quality: ${cfg.renderSettings.shadowQuality}
    Particle Quality: ${cfg.renderSettings.particleQuality}
    Texture Quality: ${cfg.renderSettings.textureQuality}
    Web Workers: ${cfg.useWorkers ? 'ON' : 'OFF'}
    ─────────────────────
    `);
  }

  /**
   * إعادة تعيين التكوين للافتراضي
   */
  reset(): void {
    this.config = {
      version: '1.0.0',
      buildDate: new Date().toISOString(),
      environment: 'development',
      debug: true,
      debugSettings: this.getDefaultDebugSettings(),
      renderSettings: this.getDefaultRenderSettings(),
      audioEnabled: true,
      maxFrameRate: 144,
      targetFrameRate: 60,
      useWorkers: true,
    };
    this.saveConfig();
    console.log('✓ Config reset to defaults');
  }

  /**
   * تصدير التكوين كـ JSON
   */
  export(): string {
    return JSON.stringify(this.config, null, 2);
  }

  /**
   * استيراد التكوين من JSON
   */
  import(jsonString: string): void {
    try {
      const imported = JSON.parse(jsonString);
      this.config = { ...this.config, ...imported };
      this.saveConfig();
      console.log('✓ Config imported successfully');
    } catch (error) {
      console.error('Failed to import config', error);
    }
  }
}

// تصدير نسخة واحدة
export const config = ConfigManager.getInstance();
