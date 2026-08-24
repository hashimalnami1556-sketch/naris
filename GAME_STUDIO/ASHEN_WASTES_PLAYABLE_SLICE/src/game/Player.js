import * as THREE from "three";

export class Player {
  constructor(scene){
    this.object = new THREE.Group();
    const body = new THREE.Mesh(new THREE.CapsuleGeometry(.38,.9,6,12),new THREE.MeshStandardMaterial({color:0x6d3c2d,roughness:.78,metalness:.18}));
    body.position.y = 0.85; this.object.add(body);
    const ember = new THREE.Mesh(new THREE.SphereGeometry(.11,12,8),new THREE.MeshBasicMaterial({color:0xff6b27}));
    ember.position.set(-.15,1.18,.34); this.object.add(ember);
    this.object.position.set(0,.1,-22); scene.add(this.object);
    this.velocity = new THREE.Vector3();
  }
  reset(){ this.object.position.set(0,.1,-22); this.object.rotation.set(0,0,0); }
  update(dt, move, input, state){
    const speed = input.down("ShiftLeft","ShiftRight") && state.stamina>10 ? 8 : 4.2;
    if(speed>6) state.stamina = Math.max(0,state.stamina-dt*35); else state.stamina = Math.min(100,state.stamina+dt*18);
    this.velocity.set(move.x*speed,0,-move.y*speed);
    this.object.position.addScaledVector(this.velocity,dt);
    this.object.position.x = THREE.MathUtils.clamp(this.object.position.x,-7,7);
    this.object.position.z = THREE.MathUtils.clamp(this.object.position.z,-28,42);
    if(this.velocity.lengthSq()>0.01) this.object.rotation.y = Math.atan2(this.velocity.x,-this.velocity.z);
  }
}
