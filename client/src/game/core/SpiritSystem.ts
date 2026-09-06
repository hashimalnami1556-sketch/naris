/**
 * Spirit System - نظام الأرواح
 * إدارة الأرواح والمخلوقات الغيبية
 */

import { EventSystem, gameEvents } from './EventSystem';
import * as BABYLON from 'babylonjs';

export type SpiritType = 'guardian' | 'guide' | 'shadow' | 'echo';

export interface Spirit {
  id: string;
  name: string;
  type: SpiritType;
  position: BABYLON.Vector3;
  power: number;
  maxPower: number;
  isActive: boolean;
  abilities: string[];
}

export class SpiritSystem {
  private static instance: SpiritSystem;
  private spirits: Map<string, Spirit> = new Map();
  private activeSpirits: Set<string> = new Set();
  private totalPowerAvailable: number = 100;

  private constructor() {
    this.initializeSpirits();
  }

  static getInstance(): SpiritSystem {
    if (!SpiritSystem.instance) {
      SpiritSystem.instance = new SpiritSystem();
    }
    return SpiritSystem.instance;
  }

  /**
   * تسجيل روح
   */
  registerSpirit(spirit: Spirit): void {
    this.spirits.set(spirit.id, spirit);
    gameEvents.emit('spirit_registered', { spiritId: spirit.id });
  }

  /**
   * استدعاء روح
   */
  summonSpirit(spiritId: string): boolean {
    const spirit = this.spirits.get(spiritId);
    if (!spirit || spirit.isActive) return false;

    spirit.isActive = true;
    this.activeSpirits.add(spiritId);
    spirit.power = spirit.maxPower;

    gameEvents.emit('spirit_summoned', { spiritId });
    console.log(`✓ Spirit summoned: ${spirit.name}`);
    return true;
  }

  /**
   * إرسال روح
   */
  dismissSpirit(spiritId: string): boolean {
    const spirit = this.spirits.get(spiritId);
    if (!spirit || !spirit.isActive) return false;

    spirit.isActive = false;
    this.activeSpirits.delete(spiritId);

    gameEvents.emit('spirit_dismissed', { spiritId });
    console.log(`✓ Spirit dismissed: ${spirit.name}`);
    return true;
  }

  /**
   * استخدام قوة الروح
   */
  useSpiritPower(spiritId: string, amount: number): boolean {
    const spirit = this.spirits.get(spiritId);
    if (!spirit || !spirit.isActive) return false;

    if (spirit.power < amount) {
      return false;
    }

    spirit.power -= amount;

    gameEvents.emit('spirit_power_used', { spiritId, amount, power: spirit.power });

    if (spirit.power === 0) {
      this.dismissSpirit(spiritId);
    }

    return true;
  }

  /**
   * شحن قوة الروح
   */
  rechargeSpirit(spiritId: string): boolean {
    const spirit = this.spirits.get(spiritId);
    if (!spirit) return false;

    spirit.power = spirit.maxPower;

    gameEvents.emit('spirit_recharged', { spiritId });
    console.log(`✓ Spirit recharged: ${spirit.name}`);
    return true;
  }

  /**
   * الحصول على روح
   */
  getSpirit(spiritId: string): Spirit | undefined {
    return this.spirits.get(spiritId);
  }

  /**
   * قائمة الأرواح النشطة
   */
  getActiveSpirits(): Spirit[] {
    const active: Spirit[] = [];
    this.activeSpirits.forEach((id) => {
      const spirit = this.spirits.get(id);
      if (spirit) active.push(spirit);
    });
    return active;
  }

  /**
   * جميع الأرواح
   */
  getAllSpirits(): Spirit[] {
    return Array.from(this.spirits.values());
  }

  /**
   * الأرواح من نوع معين
   */
  getSpiritsOfType(type: SpiritType): Spirit[] {
    return Array.from(this.spirits.values()).filter((s) => s.type === type);
  }

  /**
   * تهيئة الأرواح الافتراضية
   */
  private initializeSpirits(): void {
    const spirits: Spirit[] = [
      {
        id: 'guardian_spirit',
        name: 'Guardian Spirit',
        type: 'guardian',
        position: BABYLON.Vector3.Zero(),
        power: 100,
        maxPower: 100,
        isActive: false,
        abilities: ['protect', 'shield'],
      },
      {
        id: 'guide_spirit',
        name: 'Guide Spirit',
        type: 'guide',
        position: BABYLON.Vector3.Zero(),
        power: 80,
        maxPower: 80,
        isActive: false,
        abilities: ['navigate', 'reveal'],
      },
      {
        id: 'shadow_spirit',
        name: 'Shadow Spirit',
        type: 'shadow',
        position: BABYLON.Vector3.Zero(),
        power: 60,
        maxPower: 60,
        isActive: false,
        abilities: ['hide', 'strike'],
      },
    ];

    spirits.forEach((spirit) => this.registerSpirit(spirit));
  }

  /**
   * عدد الأرواح النشطة
   */
  getActiveSpiritCount(): number {
    return this.activeSpirits.size;
  }

  /**
   * إجمالي القوة المستخدمة
   */
  getTotalPowerUsed(): number {
    let total = 0;
    this.activeSpirits.forEach((id) => {
      const spirit = this.spirits.get(id);
      if (spirit) {
        total += spirit.maxPower - spirit.power;
      }
    });
    return total;
  }
}

export const spiritSystem = SpiritSystem.getInstance();
