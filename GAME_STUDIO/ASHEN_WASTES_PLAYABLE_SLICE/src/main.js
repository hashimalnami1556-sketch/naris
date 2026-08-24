import * as THREE from "three";
import { GameState } from "./core/GameState.js";
import { Input } from "./core/Input.js";
import { Player } from "./game/Player.js";
import { LavaSystem } from "./game/LavaSystem.js";
import { Boss } from "./game/Boss.js";
import { AshenWastesScene } from "./render/AshenWastesScene.js";
import { HUD } from "./ui/HUD.js";

const mount = document.querySelector("#game");
const hud = new HUD();
const state = new GameState();
const input = new Input();
const scenePack = new AshenWastesScene();
mount.appendChild(scenePack.renderer.domElement);

const player = new Player(scenePack.scene);
const lava = new LavaSystem(scenePack.scene);
const boss = new Boss(scenePack.scene);
state.reset();

let last = performance.now();
function reset(){
  state.reset(); player.reset(); boss.reset(); hud.hideBoss();
  hud.setStatus("Explore the ash bridge.");
}
input.onReset = reset;

function tick(now){
  const dt = Math.min((now-last)/1000, 0.05); last = now;
  const move = input.moveVector();
  player.update(dt, move, input, state);
  lava.update(dt);
  state.inLava = lava.isDanger(player.object.position);
  if(state.inLava) state.hp -= dt * 18;
  if(player.object.position.z > 28 && !state.bossStarted){
    state.bossStarted = true; boss.activate(); hud.showBoss();
    hud.setStatus("The Bone Beast awakens.");
  }
  if(state.bossStarted) boss.update(dt, player, input, state);
  if(state.hp <= 0) reset();
  scenePack.update(dt, player.object.position);
  hud.update(state, player);
  scenePack.renderer.render(scenePack.scene, scenePack.camera);
  requestAnimationFrame(tick);
}
requestAnimationFrame(tick);
