/**
 * Enemy AI - نظام ذكاء الأعداء
 * إدارة السلوك والقرارات والمسارات للأعداء
 */

import * as BABYLON from 'babylonjs';
import { Enemy, CharacterId } from '../../types/gameTypes';
import { gameEvents } from './EventSystem';
import { combatSystem } from './CombatSystem';

export type AIBehavior = 'idle' | 'patrol' | 'aggressive' | 'boss' | 'flee';

export interface EnemyInstance {
  id: string;
  enemy: Enemy;
  mesh: BABYLON.AbstractMesh | null;
  position: BABYLON.Vector3;
  velocity: BABYLON.Vector3;
  behavior: AIBehavior;
  targetPosition: BABYLON.Vector3;
  targetEnemy: EnemyInstance | null;
  lastActionTime: number;
  cooldownTimers: Map<string, number>;
  lastSeenPlayerPos: BABYLON.Vector3 | null;
  sightRange: number;
  attackRange: number;
}

export class EnemyAI {
  private static instance: EnemyAI;
  private enemies: Map<string, EnemyInstance> = new Map();
  private enemyIdCounter: number = 0;
  private updateFrequency: number = 100; // ms

  private constructor() {
    console.log('👹 EnemyAI initialized');
  }

  /**
   * الحصول على نسخة واحدة من نظام ذكاء الأعداء
   */
  static getInstance(): EnemyAI {
    if (!EnemyAI.instance) {
      EnemyAI.instance = new EnemyAI();
    }
    return EnemyAI.instance;
  }

  /**
   * تهيئة نظام الذكاء الاصطناعي
   */
  initialize(): void {
    gameEvents.subscribe('frame_update', () => this.update());
    console.log('✓ EnemyAI initialized');
  }

  /**
   * إضافة عدو جديد
   */
  addEnemy(
    enemy: Enemy,
    position: BABYLON.Vector3,
    behavior: AIBehavior = 'patrol',
    mesh: BABYLON.AbstractMesh | null = null
  ): string {
    const enemyId = `enemy_${this.enemyIdCounter++}`;

    const enemyInstance: EnemyInstance = {
      id: enemyId,
      enemy,
      mesh,
      position: position.clone(),
      velocity: BABYLON.Vector3.Zero(),
      behavior,
      targetPosition: position.clone(),
      targetEnemy: null,
      lastActionTime: Date.now(),
      cooldownTimers: new Map(),
      lastSeenPlayerPos: null,
      sightRange: 30,
      attackRange: enemy.attackRange || 2,
    };

    this.enemies.set(enemyId, enemyInstance);

    gameEvents.emit('enemy_spawned', {
      enemyId,
      enemyType: enemy.type,
      position: position.asArray(),
    });

    console.log(`👹 Enemy spawned: ${enemyId} (${enemy.type})`);
    return enemyId;
  }

  /**
   * تحديث جميع الأعداء
   */
  private update(): void {
    this.enemies.forEach((enemyInstance) => {
      this.updateEnemyBehavior(enemyInstance);
      this.updateEnemyMovement(enemyInstance);
      this.updateEnemyCombat(enemyInstance);
    });
  }

  /**
   * تحديث سلوك العدو
   */
  private updateEnemyBehavior(enemyInstance: EnemyInstance): void {
    const now = Date.now();
    const timeSinceLastAction = now - enemyInstance.lastActionTime;

    if (timeSinceLastAction < this.updateFrequency) {
      return;
    }

    switch (enemyInstance.behavior) {
      case 'idle':
        this.behaviorIdle(enemyInstance);
        break;
      case 'patrol':
        this.behaviorPatrol(enemyInstance);
        break;
      case 'aggressive':
        this.behaviorAggressive(enemyInstance);
        break;
      case 'boss':
        this.behaviorBoss(enemyInstance);
        break;
      case 'flee':
        this.behaviorFlee(enemyInstance);
        break;
    }

    enemyInstance.lastActionTime = now;
  }

  /**
   * سلوك الخمول
   */
  private behaviorIdle(enemyInstance: EnemyInstance): void {
    // لا تفعل شيئاً - تقف في مكانها
    enemyInstance.velocity = BABYLON.Vector3.Zero();

    // احتمال الانتقال إلى الدوري
    if (Math.random() < 0.1) {
      enemyInstance.behavior = 'patrol';
      console.log(`${enemyInstance.id}: idle -> patrol`);
    }
  }

  /**
   * سلوك الدوري
   */
  private behaviorPatrol(enemyInstance: EnemyInstance): void {
    // إنشاء نقطة دورية عشوائية
    if (BABYLON.Vector3.Distance(enemyInstance.position, enemyInstance.targetPosition) < 2) {
      const randomAngle = Math.random() * Math.PI * 2;
      const randomDistance = 20;
      enemyInstance.targetPosition = new BABYLON.Vector3(
        Math.cos(randomAngle) * randomDistance,
        0,
        Math.sin(randomAngle) * randomDistance
      );
    }

    // الحركة نحو النقطة
    const direction = BABYLON.Vector3.Normalize(
      enemyInstance.targetPosition.subtract(enemyInstance.position)
    );
    enemyInstance.velocity = BABYLON.Vector3.Scale(direction, enemyInstance.enemy.speed);
  }

  /**
   * السلوك العدواني
   */
  private behaviorAggressive(enemyInstance: EnemyInstance): void {
    // هذا يجب أن يكون لديه هدف (لاعب أو عدو آخر)
    if (!enemyInstance.targetEnemy) {
      // البحث عن أقرب هدف
      // سيتم تحديثه عند الكشف عن اللاعب
      enemyInstance.behavior = 'patrol';
      return;
    }

    const targetPos = enemyInstance.targetEnemy.position;
    const distance = BABYLON.Vector3.Distance(enemyInstance.position, targetPos);

    if (distance > enemyInstance.sightRange) {
      // خسر الهدف من النظر
      enemyInstance.behavior = 'patrol';
      enemyInstance.targetEnemy = null;
      return;
    }

    // الاقتراب من الهدف
    const direction = BABYLON.Vector3.Normalize(targetPos.subtract(enemyInstance.position));
    enemyInstance.velocity = BABYLON.Vector3.Scale(direction, enemyInstance.enemy.speed);
  }

  /**
   * السلوك الزعيم (Boss)
   */
  private behaviorBoss(enemyInstance: EnemyInstance): void {
    // سلوك أكثر تعقيداً
    // استراتيجيات أكثر تقدماً والقدرات الخاصة
    // يمكن إضافة أنماط هجوم وحركات خاصة

    if (!enemyInstance.targetEnemy) {
      enemyInstance.targetEnemy = this.findNearestTarget(enemyInstance);
    }

    if (!enemyInstance.targetEnemy) {
      this.behaviorPatrol(enemyInstance);
      return;
    }

    const targetPos = enemyInstance.targetEnemy.position;
    const distance = BABYLON.Vector3.Distance(enemyInstance.position, targetPos);

    if (distance > enemyInstance.sightRange * 2) {
      enemyInstance.behavior = 'patrol';
      enemyInstance.targetEnemy = null;
      return;
    }

    // الزعيم يتحرك بحذر أكثر
    const direction = BABYLON.Vector3.Normalize(targetPos.subtract(enemyInstance.position));
    enemyInstance.velocity = BABYLON.Vector3.Scale(direction, enemyInstance.enemy.speed * 0.7);
  }

  /**
   * سلوك الفرار
   */
  private behaviorFlee(enemyInstance: EnemyInstance): void {
    if (!enemyInstance.targetEnemy) {
      // الفرار انتهى
      enemyInstance.behavior = 'patrol';
      return;
    }

    const threatPos = enemyInstance.targetEnemy.position;
    const direction = BABYLON.Vector3.Normalize(
      enemyInstance.position.subtract(threatPos)
    );
    enemyInstance.velocity = BABYLON.Vector3.Scale(direction, enemyInstance.enemy.speed * 1.5);

    // المسافة من التهديد
    const distance = BABYLON.Vector3.Distance(enemyInstance.position, threatPos);
    if (distance > 50) {
      enemyInstance.behavior = 'patrol';
      enemyInstance.targetEnemy = null;
    }
  }

  /**
   * تحديث حركة العدو
   */
  private updateEnemyMovement(enemyInstance: EnemyInstance): void {
    const deltaTime = 0.016; // ~60fps

    enemyInstance.position.addInPlace(BABYLON.Vector3.Scale(enemyInstance.velocity, deltaTime));

    // تحديث موضع الشكل الثلاثي الأبعاد
    if (enemyInstance.mesh) {
      enemyInstance.mesh.position = enemyInstance.position.clone();
    }

    // تطبيق الجاذبية
    if (enemyInstance.position.y > 0) {
      enemyInstance.velocity.y -= 9.8 * deltaTime;
    } else {
      enemyInstance.position.y = 0;
      enemyInstance.velocity.y = 0;
    }
  }

  /**
   * تحديث قتال العدو
   */
  private updateEnemyCombat(enemyInstance: EnemyInstance): void {
    if (!enemyInstance.targetEnemy) return;

    const distance = BABYLON.Vector3.Distance(
      enemyInstance.position,
      enemyInstance.targetEnemy.position
    );

    if (distance <= enemyInstance.attackRange) {
      this.executeEnemyAttack(enemyInstance);
    }
  }

  /**
   * تنفيذ هجوم العدو
   */
  private executeEnemyAttack(enemyInstance: EnemyInstance): void {
    const ability = enemyInstance.enemy.abilities?.[0];
    if (!ability) return;

    // فحص Cooldown
    const cooldown = enemyInstance.cooldownTimers.get(ability.name) || 0;
    if (cooldown > 0) {
      enemyInstance.cooldownTimers.set(ability.name, cooldown - 16);
      return;
    }

    // تنفيذ الهجوم
    gameEvents.emit('enemy_attack', {
      enemyId: enemyInstance.id,
      ability: ability.name,
      damage: ability.damage,
    });

    // تعيين Cooldown
    enemyInstance.cooldownTimers.set(ability.name, ability.cooldown);

    console.log(`👹 ${enemyInstance.id} uses ${ability.name}`);
  }

  /**
   * البحث عن أقرب هدف
   */
  private findNearestTarget(enemyInstance: EnemyInstance): EnemyInstance | null {
    let nearest: EnemyInstance | null = null;
    let minDistance = enemyInstance.sightRange;

    this.enemies.forEach((other) => {
      if (other.id === enemyInstance.id) return;

      const distance = BABYLON.Vector3.Distance(enemyInstance.position, other.position);
      if (distance < minDistance) {
        minDistance = distance;
        nearest = other;
      }
    });

    return nearest;
  }

  /**
   * إلحاق الضرر بالعدو
   */
  damageEnemy(enemyId: string, damage: number): boolean {
    const enemyInstance = this.enemies.get(enemyId);
    if (!enemyInstance) return false;

    enemyInstance.enemy.health -= damage;

    // تحويل إلى عدواني عند الإصابة
    if (enemyInstance.behavior !== 'boss' && enemyInstance.behavior !== 'aggressive') {
      enemyInstance.behavior = 'aggressive';
    }

    gameEvents.emit('enemy_damaged', {
      enemyId,
      damage,
      healthRemaining: enemyInstance.enemy.health,
    });

    // فحص الوفاة
    if (enemyInstance.enemy.health <= 0) {
      this.removeEnemy(enemyId);
      return true;
    }

    return false;
  }

  /**
   * إزالة عدو
   */
  removeEnemy(enemyId: string): void {
    const enemyInstance = this.enemies.get(enemyId);
    if (!enemyInstance) return;

    if (enemyInstance.mesh) {
      enemyInstance.mesh.dispose();
    }

    this.enemies.delete(enemyId);

    gameEvents.emit('enemy_defeated', {
      enemyId,
    });

    console.log(`🗑️ Enemy removed: ${enemyId}`);
  }

  /**
   * الحصول على عدو
   */
  getEnemy(enemyId: string): EnemyInstance | undefined {
    return this.enemies.get(enemyId);
  }

  /**
   * الحصول على جميع الأعداء
   */
  getAllEnemies(): EnemyInstance[] {
    return Array.from(this.enemies.values());
  }

  /**
   * تعيين السلوك
   */
  setEnemyBehavior(enemyId: string, behavior: AIBehavior): void {
    const enemyInstance = this.enemies.get(enemyId);
    if (enemyInstance) {
      enemyInstance.behavior = behavior;
      console.log(`${enemyId}: behavior -> ${behavior}`);
    }
  }

  /**
   * طباعة معلومات العدو
   */
  printEnemyInfo(enemyId: string): void {
    const enemyInstance = this.enemies.get(enemyId);
    if (!enemyInstance) {
      console.log(`Enemy ${enemyId} not found`);
      return;
    }

    console.log(`
    👹 ENEMY INFO: ${enemyId}
    ─────────────────────
    Type: ${enemyInstance.enemy.type}
    Health: ${enemyInstance.enemy.health}/${enemyInstance.enemy.maxHealth}
    Behavior: ${enemyInstance.behavior}

    Stats:
      Damage: ${enemyInstance.enemy.damage}
      Speed: ${enemyInstance.enemy.speed}
      Attack Range: ${enemyInstance.attackRange}
      Sight Range: ${enemyInstance.sightRange}

    Position: [${enemyInstance.position.x.toFixed(2)}, ${enemyInstance.position.y.toFixed(2)}, ${enemyInstance.position.z.toFixed(2)}]
    Velocity: [${enemyInstance.velocity.x.toFixed(2)}, ${enemyInstance.velocity.y.toFixed(2)}, ${enemyInstance.velocity.z.toFixed(2)}]

    Target: ${enemyInstance.targetEnemy?.id || 'None'}
    ─────────────────────
    `);
  }

  /**
   * طباعة إحصائيات الأعداء
   */
  printEnemyStats(): void {
    const enemies = Array.from(this.enemies.values());
    const totalHealth = enemies.reduce((sum, e) => sum + e.enemy.health, 0);
    const behaviorCounts = {
      idle: 0,
      patrol: 0,
      aggressive: 0,
      boss: 0,
      flee: 0,
    };

    enemies.forEach((e) => {
      behaviorCounts[e.behavior]++;
    });

    console.log(`
    👹 ENEMY STATISTICS
    ─────────────────────
    Total Enemies: ${enemies.length}
    Total Health: ${totalHealth}

    Behaviors:
      Idle: ${behaviorCounts.idle}
      Patrol: ${behaviorCounts.patrol}
      Aggressive: ${behaviorCounts.aggressive}
      Boss: ${behaviorCounts.boss}
      Flee: ${behaviorCounts.flee}
    ─────────────────────
    `);
  }

  /**
   * تنظيف الموارد
   */
  dispose(): void {
    this.enemies.forEach((_, enemyId) => {
      this.removeEnemy(enemyId);
    });

    this.enemies.clear();
    console.log('🗑️ EnemyAI disposed');
  }
}

// تصدير نسخة واحدة
export const enemyAI = EnemyAI.getInstance();
