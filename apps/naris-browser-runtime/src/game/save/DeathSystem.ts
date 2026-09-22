import { Vector3 } from '@babylonjs/core';
import type { GameBus } from '../core/GameBus';
import type { CharacterController } from '../characters/CharacterController';

export class DeathSystem {
  private health = 100;
  private maxHealth = 100;
  private shards = 0;
  private checkpoint = new Vector3(0, 1.1, 10);
  private dead = false;

  constructor(private bus: GameBus, private player: CharacterController) {
    bus.on('world.waystoneActivated', () => { this.checkpoint.copyFrom(player.position); });
  }

  setHealth(value: number, maxHealth = this.maxHealth): void {
    this.maxHealth = Math.max(1, maxHealth);
    this.health = Math.max(0, Math.min(this.maxHealth, value));
    if (this.health === 0) this.die();
  }

  setShards(value: number): void { this.shards = Math.max(0, Math.floor(value)); }
  get currentHealth(): number { return this.health; }
  get currentShards(): number { return this.shards; }
  get isDead(): boolean { return this.dead; }

  damage(amount: number): void { this.setHealth(this.health - Math.max(0, amount)); }

  respawn(): void {
    this.dead = false;
    this.health = this.maxHealth;
    this.player.root.position.copyFrom(this.checkpoint);
  }

  private die(): void {
    if (this.dead) return;
    this.dead = true;
    const lost = Math.floor(this.shards / 2);
    this.shards -= lost;
    this.bus.emit('player.died', { lostShards: lost });
    this.respawn();
  }
}
