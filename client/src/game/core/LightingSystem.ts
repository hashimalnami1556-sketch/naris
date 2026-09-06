/**
 * Lighting System - نظام الإضاءة
 * إدارة الإضاءة والظلال والتأثيرات الضوئية
 */

import { EventSystem, gameEvents } from './EventSystem';
import * as BABYLON from 'babylonjs';

export interface Light {
  id: string;
  name: string;
  type: 'directional' | 'point' | 'spot';
  intensity: number;
  color: BABYLON.Color3;
  position?: BABYLON.Vector3;
  direction?: BABYLON.Vector3;
  range?: number;
  shadowGenerator?: BABYLON.ShadowGenerator;
}

export class LightingSystem {
  private static instance: LightingSystem;
  private lights: Map<string, Light> = new Map();
  private scene: BABYLON.Scene | null = null;
  private sunLight: Light | null = null;
  private ambientLight: Light | null = null;

  private constructor() {}

  static getInstance(): LightingSystem {
    if (!LightingSystem.instance) {
      LightingSystem.instance = new LightingSystem();
    }
    return LightingSystem.instance;
  }

  /**
   * تعيين المشهد
   */
  setScene(scene: BABYLON.Scene): void {
    this.scene = scene;
    this.initializeDefaultLights();
  }

  /**
   * إضافة إضاءة
   */
  addLight(light: Light): boolean {
    if (!this.scene) return false;

    this.lights.set(light.id, light);

    // إنشاء الضوء في Babylon.js
    let babylonLight: BABYLON.Light;

    switch (light.type) {
      case 'directional':
        babylonLight = new BABYLON.HemisphericLight(light.id, new BABYLON.Vector3(0, 1, 0), this.scene);
        babylonLight.intensity = light.intensity;
        (babylonLight as BABYLON.HemisphericLight).diffuse = light.color;
        break;

      case 'point':
        babylonLight = new BABYLON.PointLight(light.id, light.position || BABYLON.Vector3.Zero(), this.scene);
        babylonLight.intensity = light.intensity;
        babylonLight.range = light.range || 100;
        (babylonLight as BABYLON.PointLight).diffuse = light.color;
        break;

      case 'spot':
        babylonLight = new BABYLON.SpotLight(
          light.id,
          light.position || BABYLON.Vector3.Zero(),
          light.direction || new BABYLON.Vector3(0, -1, 0),
          Math.PI / 3,
          2,
          this.scene
        );
        babylonLight.intensity = light.intensity;
        (babylonLight as BABYLON.SpotLight).diffuse = light.color;
        break;

      default:
        return false;
    }

    gameEvents.emit('light_added', { lightId: light.id });
    console.log(`✓ Light added: ${light.name}`);
    return true;
  }

  /**
   * إزالة إضاءة
   */
  removeLight(lightId: string): boolean {
    const light = this.lights.get(lightId);
    if (!light || !this.scene) return false;

    const babylonLight = this.scene.getLightByID(lightId);
    if (babylonLight) {
      babylonLight.dispose();
    }

    this.lights.delete(lightId);
    gameEvents.emit('light_removed', { lightId });
    return true;
  }

  /**
   * تعديل شدة الإضاءة
   */
  setLightIntensity(lightId: string, intensity: number): boolean {
    const light = this.lights.get(lightId);
    if (!light || !this.scene) return false;

    light.intensity = intensity;

    const babylonLight = this.scene.getLightByID(lightId);
    if (babylonLight) {
      babylonLight.intensity = intensity;
    }

    gameEvents.emit('light_intensity_changed', { lightId, intensity });
    return true;
  }

  /**
   * تعديل لون الإضاءة
   */
  setLightColor(lightId: string, color: BABYLON.Color3): boolean {
    const light = this.lights.get(lightId);
    if (!light || !this.scene) return false;

    light.color = color;

    const babylonLight = this.scene.getLightByID(lightId);
    if (babylonLight) {
      (babylonLight as any).diffuse = color;
    }

    gameEvents.emit('light_color_changed', { lightId, color });
    return true;
  }

  /**
   * إنشاء مولد الظلال
   */
  createShadowGenerator(lightId: string, mapSize: number = 2048): BABYLON.ShadowGenerator | null {
    const light = this.lights.get(lightId);
    if (!light || !this.scene) return null;

    const babylonLight = this.scene.getLightByID(lightId);
    if (!babylonLight) return null;

    const shadowGenerator = new BABYLON.ShadowGenerator(mapSize, babylonLight as any);
    light.shadowGenerator = shadowGenerator;

    gameEvents.emit('shadow_generator_created', { lightId });
    return shadowGenerator;
  }

  /**
   * تهيئة الإضاءات الافتراضية
   */
  private initializeDefaultLights(): void {
    if (!this.scene) return;

    // شمس
    const sunLight: Light = {
      id: 'sun',
      name: 'Sun',
      type: 'directional',
      intensity: 1,
      color: new BABYLON.Color3(1, 0.95, 0.8),
      direction: new BABYLON.Vector3(1, -1, 1),
    };

    // إضاءة محيطة
    const ambientLight: Light = {
      id: 'ambient',
      name: 'Ambient',
      type: 'directional',
      intensity: 0.4,
      color: new BABYLON.Color3(0.5, 0.7, 1),
    };

    this.addLight(sunLight);
    this.addLight(ambientLight);

    this.sunLight = sunLight;
    this.ambientLight = ambientLight;
  }

  /**
   * الحصول على الشمس
   */
  getSunLight(): Light | null {
    return this.sunLight;
  }

  /**
   * الحصول على الإضاءة المحيطة
   */
  getAmbientLight(): Light | null {
    return this.ambientLight;
  }

  /**
   * جميع الإضاءات
   */
  getAllLights(): Light[] {
    return Array.from(this.lights.values());
  }
}

export const lightingSystem = LightingSystem.getInstance();
