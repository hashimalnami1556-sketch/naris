import { MeshBuilder, Scene, StandardMaterial, Color3, TransformNode, Vector3 } from '@babylonjs/core';
import type { CharacterId } from '../core/GameState';
import type { GameBus } from '../core/GameBus';

export const CHARACTER_PROFILES: Record<CharacterId, { label: string; accent: Color3; speed: number; range: number; damage: number }> = {
  ash: { label: 'آش', accent: new Color3(0.78, 0.58, 0.28), speed: 4.8, range: 2.4, damage: 24 },
  rune: { label: 'رون', accent: new Color3(0.15, 0.78, 0.92), speed: 4.2, range: 9, damage: 18 },
  kor: { label: 'كور', accent: new Color3(0.92, 0.34, 0.12), speed: 3.5, range: 2.8, damage: 34 }
};

export class CharacterController {
  readonly root: TransformNode;
  private mesh;
  private input = new Vector3();
  private attackCooldown = 0;
  private characterId: CharacterId = 'ash';

  constructor(private scene: Scene, private bus: GameBus) {
    this.root = new TransformNode('naris-player-root', scene);
    this.mesh = MeshBuilder.CreateCapsule('naris-player', { height: 2.2, radius: 0.42 }, scene);
    this.mesh.parent = this.root;
    this.root.position.set(0, 1.1, 10);
    this.applyProfile();
  }

  get id(): CharacterId { return this.characterId; }
  get position(): Vector3 { return this.root.position; }
  setInput(x: number, z: number): void { this.input.set(x, 0, z); }
  switchTo(id: CharacterId): void {
    if (id === this.characterId) return;
    this.characterId = id;
    this.applyProfile();
    this.bus.emit('character.changed', { id });
  }
  attack(): void {
    if (this.attackCooldown > 0) return;
    this.attackCooldown = this.characterId === 'kor' ? 0.85 : 0.45;
    this.bus.emit('combat.playerAttack', { characterId: this.characterId });
  }
  update(dt: number): void {
    this.attackCooldown = Math.max(0, this.attackCooldown - dt);
    const profile = CHARACTER_PROFILES[this.characterId];
    if (this.input.lengthSquared() > 0.001) {
      this.input.normalize();
      this.root.position.addInPlace(this.input.scale(profile.speed * dt));
      this.root.position.x = Math.max(-18, Math.min(18, this.root.position.x));
      this.root.position.z = Math.max(-18, Math.min(18, this.root.position.z));
      this.root.rotation.y = Math.atan2(this.input.x, this.input.z);
    }
  }
  dispose(): void { this.root.dispose(false, true); }

  private applyProfile(): void {
    const profile = CHARACTER_PROFILES[this.characterId];
    const material = new StandardMaterial(`mat-${this.characterId}`, this.scene);
    material.diffuseColor = profile.accent.scale(0.38);
    material.emissiveColor = profile.accent.scale(0.18);
    this.mesh.material = material;
  }
}
