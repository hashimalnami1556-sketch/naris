/**
 * Ally System - نظام الحلفاء
 * إدارة الحلفاء والمساعدين في المعركة
 */

import { EventSystem, gameEvents } from './EventSystem';
import * as BABYLON from 'babylonjs';

export interface Ally {
  id: string;
  name: string;
  characterId: string;
  level: number;
  health: number;
  maxHealth: number;
  position: BABYLON.Vector3;
  isActive: boolean;
  skills: string[];
}

export class AllySystem {
  private static instance: AllySystem;
  private allies: Map<string, Ally> = new Map();
  private activeAllies: Set<string> = new Set();
  private maxAllies: number = 3;

  private constructor() {}

  static getInstance(): AllySystem {
    if (!AllySystem.instance) {
      AllySystem.instance = new AllySystem();
    }
    return AllySystem.instance;
  }

  /**
   * تسجيل حليف
   */
  addAlly(ally: Ally): boolean {
    if (this.allies.size >= this.maxAllies && !this.activeAllies.has(ally.id)) {
      gameEvents.emit('max_allies_reached', {});
      return false;
    }

    this.allies.set(ally.id, ally);
    gameEvents.emit('ally_added', { allyId: ally.id });
    console.log(`✓ Ally added: ${ally.name}`);
    return true;
  }

  /**
   * إزالة حليف
   */
  removeAlly(allyId: string): boolean {
    if (!this.allies.has(allyId)) return false;

    this.allies.delete(allyId);
    this.activeAllies.delete(allyId);

    gameEvents.emit('ally_removed', { allyId });
    return true;
  }

  /**
   * تفعيل حليف
   */
  activateAlly(allyId: string): boolean {
    const ally = this.allies.get(allyId);
    if (!ally) return false;

    if (this.activeAllies.size >= this.maxAllies && !this.activeAllies.has(allyId)) {
      gameEvents.emit('max_active_allies_reached', {});
      return false;
    }

    ally.isActive = true;
    this.activeAllies.add(allyId);

    gameEvents.emit('ally_activated', { allyId });
    console.log(`✓ Ally activated: ${ally.name}`);
    return true;
  }

  /**
   * تعطيل حليف
   */
  deactivateAlly(allyId: string): boolean {
    const ally = this.allies.get(allyId);
    if (!ally) return false;

    ally.isActive = false;
    this.activeAllies.delete(allyId);

    gameEvents.emit('ally_deactivated', { allyId });
    return true;
  }

  /**
   * الحصول على حليف
   */
  getAlly(allyId: string): Ally | undefined {
    return this.allies.get(allyId);
  }

  /**
   * قائمة الحلفاء النشطين
   */
  getActiveAllies(): Ally[] {
    const active: Ally[] = [];
    this.activeAllies.forEach((id) => {
      const ally = this.allies.get(id);
      if (ally) active.push(ally);
    });
    return active;
  }

  /**
   * جميع الحلفاء
   */
  getAllAllies(): Ally[] {
    return Array.from(this.allies.values());
  }

  /**
   * إلحاق الضرر بحليف
   */
  damageAlly(allyId: string, damage: number): boolean {
    const ally = this.allies.get(allyId);
    if (!ally) return false;

    ally.health = Math.max(0, ally.health - damage);

    gameEvents.emit('ally_damaged', { allyId, damage, health: ally.health });

    if (ally.health === 0) {
      gameEvents.emit('ally_defeated', { allyId });
      this.deactivateAlly(allyId);
    }

    return true;
  }

  /**
   * شفاء حليف
   */
  healAlly(allyId: string, amount: number): boolean {
    const ally = this.allies.get(allyId);
    if (!ally) return false;

    ally.health = Math.min(ally.maxHealth, ally.health + amount);

    gameEvents.emit('ally_healed', { allyId, amount, health: ally.health });
    return true;
  }

  /**
   * عدد الحلفاء النشطين
   */
  getActiveAllyCount(): number {
    return this.activeAllies.size;
  }

  /**
   * إعادة تعيين الحلفاء
   */
  resetAllies(): void {
    this.allies.forEach((ally) => {
      ally.health = ally.maxHealth;
      ally.isActive = false;
    });
    this.activeAllies.clear();

    gameEvents.emit('allies_reset', {});
  }
}

export const allySystem = AllySystem.getInstance();
