/**
 * World Manager - مدير العالم
 * إدارة التبديل بين البيئات والعوالم المختلفة
 */

import { EventSystem, gameEvents } from './EventSystem';

export interface World {
  id: string;
  name: string;
  description: string;
  theme: string;
  lighting: {
    ambientIntensity: number;
    sunIntensity: number;
    sunColor: { r: number; g: number; b: number };
  };
  environmentProps: {
    fogDensity: number;
    precipitation: 'none' | 'rain' | 'snow' | 'ash';
    temperature: number;
  };
}

export class WorldManager {
  private static instance: WorldManager;
  private worlds: Map<string, World> = new Map();
  private currentWorldId: string | null = null;
  private previousWorldId: string | null = null;

  private constructor() {
    this.initializeWorlds();
  }

  static getInstance(): WorldManager {
    if (!WorldManager.instance) {
      WorldManager.instance = new WorldManager();
    }
    return WorldManager.instance;
  }

  /**
   * تسجيل عالم
   */
  registerWorld(world: World): void {
    this.worlds.set(world.id, world);
  }

  /**
   * التبديل إلى عالم
   */
  switchToWorld(worldId: string): boolean {
    const world = this.worlds.get(worldId);
    if (!world) return false;

    this.previousWorldId = this.currentWorldId;
    this.currentWorldId = worldId;

    gameEvents.emit('world_switched', {
      worldId,
      previousWorldId: this.previousWorldId,
      world,
    });

    console.log(`✓ Switched to world: ${world.name}`);
    return true;
  }

  /**
   * الحصول على العالم الحالي
   */
  getCurrentWorld(): World | null {
    return this.currentWorldId ? this.worlds.get(this.currentWorldId) || null : null;
  }

  /**
   * الحصول على عالم
   */
  getWorld(worldId: string): World | undefined {
    return this.worlds.get(worldId);
  }

  /**
   * قائمة جميع العوالم
   */
  getAllWorlds(): World[] {
    return Array.from(this.worlds.values());
  }

  /**
   * العودة إلى العالم السابق
   */
  returnToPreviousWorld(): boolean {
    if (!this.previousWorldId) return false;
    return this.switchToWorld(this.previousWorldId);
  }

  /**
   * تحديث خصائص العالم
   */
  updateWorldProperties(worldId: string, updates: Partial<World>): boolean {
    const world = this.worlds.get(worldId);
    if (!world) return false;

    Object.assign(world, updates);
    gameEvents.emit('world_updated', { worldId, updates });

    return true;
  }

  /**
   * تهيئة العوالم الافتراضية
   */
  private initializeWorlds(): void {
    const worlds: World[] = [
      {
        id: 'ashen_forest',
        name: 'Ashen Forest',
        description: 'غابة رمادية محاطة بدخان والسحب',
        theme: 'dark_nature',
        lighting: {
          ambientIntensity: 0.5,
          sunIntensity: 0.7,
          sunColor: { r: 1, g: 0.8, b: 0.6 },
        },
        environmentProps: {
          fogDensity: 0.3,
          precipitation: 'ash',
          temperature: 15,
        },
      },
      {
        id: 'crystal_cavern',
        name: 'Crystal Cavern',
        description: 'كهف مليء بالبلورات المتألقة',
        theme: 'cave_mystical',
        lighting: {
          ambientIntensity: 0.3,
          sunIntensity: 0.2,
          sunColor: { r: 0.5, g: 0.8, b: 1 },
        },
        environmentProps: {
          fogDensity: 0.15,
          precipitation: 'none',
          temperature: 10,
        },
      },
      {
        id: 'void_palace',
        name: 'Void Palace',
        description: 'قصر في فراغ الفضاء',
        theme: 'ethereal_void',
        lighting: {
          ambientIntensity: 0.4,
          sunIntensity: 0,
          sunColor: { r: 0.8, g: 0.5, b: 1 },
        },
        environmentProps: {
          fogDensity: 0.2,
          precipitation: 'none',
          temperature: -10,
        },
      },
      {
        id: 'echo_sanctum',
        name: 'Echo Sanctum',
        description: 'معبد مقدس مليء بالأصداء',
        theme: 'sacred_chamber',
        lighting: {
          ambientIntensity: 0.6,
          sunIntensity: 0.8,
          sunColor: { r: 1, g: 1, b: 0.9 },
        },
        environmentProps: {
          fogDensity: 0.1,
          precipitation: 'none',
          temperature: 20,
        },
      },
    ];

    worlds.forEach((world) => this.registerWorld(world));
  }

  /**
   * معلومات العالم الحالي
   */
  getCurrentWorldInfo(): string {
    const world = this.getCurrentWorld();
    return world ? `${world.name} (${world.id})` : 'No world loaded';
  }
}

export const worldManager = WorldManager.getInstance();
