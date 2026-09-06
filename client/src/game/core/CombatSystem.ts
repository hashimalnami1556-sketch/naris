/**
 * Combat System - نظام القتال
 * إدارة الضرر والقدرات والحسابات القتالية
 */

import {
  DamageType,
  DamageCalculation,
  Enemy,
  EnemyAbility,
  CharacterProfile,
} from '../../types/gameTypes';
import { gameEvents } from './EventSystem';
import { gameState } from './StateManager';

export interface CombatAction {
  actorId: string;
  targetId: string;
  actionType: 'attack' | 'ability' | 'defend';
  damage?: number;
  damageType?: DamageType;
  timestamp: number;
}

export interface CombatLog {
  action: CombatAction;
  result: {
    baseDamage: number;
    multiplier: number;
    weakness: boolean;
    resistance: boolean;
    finalDamage: number;
    targetHealthAfter: number;
  };
}

export class CombatSystem {
  private static instance: CombatSystem;
  private combatLogs: CombatLog[] = [];
  private maxLogSize: number = 1000;
  private weaknessMap: Record<DamageType, DamageType[]> = {
    physical: ['void'],
    fire: ['water', 'arcane'],
    arcane: ['light', 'physical'],
    void: ['light', 'fire'],
    light: ['void'],
    water: ['fire'],
  };
  private resistanceMap: Record<DamageType, DamageType[]> = {
    physical: ['light'],
    fire: ['fire', 'arcane'],
    arcane: ['arcane', 'void'],
    void: ['void', 'light'],
    light: ['light', 'arcane'],
    water: ['water'],
  };

  private constructor() {
    console.log('⚔️ CombatSystem initialized');
  }

  /**
   * الحصول على نسخة واحدة من نظام القتال
   */
  static getInstance(): CombatSystem {
    if (!CombatSystem.instance) {
      CombatSystem.instance = new CombatSystem();
    }
    return CombatSystem.instance;
  }

  /**
   * حساب الضرر الكامل
   */
  calculateDamage(
    attacker: CharacterProfile,
    defender: any,
    damageType: DamageType = 'physical',
    abilityMultiplier: number = 1.0
  ): DamageCalculation {
    const baseDamage = attacker.stats.baseDamage;
    const defenderDefense = defender.stats?.defense || 0;

    // حساب الضرر الأساسي (مع مراعاة الدفاع)
    const defenseFactor = Math.max(0.5, 1 - defenderDefense / 100);
    const damageAfterDefense = baseDamage * defenseFactor;

    // فحص الضعف
    const hasWeakness = this.checkWeakness(defender, damageType);
    const weaknessMultiplier = hasWeakness ? 1.5 : 1.0;

    // فحص المقاومة
    const hasResistance = this.checkResistance(defender, damageType);
    const resistanceMultiplier = hasResistance ? 0.7 : 1.0;

    // الضرر النهائي
    const finalDamage = Math.round(
      damageAfterDefense * abilityMultiplier * weaknessMultiplier * resistanceMultiplier
    );

    return {
      baseDamage,
      multiplier: abilityMultiplier,
      weakness: hasWeakness,
      resistance: hasResistance,
      finalDamage: Math.max(1, finalDamage), // الحد الأدنى 1 ضرر
    };
  }

  /**
   * فحص الضعف
   */
  private checkWeakness(defender: any, damageType: DamageType): boolean {
    const defenderType = defender.damageType || 'physical';
    return this.weaknessMap[damageType]?.includes(defenderType) || false;
  }

  /**
   * فحص المقاومة
   */
  private checkResistance(defender: any, damageType: DamageType): boolean {
    const defenderType = defender.damageType || 'physical';
    return this.resistanceMap[damageType]?.includes(defenderType) || false;
  }

  /**
   * تنفيذ هجوم عادي
   */
  executeAttack(
    attackerId: string,
    targetId: string,
    attacker: CharacterProfile,
    defender: any
  ): void {
    const damageCalc = this.calculateDamage(attacker, defender, 'physical', 1.0);

    // تطبيق الضرر
    if (defender.health !== undefined) {
      defender.health = Math.max(0, defender.health - damageCalc.finalDamage);
    }

    // تسجيل الهجوم
    this.logCombatAction(
      {
        actorId: attackerId,
        targetId,
        actionType: 'attack',
        damage: damageCalc.finalDamage,
        damageType: 'physical',
        timestamp: Date.now(),
      },
      damageCalc,
      defender.health || 0
    );

    // بث الأحداث
    gameEvents.emit('attack_executed', {
      attacker: attackerId,
      target: targetId,
      damage: damageCalc.finalDamage,
      hasWeakness: damageCalc.weakness,
      hasResistance: damageCalc.resistance,
    });

    if (defender.health <= 0) {
      gameEvents.emit('enemy_defeated', {
        enemyId: targetId,
        defeatedBy: attackerId,
      });

      // منح المكافآت
      if (defender.lootTable) {
        this.processLoot(attackerId, defender.lootTable);
      }
    }

    console.log(`⚔️ Attack: ${attackerId} -> ${targetId} (${damageCalc.finalDamage} damage)`);
  }

  /**
   * تنفيذ قدرة
   */
  executeAbility(
    actorId: string,
    targetId: string,
    ability: EnemyAbility,
    attacker: CharacterProfile,
    defender: any
  ): void {
    // فحص الطاقة
    const currentEnergy = gameState.getState().playerState.energy;
    if (currentEnergy < ability.energyCost) {
      console.warn('Not enough energy for ability');
      return;
    }

    // استهلاك الطاقة
    gameState.updateEnergy(-ability.energyCost);

    // حساب الضرر
    const multiplier = ability.damage / 100;
    const damageCalc = this.calculateDamage(attacker, defender, ability.effect.type, multiplier);

    // تطبيق الضرر
    if (defender.health !== undefined) {
      defender.health = Math.max(0, defender.health - damageCalc.finalDamage);
    }

    // تطبيق التأثير الإضافي
    this.applyAbilityEffect(targetId, ability.effect);

    // تسجيل القدرة
    this.logCombatAction(
      {
        actorId,
        targetId,
        actionType: 'ability',
        damage: damageCalc.finalDamage,
        damageType: ability.effect.type,
        timestamp: Date.now(),
      },
      damageCalc,
      defender.health || 0
    );

    // بث الأحداث
    gameEvents.emit('ability_used', {
      actor: actorId,
      ability: ability.name,
      target: targetId,
      damage: damageCalc.finalDamage,
    });

    if (defender.health <= 0) {
      gameEvents.emit('enemy_defeated', {
        enemyId: targetId,
        defeatedBy: actorId,
      });

      // منح المكافآت
      if (defender.lootTable) {
        this.processLoot(actorId, defender.lootTable);
      }
    }

    console.log(`✨ Ability: ${actorId} used ${ability.name} on ${targetId} (${damageCalc.finalDamage} damage)`);
  }

  /**
   * تطبيق تأثير القدرة
   */
  private applyAbilityEffect(targetId: string, effect: any): void {
    if (!effect.statusEffect) return;

    // معالجة التأثيرات المختلفة
    switch (effect.statusEffect) {
      case 'burn':
        gameEvents.emit('status_effect_applied', {
          target: targetId,
          effect: 'burn',
          duration: 5,
          damagePerSecond: 2,
        });
        break;

      case 'freeze':
        gameEvents.emit('status_effect_applied', {
          target: targetId,
          effect: 'freeze',
          duration: 3,
          speedReduction: 0.5,
        });
        break;

      case 'stun':
        gameEvents.emit('status_effect_applied', {
          target: targetId,
          effect: 'stun',
          duration: 2,
        });
        break;

      default:
        break;
    }
  }

  /**
   * معالجة الغنائم
   */
  private processLoot(winnerActorId: string, lootTable: any): void {
    if (!lootTable) return;

    // حساب عشوائي للغنائم
    const randomFactor = Math.random();

    if (lootTable.shards && randomFactor < (lootTable.shards.chance || 0.5)) {
      const shardAmount = lootTable.shards.amount || 10;
      gameState.addShards(shardAmount);

      gameEvents.emit('loot_gained', {
        actor: winnerActorId,
        type: 'shards',
        amount: shardAmount,
      });
    }

    if (lootTable.experience && randomFactor < (lootTable.experience.chance || 1.0)) {
      const expAmount = lootTable.experience.amount || 50;
      gameState.addExperience(expAmount);

      gameEvents.emit('loot_gained', {
        actor: winnerActorId,
        type: 'experience',
        amount: expAmount,
      });
    }

    if (lootTable.items && randomFactor < (lootTable.items.chance || 0.2)) {
      const item = lootTable.items.items?.[Math.floor(Math.random() * lootTable.items.items.length)];
      if (item) {
        gameState.addToInventory(item);

        gameEvents.emit('loot_gained', {
          actor: winnerActorId,
          type: 'item',
          item: item.itemId,
        });
      }
    }
  }

  /**
   * منع/دفاع عن الضرر
   */
  executeDefend(actorId: string): void {
    const defenseBoost = 0.5; // تقليل الضرر بنسبة 50%

    gameState.updateEnergy(-10); // استهلاك الطاقة

    gameEvents.emit('defend_executed', {
      actor: actorId,
      defenseBoost,
    });

    console.log(`🛡️ Defense: ${actorId} assumes defensive stance`);
  }

  /**
   * تسجيل إجراء قتالي
   */
  private logCombatAction(
    action: CombatAction,
    result: DamageCalculation,
    targetHealthAfter: number
  ): void {
    const log: CombatLog = {
      action,
      result: {
        ...result,
        targetHealthAfter,
      },
    };

    this.combatLogs.push(log);

    if (this.combatLogs.length > this.maxLogSize) {
      this.combatLogs.shift();
    }
  }

  /**
   * الحصول على سجل القتال
   */
  getCombatLog(limit: number = 50): CombatLog[] {
    return this.combatLogs.slice(-limit);
  }

  /**
   * طباعة سجل القتال
   */
  printCombatLog(limit: number = 20): void {
    console.log('⚔️ Combat Log:');
    const logs = this.getCombatLog(limit);
    logs.forEach((log, index) => {
      console.log(
        `${index + 1}. [${log.action.actionType}] ${log.action.actorId} -> ${log.action.targetId}: ${log.result.finalDamage} damage`
      );
    });
  }

  /**
   * طباعة إحصائيات القتال
   */
  printCombatStats(): void {
    const logs = this.combatLogs;
    const totalDamageDealt = logs.reduce((sum, log) => sum + log.result.finalDamage, 0);
    const criticalHits = logs.filter((log) => log.result.weakness).length;
    const resistedHits = logs.filter((log) => log.result.resistance).length;

    console.log(`
    ⚔️ COMBAT STATISTICS
    ─────────────────────
    Total Actions: ${logs.length}
    Total Damage: ${totalDamageDealt}
    Average Damage: ${(totalDamageDealt / logs.length).toFixed(1)}
    Critical Hits: ${criticalHits}
    Resisted Attacks: ${resistedHits}
    ─────────────────────
    `);
  }
}

// تصدير نسخة واحدة
export const combatSystem = CombatSystem.getInstance();
