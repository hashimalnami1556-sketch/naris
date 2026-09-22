import { Color3, Mesh, MeshBuilder, Scene, StandardMaterial } from '@babylonjs/core';
import type { GameBus } from '../core/GameBus';

export class GateSystem {
  readonly gate: Mesh;
  private unlocked = false;

  constructor(private scene: Scene, private bus: GameBus) {
    this.gate = MeshBuilder.CreateBox('ash-gate', { width: 7, height: 6, depth: 0.8 }, scene);
    this.gate.position.set(0, 3, -19);
    const mat = new StandardMaterial('ash-gate-mat', scene);
    mat.diffuseColor = new Color3(0.07, 0.06, 0.08);
    mat.emissiveColor = new Color3(0.45, 0.3, 0.08);
    this.gate.material = mat;
  }

  get isUnlocked(): boolean { return this.unlocked; }

  unlock(): void {
    if (this.unlocked) return;
    this.unlocked = true;
    this.gate.isVisible = false;
    this.gate.checkCollisions = false;
    this.bus.emit('world.gateUnlocked', { gateId: 'ash-gate' });
  }

  tryUnlock(questComplete: boolean): boolean {
    if (questComplete) this.unlock();
    return this.unlocked;
  }

  dispose(): void { this.gate.dispose(false, true); }
}
