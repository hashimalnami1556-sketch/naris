import { Color3, Mesh, MeshBuilder, ParticleSystem, Scene, StandardMaterial, Vector3 } from '@babylonjs/core';
import type { GameBus } from '../core/GameBus';

export type BossPhase = 'awakening' | 'phase1' | 'phase2' | 'phase3' | 'execution' | 'dead';

export class BossController {
  readonly root: Mesh;
  private phase: BossPhase = 'awakening';
  private health = 1800;
  private attackTimer = 1.4;
  private telegraphTimer = 0;
  private readonly material: StandardMaterial;

  constructor(private scene: Scene, private bus: GameBus, position = new Vector3(0, 2.2, -14)) {
    this.root = MeshBuilder.CreateSphere('gate-guardian', { diameter: 4.4, segments: 20 }, scene);
    this.root.position.copyFrom(position);
    this.material = new StandardMaterial('gate-guardian-material', scene);
    this.material.diffuseColor = new Color3(0.06, 0.04, 0.08);
    this.material.emissiveColor = new Color3(0.42, 0.08, 0.55);
    this.root.material = this.material;
    this.enterPhase('phase1');
  }

  get isDead(): boolean { return this.phase === 'dead'; }
  get currentPhase(): BossPhase { return this.phase; }
  get currentHealth(): number { return this.health; }
  get maxHealth(): number { return 1800; }
  get attackTelegraphActive(): boolean { return this.telegraphTimer > 0; }

  damage(amount: number): void {
    if (this.isDead || amount <= 0) return;
    this.health = Math.max(0, this.health - amount);
    if (this.health <= 0) {
      this.enterPhase('dead');
      this.bus.emit('combat.enemyDefeated', { enemyId: 'gate-guardian', xp: 250 });
      return;
    }
    const ratio = this.health / this.maxHealth;
    const next: BossPhase = ratio <= 0.12 ? 'execution' : ratio <= 0.40 ? 'phase3' : ratio <= 0.70 ? 'phase2' : 'phase1';
    if (next !== this.phase) this.enterPhase(next);
  }

  update(dt: number, playerPosition: Vector3): void {
    if (this.isDead) return;
    this.attackTimer -= dt;
    this.telegraphTimer = Math.max(0, this.telegraphTimer - dt);
    const toPlayer = playerPosition.subtract(this.root.position);
    const distance = toPlayer.length();
    const speed = this.phase === 'phase2' ? 1.25 : this.phase === 'phase3' ? 1.55 : this.phase === 'execution' ? 1.85 : 0.8;
    if (distance > 0.01 && distance < 22) {
      this.root.position.addInPlace(toPlayer.normalize().scale(Math.min(distance, speed * dt)));
      this.root.position.y = 2.2;
    }
    const range = this.phase === 'phase3' || this.phase === 'execution' ? 7.5 : 6.0;
    if (this.attackTimer <= 0 && distance < range) {
      this.attackTimer = this.phase === 'phase1' ? 2.2 : this.phase === 'phase2' ? 1.45 : this.phase === 'phase3' ? 1.05 : 0.82;
      this.telegraphTimer = 0.32;
      const base = this.phase === 'execution' ? 32 : this.phase === 'phase3' ? 27 : this.phase === 'phase2' ? 20 : 14;
      this.bus.emit('player.damaged', { amount: base, health: 0 });
      this.pulseVfx();
    }
  }

  dispose(): void { this.root.dispose(false, true); }

  private enterPhase(next: BossPhase): void {
    this.phase = next;
    const color = next === 'execution' ? new Color3(0.95, 0.10, 0.06) : next === 'phase3' ? new Color3(0.80, 0.10, 0.68) : next === 'phase2' ? new Color3(0.62, 0.10, 0.82) : next === 'dead' ? new Color3(0.05, 0.03, 0.05) : new Color3(0.42, 0.08, 0.55);
    this.material.emissiveColor = color;
    this.bus.emit('boss.phaseChanged', { phase: next });
  }

  private pulseVfx(): void {
    const fx = new ParticleSystem('guardian-impact', 36, this.scene);
    fx.emitter = this.root;
    fx.minSize = 0.05; fx.maxSize = 0.22; fx.minLifeTime = 0.12; fx.maxLifeTime = 0.45;
    fx.color1 = new Color3(0.72, 0.12, 0.86).toColor4(1);
    fx.color2 = new Color3(1, 0.16, 0.06).toColor4(1);
    fx.direction1 = new Vector3(-1, 0.2, -1); fx.direction2 = new Vector3(1, 1, 1);
    fx.emitRate = 36; fx.targetStopDuration = 0.22; fx.start();
  }
}
