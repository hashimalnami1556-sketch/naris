/**
 * Combat Enhancements - تحسينات نظام القتال
 * Hitbox Detection, Hit-Stop, Camera Shake, Visual Feedback
 */

import * as BABYLON from 'babylonjs';
import { gameEvents } from './EventSystem';
import { advancedVFXSystem } from './AdvancedVFXSystem';

export interface Hitbox {
  id: string;
  entity: string;
  mesh: BABYLON.Mesh;
  radius: number;
  isActive: boolean;
  lastHitTime: number;
  cooldown: number;
}

export interface HitResult {
  hit: boolean;
  hitEntity: string | null;
  hitPosition: BABYLON.Vector3;
  hitNormal: BABYLON.Vector3;
  damage: number;
}

export class CombatEnhancements {
  private static instance: CombatEnhancements;
  private hitboxes: Map<string, Hitbox> = new Map();
  private hitResults: HitResult[] = [];
  private globalTimeDilation: number = 1.0;
  private readonly HIT_STOP_DURATION = 0.1; // 100ms
  private readonly CAMERA_SHAKE_INTENSITY = {
    light: 0.3,
    medium: 0.6,
    heavy: 1.0,
    critical: 1.5,
  };

  private constructor(private scene: BABYLON.Scene | null = null) {
    console.log('⚔️ CombatEnhancements initialized');
  }

  /**
   * الحصول على نسخة واحدة
   */
  static getInstance(): CombatEnhancements {
    if (!CombatEnhancements.instance) {
      CombatEnhancements.instance = new CombatEnhancements();
    }
    return CombatEnhancements.instance;
  }

  /**
   * تعيين المشهد
   */
  setScene(scene: BABYLON.Scene): void {
    this.scene = scene;
    advancedVFXSystem.setScene(scene);
    console.log('✓ Scene assigned to CombatEnhancements');
  }

  /**
   * إنشاء Hitbox
   */
  createHitbox(
    entityId: string,
    position: BABYLON.Vector3,
    radius: number = 2.0,
    cooldown: number = 0.5
  ): string {
    if (!this.scene) {
      console.warn('Scene not initialized');
      return '';
    }

    const hitboxId = `hitbox_${entityId}_${Date.now()}`;
    const hitboxMesh = BABYLON.MeshBuilder.CreateSphere(
      hitboxId,
      { segments: 8 },
      this.scene
    );

    hitboxMesh.position = position;
    hitboxMesh.scaling = new BABYLON.Vector3(radius, radius, radius);
    hitboxMesh.isVisible = false; // Invisible hitbox

    const hitbox: Hitbox = {
      id: hitboxId,
      entity: entityId,
      mesh: hitboxMesh,
      radius,
      isActive: true,
      lastHitTime: 0,
      cooldown,
    };

    this.hitboxes.set(hitboxId, hitbox);
    console.log(`✓ Hitbox created: ${hitboxId} for ${entityId}`);

    return hitboxId;
  }

  /**
   * فحص تصادمات Hitbox
   */
  checkHitboxCollisions(attackerHitboxId: string): HitResult[] {
    const results: HitResult[] = [];
    const attackerHitbox = this.hitboxes.get(attackerHitboxId);

    if (!attackerHitbox || !attackerHitbox.isActive) return results;

    // فحص كل Hitbox أخرى
    for (const [targetId, targetHitbox] of this.hitboxes.entries()) {
      if (targetId === attackerHitboxId || !targetHitbox.isActive) continue;

      // فحص تصادم الكرات
      const distance = BABYLON.Vector3.Distance(
        attackerHitbox.mesh.getAbsolutePosition(),
        targetHitbox.mesh.getAbsolutePosition()
      );

      if (distance < attackerHitbox.radius + targetHitbox.radius) {
        // تحقق من cooldown
        const timeSinceLastHit = (Date.now() - targetHitbox.lastHitTime) / 1000;
        if (timeSinceLastHit < targetHitbox.cooldown) continue;

        const targetPos = targetHitbox.mesh.getAbsolutePosition();
        const attackerPos = attackerHitbox.mesh.getAbsolutePosition();
        const hitNormalDir = targetPos.subtract(attackerPos);

        const hitResult: HitResult = {
          hit: true,
          hitEntity: targetHitbox.entity,
          hitPosition: targetPos,
          hitNormal: BABYLON.Vector3.Normalize(hitNormalDir),
          damage: 10, // Base damage
        };

        results.push(hitResult);
        targetHitbox.lastHitTime = Date.now();

        console.log(
          `🎯 Hit detected: ${attackerHitbox.entity} → ${targetHitbox.entity}`
        );
      }
    }

    return results;
  }

  /**
   * تطبيق Hit-Stop (تجميد الإطار)
   */
  activateHitStop(duration: number = this.HIT_STOP_DURATION): void {
    console.log(`⏸️ Hit-Stop activated (${(duration * 1000).toFixed(0)}ms)`);

    // تقليل سرعة الوقت
    this.globalTimeDilation = 0.1;
    if (this.scene) {
      // يمكن تطبيق تأثير على الفيزياء أو الأنيميشن هنا
    }

    gameEvents.emit('hit_stop', { duration });

    setTimeout(() => {
      this.globalTimeDilation = 1.0;
      console.log('⏸️ Hit-Stop ended');
    }, duration * 1000);
  }

  /**
   * تفعيل Camera Shake
   */
  activateCameraShake(
    intensity: 'light' | 'medium' | 'heavy' | 'critical' = 'medium',
    duration: number = 0.2
  ): void {
    const intensityValue = this.CAMERA_SHAKE_INTENSITY[intensity];
    console.log(
      `📷 Camera Shake: ${intensity} (${(duration * 1000).toFixed(0)}ms)`
    );

    gameEvents.emit('camera_shake', {
      intensity: intensityValue,
      duration,
      frequency: intensity === 'critical' ? 20 : 10,
    });
  }

  /**
   * تشغيل تأثير بصري عند الضربة
   */
  playImpactEffect(
    position: BABYLON.Vector3,
    intensity: number = 1.0,
    impactType: 'slash' | 'blunt' | 'magic' = 'slash'
  ): string {
    if (!this.scene) return '';

    let vfxType: 'impact' | 'spell_cast' | 'dust_cloud' = 'impact';
    if (impactType === 'magic') vfxType = 'spell_cast';
    else if (impactType === 'blunt') vfxType = 'dust_cloud';

    const effectId = advancedVFXSystem.playEffect({
      type: vfxType,
      position,
      intensity,
      duration: 1000,
      scale: intensity,
    });

    console.log(`✨ Impact effect played: ${effectId} at [${position.x.toFixed(1)}, ${position.y.toFixed(1)}, ${position.z.toFixed(1)}]`);
    return effectId;
  }

  /**
   * تطبيق تأثير كامل للضربة (Hit-Stop + Camera Shake + VFX)
   */
  applyFullHitEffect(
    hitPosition: BABYLON.Vector3,
    isCritical: boolean = false
  ): void {
    if (isCritical) {
      this.activateHitStop(this.HIT_STOP_DURATION);
      this.activateCameraShake('critical', 0.3);
      this.playImpactEffect(hitPosition, 1.5, 'blunt');
    } else {
      this.activateHitStop(this.HIT_STOP_DURATION * 0.5);
      this.activateCameraShake('medium', 0.2);
      this.playImpactEffect(hitPosition, 1.0, 'slash');
    }
  }

  /**
   * تحديث Hitbox position
   */
  updateHitboxPosition(hitboxId: string, newPosition: BABYLON.Vector3): void {
    const hitbox = this.hitboxes.get(hitboxId);
    if (hitbox) {
      hitbox.mesh.position = newPosition;
    }
  }

  /**
   * تفعيل/تعطيل Hitbox
   */
  setHitboxActive(hitboxId: string, active: boolean): void {
    const hitbox = this.hitboxes.get(hitboxId);
    if (hitbox) {
      hitbox.isActive = active;
      console.log(`${active ? '✓' : '✗'} Hitbox ${hitboxId} is now ${active ? 'active' : 'inactive'}`);
    }
  }

  /**
   * حذف Hitbox
   */
  removeHitbox(hitboxId: string): void {
    const hitbox = this.hitboxes.get(hitboxId);
    if (hitbox) {
      hitbox.mesh.dispose();
      this.hitboxes.delete(hitboxId);
      console.log(`✓ Hitbox removed: ${hitboxId}`);
    }
  }

  /**
   * الحصول على نتائج الضربات
   */
  getHitResults(): HitResult[] {
    return [...this.hitResults];
  }

  /**
   * مسح نتائج الضربات
   */
  clearHitResults(): void {
    this.hitResults = [];
  }

  /**
   * الحصول على معلومات الـ Timescale
   */
  getTimeDilation(): number {
    return this.globalTimeDilation;
  }

  /**
   * طباعة معلومات الـ Hitboxes
   */
  printHitboxInfo(): void {
    console.log(`
    ⚔️ HITBOX INFORMATION
    ─────────────────────
    Total Hitboxes: ${this.hitboxes.size}
    Active Hitboxes: ${Array.from(this.hitboxes.values()).filter(h => h.isActive).length}

    Hitboxes:
    ${Array.from(this.hitboxes.values())
      .map(h => `  - ${h.id} (${h.entity}) - ${h.isActive ? '✓' : '✗'} - Radius: ${h.radius}`)
      .join('\n')}
    ─────────────────────
    `);
  }
}

// تصدير نسخة واحدة
export const combatEnhancements = CombatEnhancements.getInstance();
