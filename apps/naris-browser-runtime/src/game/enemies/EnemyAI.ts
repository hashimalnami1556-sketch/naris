import { Vector3 } from '@babylonjs/core';
import type { RuntimeEnemy } from './EnemyFactory';

export class EnemyAI {
  update(enemy: RuntimeEnemy, dt: number, playerPosition: Vector3): void {
    if (enemy.state === 'dead') return;
    const delta = playerPosition.subtract(enemy.mesh.position);
    const distance = delta.length();
    if (enemy.state === 'stagger') {
      enemy.state = 'chase';
      return;
    }
    if (distance > 18) {
      enemy.state = 'idle';
      return;
    }
    if (distance <= enemy.profile.attackRange) {
      enemy.state = 'attack';
      return;
    }
    enemy.state = 'chase';
    if (distance > 0.05) {
      const step = Math.min(distance, enemy.profile.speed * dt);
      const direction = delta.normalize();
      if (!enemy.profile.flying) direction.y = 0;
      enemy.mesh.position.addInPlace(direction.normalize().scale(step));
    }
  }
}
