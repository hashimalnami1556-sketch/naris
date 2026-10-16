import { Color3, Mesh, MeshBuilder, Scene, StandardMaterial, Vector3 } from '@babylonjs/core';
import type { GameBus } from '../core/GameBus';

export type WolfCommand = 'follow' | 'guard' | 'track' | 'mark' | 'soulVision';

export class CompanionController {
  readonly root: Mesh;
  private command: WolfCommand = 'follow';
  private target: Vector3 | null = null;

  constructor(private scene: Scene, private bus: GameBus, spawn = new Vector3(-2, 0.65, 12)) {
    this.root = MeshBuilder.CreateSphere('celestial-wolf', { diameter: 1.25, segments: 12 }, scene);
    this.root.position.copyFrom(spawn);
    const mat = new StandardMaterial('celestial-wolf-mat', scene);
    mat.diffuseColor = new Color3(0.12, 0.16, 0.22);
    mat.emissiveColor = new Color3(0.12, 0.55, 0.68);
    this.root.material = mat;
  }

  setCommand(command: WolfCommand): void {
    this.command = command;
    this.bus.emit('companion.command', { command });
  }

  markTarget(position: Vector3): void {
    this.target = position.clone();
    this.setCommand('mark');
  }

  update(dt: number, playerPosition: Vector3): void {
    const desired = this.command === 'guard' ? playerPosition.add(new Vector3(2, 0, 1)) : playerPosition.add(new Vector3(-1.8, 0, 1.8));
    if (this.command === 'mark' && this.target) desired.copyFrom(this.target);
    const delta = desired.subtract(this.root.position);
    if (delta.lengthSquared() > 0.25) this.root.position.addInPlace(delta.normalize().scale(Math.min(delta.length(), 3.8 * dt)));
    this.root.position.y = 0.65;
  }

  dispose(): void { this.root.dispose(false, true); }
}
