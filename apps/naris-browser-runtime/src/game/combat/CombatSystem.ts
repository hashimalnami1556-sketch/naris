import { Color3, MeshBuilder, Scene, StandardMaterial, TransformNode, Vector3 } from '@babylonjs/core';
import type { GameBus } from '../core/GameBus';
import type { CharacterController } from '../characters/CharacterController';
import { CHARACTER_PROFILES } from '../characters/CharacterController';

export interface EnemyRuntime { id: string; root: TransformNode; health: number; maxHealth: number; damage: number; speed: number; range: number; cooldown: number; }

export class CombatSystem {
  readonly enemies: EnemyRuntime[] = [];
  constructor(private scene: Scene, private player: CharacterController, private bus: GameBus, private damagePlayer: (amount: number) => void) {}

  spawnEnemy(id: string, position: Vector3, kind: 'shadow' | 'thorn' | 'guardian' = 'shadow'): void {
    const stats = kind === 'guardian' ? { hp: 160, damage: 22, speed: 1.5, range: 2.5, color: new Color3(0.28, 0.25, 0.3) } : kind === 'thorn' ? { hp: 70, damage: 12, speed: 2.7, range: 1.9, color: new Color3(0.28, 0.55, 0.2) } : { hp: 55, damage: 10, speed: 2.3, range: 2.1, color: new Color3(0.32, 0.12, 0.42) };
    const root = new TransformNode(`enemy-${id}`, this.scene); root.position.copyFrom(position);
    const body = MeshBuilder.CreateSphere(`${id}-body`, { diameter: 1.5 }, this.scene); body.parent = root;
    const mat = new StandardMaterial(`${id}-mat`, this.scene); mat.diffuseColor = stats.color; mat.emissiveColor = stats.color.scale(0.22); body.material = mat;
    this.enemies.push({ id, root, health: stats.hp, maxHealth: stats.hp, damage: stats.damage, speed: stats.speed, range: stats.range, cooldown: 0 });
  }

  playerAttack(): void {
    const profile = CHARACTER_PROFILES[this.player.id];
    let target: EnemyRuntime | undefined;
    let best = Infinity;
    for (const enemy of this.enemies) {
      const d = Vector3.Distance(enemy.root.position, this.player.position);
      if (d <= profile.range && d < best) { best = d; target = enemy; }
    }
    if (!target) return;
    const multiplier = this.player.id === 'kor' ? 1.35 : this.player.id === 'rune' ? 0.85 : 1;
    target.health -= profile.damage * multiplier;
    target.root.scaling.setAll(1.12);
    setTimeout(() => target && !target.root.isDisposed && target.root.scaling.setAll(1), 90);
    if (target.health <= 0) this.defeat(target);
  }

  update(dt: number): void {
    for (const enemy of this.enemies) {
      if (enemy.root.isDisposed) continue;
      enemy.cooldown = Math.max(0, enemy.cooldown - dt);
      const toPlayer = this.player.position.subtract(enemy.root.position); const distance = toPlayer.length();
      if (distance > enemy.range && distance < 13) {
        toPlayer.normalize(); enemy.root.position.addInPlace(toPlayer.scale(enemy.speed * dt));
      } else if (distance <= enemy.range && enemy.cooldown === 0) {
        enemy.cooldown = 1.15; this.damagePlayer(enemy.damage);
      }
    }
  }

  private defeat(enemy: EnemyRuntime): void {
    this.bus.emit('combat.enemyDefeated', { enemyId: enemy.id, xp: 35 });
    enemy.root.dispose(false, true);
    const index = this.enemies.indexOf(enemy); if (index >= 0) this.enemies.splice(index, 1);
  }
}
