import { Color3, MeshBuilder, Scene, StandardMaterial, Vector3 } from '@babylonjs/core';
import { GameBus } from '../core/GameBus';

export type EnemyId = 'ashen-shade' | 'thorn-creature' | 'stone-guardian' | 'gate-guardian';
export type EnemyState = 'idle' | 'investigate' | 'chase' | 'attack' | 'stagger' | 'dead';

export interface EnemyProfile {
  id: EnemyId; name: string; health: number; damage: number; speed: number;
  attackRange: number; attackCooldown: number; flying: boolean; element: string; color: Color3;
}

export const ENEMY_PROFILES: Record<EnemyId, EnemyProfile> = {
  'ashen-shade': { id: 'ashen-shade', name: 'Ashen Shade', health: 220, damage: 24, speed: 3.8, attackRange: 2.8, attackCooldown: 1.2, flying: true, element: 'AetherViolet', color: new Color3(0.32, 0.12, 0.48) },
  'thorn-creature': { id: 'thorn-creature', name: 'Thorn Creature', health: 300, damage: 32, speed: 4.6, attackRange: 2.2, attackCooldown: 1.0, flying: false, element: 'Emerald', color: new Color3(0.08, 0.32, 0.18) },
  'stone-guardian': { id: 'stone-guardian', name: 'Stone Guardian', health: 650, damage: 55, speed: 1.7, attackRange: 3.2, attackCooldown: 1.8, flying: false, element: 'Obsidian', color: new Color3(0.18, 0.20, 0.22) },
  'gate-guardian': { id: 'gate-guardian', name: 'Gate Guardian', health: 1800, damage: 55, speed: 2.6, attackRange: 3.2, attackCooldown: 1.5, flying: false, element: 'Void', color: new Color3(0.10, 0.06, 0.16) },
};

export interface RuntimeEnemy {
  id: string; profile: EnemyProfile; mesh: import('@babylonjs/core').Mesh;
  health: number; state: EnemyState; lastAttackAt: number;
}

export class EnemyFactory {
  constructor(private readonly scene: Scene, private readonly bus: GameBus) {}

  spawn(type: EnemyId, position: Vector3): RuntimeEnemy {
    const profile = ENEMY_PROFILES[type];
    const root = MeshBuilder.CreateCapsule(`enemy_${type}_${Date.now()}`, { height: type === 'stone-guardian' || type === 'gate-guardian' ? 3.6 : 2.4, radius: 0.65 }, this.scene);
    root.position.copyFrom(position);
    root.position.y = profile.flying ? position.y + 2.0 : Math.max(0.9, position.y);
    const material = new StandardMaterial(`mat_${type}`, this.scene);
    material.diffuseColor = profile.color;
    material.emissiveColor = type === 'ashen-shade' || type === 'gate-guardian' ? profile.color.scale(0.45) : Color3.Black();
    root.material = material;
    root.metadata = { naris: { enemyId: type, profile, hitbox: 'capsule', sockets: ['SOCKET_VFX_CORE', 'SOCKET_ATTACK', 'SOCKET_HIT', 'SOCKET_PROJECTILE'] } };
    const enemy: RuntimeEnemy = { id: root.name, profile, mesh: root, health: profile.health, state: 'idle', lastAttackAt: -Infinity };
    return enemy;
  }

  damage(enemy: RuntimeEnemy, amount: number): void {
    if (enemy.state === 'dead') return;
    enemy.health = Math.max(0, enemy.health - Math.max(0, amount));
    enemy.state = enemy.health <= 0 ? 'dead' : 'stagger';
    if (enemy.health <= 0) {
      enemy.mesh.setEnabled(false);
      this.bus.emit('combat.enemyDefeated', { enemyId: enemy.profile.id, xp: Math.round(enemy.profile.health / 4) });
    }
  }
}
