import { Color3, Mesh, MeshBuilder, ParticleSystem, Scene, StandardMaterial, Vector3 } from '@babylonjs/core';
import type { GameBus } from '../core/GameBus';

export type BossPhase = 'awakening' | 'phase1' | 'phase2' | 'execution' | 'dead';

export class BossController {
  readonly root: Mesh;
  private phase: BossPhase = 'awakening';
  private health = 900;
  private attackTimer = 0;
  private phaseCueTimer = 0;
  private readonly material: StandardMaterial;

  constructor(private scene: Scene, private bus: GameBus, position = new Vector3(0, 2.2, -14)) {
    this.root = MeshBuilder.CreateSphere('gate-guardian', { diameter: 4.4, segments: 16 }, scene);
    this.root.position.copyFrom(position);
    this.material = new StandardMaterial('gate-guardian-material', scene);
    this.material.diffuseColor = new Color3(0.08, 0.06, 0.1);
    this.material.emissiveColor = new Color3(0.42, 0.08, 0.55);
    this.root.material = this.material;
    this.enterPhase('phase1');
  }

  get isDead(): boolean { return this.phase === 'dead'; }
  get currentPhase(): BossPhase { return this.phase; }
  get currentHealth(): number { return this.health; }

  damage(amount: number): void {
    if (this.isDead || amount <= 0) return;
    this.health = Math.max(0, this.health - amount);
    if (this.health <= 0) {
      this.enterPhase('dead');
      this.bus.emit('combat.enemyDefeated', { enemyId: 'gate-guardian', xp: 250 });
      return;
    }
    const next = this.health <= 40 ? 'execution' : this.health <= 70 ? 'phase2' : 'phase1';
    if (next !== this.phase) this.enterPhase(next);
  }

  update(dt: number, playerPosition: Vector3): void {
    if (this.isDead) return;
    this.attackTimer -= dt;
    this.phaseCueTimer -= dt;
    const toPlayer = playerPosition.subtract(this.root.position);
    const distance = toPlayer.length();
    if (distance > 0.01) {
      const speed = this.phase === 'phase2' ? 1.25 : this.phase === 'execution' ? 1.7 : 0.8;
      this.root.position.addInPlace(toPlayer.normalize().scale(Math.min(distance, speed * dt)));
      this.root.position.y = 2.2;
    }
    if (this.attackTimer <= 0 && distance < 7) {
      this.attackTimer = this.phase === 'phase1' ? 2.2 : this.phase === 'phase2' ? 1.45 : 1.0;
      this.bus.emit('player.damaged', { amount: this.phase === 'execution' ? 28 : this.phase === 'phase2' ? 20 : 14, health: 0 });
      this.pulseVfx();
    }
  }

  dispose(): void { this.root.dispose(false, true); }

  private enterPhase(next: BossPhase): void {
    this.phase = next;
    this.phaseCueTimer = 1.2;
    const color = next === 'execution' ? new Color3(0.95, 0.12, 0.08) : next === 'phase2' ? new Color3(0.72, 0.12, 0.86) : new Color3(0.42, 0.08, 0.55);
    this.material.emissiveColor = color;
    this.bus.emit('boss.phaseChanged', { phase: next });
  }

  private pulseVfx(): void {
    const fx = new ParticleSystem('guardian-impact', 24, this.scene);
    fx.emitter = this.root;
    fx.minSize = 0.06; fx.maxSize = 0.18; fx.minLifeTime = 0.15; fx.maxLifeTime = 0.4;
    fx.color1 = new Color3(0.8, 0.2, 0.9).toColor4(1); fx.color2 = new Color3(1, 0.2, 0.1).toColor4(1);
    fx.direction1 = new Vector3(-1, 0.2, -1); fx.direction2 = new Vector3(1, 1, 1); fx.emitRate = 24; fx.targetStopDuration = 0.2; fx.start();
  }
}
