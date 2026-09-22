import { Engine, HemisphericLight, Scene, Vector3, Color4, MeshBuilder, StandardMaterial, Color3, FreeCamera, GlowLayer } from '@babylonjs/core';
import { GameBus } from './GameBus';
import { GameStateStore } from './GameState';
import { ServiceRegistry } from './ServiceRegistry';
import { CharacterController } from '../characters/CharacterController';
import { CombatSystem } from '../combat/CombatSystem';

export class GameRoot {
  readonly bus = new GameBus();
  readonly state = new GameStateStore();
  readonly services = new ServiceRegistry();
  readonly scene: Scene;
  readonly player: CharacterController;
  readonly combat: CombatSystem;
  readonly camera: FreeCamera;
  private engine: Engine;
  private disposed = false;

  constructor(private canvas: HTMLCanvasElement) {
    this.engine = new Engine(canvas, true, { antialias: true, adaptToDeviceRatio: true });
    this.scene = new Scene(this.engine);
    this.scene.clearColor = new Color4(0.018, 0.022, 0.035, 1);
    this.scene.fogMode = Scene.FOGMODE_EXP2; this.scene.fogDensity = 0.025; this.scene.fogColor = new Color3(0.04, 0.035, 0.055);
    new HemisphericLight('moon', new Vector3(0.2, 1, 0.1), this.scene).intensity = 0.55;
    const glow = new GlowLayer('naris-glow', this.scene); glow.intensity = 0.7;
    this.camera = new FreeCamera('player-camera', new Vector3(0, 7, 18), this.scene); this.camera.setTarget(new Vector3(0, 1, 5));
    this.player = new CharacterController(this.scene, this.bus);
    this.combat = new CombatSystem(this.scene, this.player, this.bus, (amount) => {
      this.state.patch((s) => { s.player.health = Math.max(0, s.player.health - amount); });
      this.bus.emit('player.damaged', { amount, health: this.state.snapshot.player.health });
    });
    this.services.set('game', this); this.services.set('state', this.state); this.services.set('bus', this.bus); this.services.set('player', this.player); this.services.set('combat', this.combat);
    this.buildAshenForest(); this.bindInput();
    this.engine.runRenderLoop(() => this.tick());
    window.addEventListener('resize', this.resize);
  }

  private tick = (): void => {
    if (this.disposed) return;
    const dt = Math.min(this.engine.getDeltaTime() / 1000, 0.05);
    if (!this.state.snapshot.paused) { this.player.update(dt); this.combat.update(dt); }
    this.camera.position.x += (this.player.position.x - this.camera.position.x) * Math.min(1, dt * 5);
    this.camera.position.z += ((this.player.position.z + 9) - this.camera.position.z) * Math.min(1, dt * 5);
    this.camera.setTarget(this.player.position.add(new Vector3(0, 0.7, 0)));
    this.scene.render();
  };

  private bindInput(): void {
    const keys = new Set<string>();
    window.addEventListener('keydown', (e) => { keys.add(e.key.toLowerCase()); if (e.key === ' ') this.player.attack(); if (e.key === '1') this.player.switchTo('ash'); if (e.key === '2') this.player.switchTo('rune'); if (e.key === '3') this.player.switchTo('kor'); });
    window.addEventListener('keyup', (e) => keys.delete(e.key.toLowerCase()));
    this.scene.onBeforeRenderObservable.add(() => this.player.setInput((keys.has('d') ? 1 : 0) - (keys.has('a') ? 1 : 0), (keys.has('s') ? 1 : 0) - (keys.has('w') ? 1 : 0)));
    this.canvas.addEventListener('pointerdown', () => this.player.attack());
  }

  private buildAshenForest(): void {
    const ground = MeshBuilder.CreateGround('ashen-ground', { width: 40, height: 40, subdivisions: 8 }, this.scene);
    const groundMat = new StandardMaterial('ashen-soil', this.scene); groundMat.diffuseColor = new Color3(0.055, 0.048, 0.06); groundMat.specularColor = new Color3(0.08, 0.08, 0.1); ground.material = groundMat;
    for (let i = 0; i < 34; i++) {
      const x = ((i * 17) % 37) - 18, z = ((i * 29) % 37) - 18;
      if (Math.abs(x) < 4 && z > 3) continue;
      const trunk = MeshBuilder.CreateCylinder(`tree-${i}`, { height: 3 + (i % 4), diameterTop: 0.2, diameterBottom: 0.55 }, this.scene);
      trunk.position.set(x, trunk.scaling.y * 1.5, z); trunk.scaling.y = 1;
      const mat = new StandardMaterial(`tree-mat-${i}`, this.scene); mat.diffuseColor = new Color3(0.07, 0.055, 0.06); trunk.material = mat;
    }
    const gate = MeshBuilder.CreateTorus('ash-gate', { diameter: 6, thickness: 0.55, tessellation: 24 }, this.scene); gate.position.set(0, 3, -13); gate.rotation.x = Math.PI / 2;
    const gateMat = new StandardMaterial('gate-gold', this.scene); gateMat.diffuseColor = new Color3(0.28, 0.18, 0.06); gateMat.emissiveColor = new Color3(0.35, 0.18, 0.03); gate.material = gateMat;
    this.combat.spawnEnemy('shadow-01', new Vector3(-5, 1, 2), 'shadow'); this.combat.spawnEnemy('thorn-01', new Vector3(5, 1, -3), 'thorn'); this.combat.spawnEnemy('guardian-01', new Vector3(0, 1, -7), 'guardian');
    for (let i = 0; i < 5; i++) { const shard = MeshBuilder.CreatePolyhedron(`shard-${i}`, { type: 1, size: 0.6 }, this.scene); shard.position.set(-8 + i * 4, 0.65, 6 - (i % 2) * 2); const m = new StandardMaterial(`shard-mat-${i}`, this.scene); m.diffuseColor = new Color3(0.75, 0.48, 0.08); m.emissiveColor = new Color3(0.6, 0.3, 0.03); shard.material = m; }
  }

  private resize = (): void => this.engine.resize();
  dispose(): void { this.disposed = true; window.removeEventListener('resize', this.resize); this.scene.dispose(); this.engine.dispose(); this.bus.clear(); }
}
