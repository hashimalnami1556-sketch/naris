import * as THREE from "three";

export class Input {
  constructor(){
    this.keys = new Set();
    this.onReset = null;
    addEventListener("keydown", e=>{
      this.keys.add(e.code);
      if(e.code==="KeyR" && this.onReset) this.onReset();
    });
    addEventListener("keyup", e=>this.keys.delete(e.code));
  }
  down(...codes){ return codes.some(c=>this.keys.has(c)); }
  moveVector(){
    const x = (this.down("KeyD","ArrowRight")?1:0) - (this.down("KeyA","ArrowLeft")?1:0);
    const z = (this.down("KeyW","ArrowUp")?1:0) - (this.down("KeyS","ArrowDown")?1:0);
    const v = new THREE.Vector2(x,z);
    if(v.lengthSq()>1) v.normalize();
    return v;
  }
}
