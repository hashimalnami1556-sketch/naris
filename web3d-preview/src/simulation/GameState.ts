export type Vec3 = { x: number; y: number; z: number };

export class GameState {
  player = {
    position: { x: 0, y: 1, z: 0 } as Vec3,
    yaw: 0,
    hp: 100,
    maxHp: 100,
    energy: 100,
    resonance: 0,
    speed: 5.2,
    sprintMultiplier: 1.65
  };

  objective = "Awaken in the Ashen Forest";
  paused = false;

  setPaused(value: boolean) {
    this.paused = value;
  }

  spendEnergy(amount: number): boolean {
    if (this.player.energy < amount) return false;
    this.player.energy -= amount;
    return true;
  }

  addResonance(amount: number) {
    this.player.resonance = Math.max(0, Math.min(100, this.player.resonance + amount));
  }

  tick(dt: number) {
    if (this.paused) return;
    this.player.energy = Math.min(100, this.player.energy + 12 * dt);
    this.player.resonance = Math.max(0, this.player.resonance - 2 * dt);
  }
}
