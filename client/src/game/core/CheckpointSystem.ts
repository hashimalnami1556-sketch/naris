/**
 * Checkpoint System - نظام نقاط التفتيش
 * إدارة نقاط الحفظ والعودة في العالم
 */

import { EventSystem, gameEvents } from './EventSystem';
import * as BABYLON from 'babylonjs';

export interface Checkpoint {
  id: string;
  name: string;
  position: BABYLON.Vector3;
  rotation: BABYLON.Vector3;
  worldName: string;
  isSaved: boolean;
}

export class CheckpointSystem {
  private static instance: CheckpointSystem;
  private checkpoints: Map<string, Checkpoint> = new Map();
  private lastCheckpointId: string | null = null;
  private activatedCheckpoints: Set<string> = new Set();

  private constructor() {}

  static getInstance(): CheckpointSystem {
    if (!CheckpointSystem.instance) {
      CheckpointSystem.instance = new CheckpointSystem();
    }
    return CheckpointSystem.instance;
  }

  /**
   * تسجيل نقطة تفتيش
   */
  registerCheckpoint(checkpoint: Checkpoint): void {
    this.checkpoints.set(checkpoint.id, checkpoint);
    gameEvents.emit('checkpoint_registered', { checkpointId: checkpoint.id });
  }

  /**
   * تفعيل نقطة تفتيش
   */
  activateCheckpoint(checkpointId: string): boolean {
    const checkpoint = this.checkpoints.get(checkpointId);
    if (!checkpoint) return false;

    this.activatedCheckpoints.add(checkpointId);
    this.lastCheckpointId = checkpointId;
    checkpoint.isSaved = true;

    gameEvents.emit('checkpoint_activated', {
      checkpointId,
      position: checkpoint.position,
    });

    console.log(`✓ Checkpoint activated: ${checkpoint.name}`);
    return true;
  }

  /**
   * الحصول على نقطة التفتيش الأخيرة
   */
  getLastCheckpoint(): Checkpoint | null {
    return this.lastCheckpointId ? this.checkpoints.get(this.lastCheckpointId) || null : null;
  }

  /**
   * الحصول على نقطة تفتيش
   */
  getCheckpoint(checkpointId: string): Checkpoint | undefined {
    return this.checkpoints.get(checkpointId);
  }

  /**
   * قائمة نقاط التفتيش المفعلة
   */
  getActivatedCheckpoints(): Checkpoint[] {
    const activated: Checkpoint[] = [];
    this.activatedCheckpoints.forEach((id) => {
      const checkpoint = this.checkpoints.get(id);
      if (checkpoint) activated.push(checkpoint);
    });
    return activated;
  }

  /**
   * العودة إلى نقطة تفتيش
   */
  respawnAtCheckpoint(checkpointId: string): boolean {
    const checkpoint = this.checkpoints.get(checkpointId);
    if (!checkpoint || !this.activatedCheckpoints.has(checkpointId)) {
      return false;
    }

    this.lastCheckpointId = checkpointId;

    gameEvents.emit('player_respawned', {
      checkpointId,
      position: checkpoint.position,
      worldName: checkpoint.worldName,
    });

    console.log(`✓ Respawned at checkpoint: ${checkpoint.name}`);
    return true;
  }

  /**
   * هل تم تفعيل نقطة التفتيش
   */
  isCheckpointActivated(checkpointId: string): boolean {
    return this.activatedCheckpoints.has(checkpointId);
  }

  /**
   * جميع نقاط التفتيش
   */
  getAllCheckpoints(): Checkpoint[] {
    return Array.from(this.checkpoints.values());
  }

  /**
   * حساب نقاط التفتيش المفعلة
   */
  getActivatedCheckpointCount(): number {
    return this.activatedCheckpoints.size;
  }

  /**
   * نقاط التفتيش في العالم المحدد
   */
  getCheckpointsInWorld(worldName: string): Checkpoint[] {
    return Array.from(this.checkpoints.values()).filter((cp) => cp.worldName === worldName);
  }
}

export const checkpointSystem = CheckpointSystem.getInstance();
