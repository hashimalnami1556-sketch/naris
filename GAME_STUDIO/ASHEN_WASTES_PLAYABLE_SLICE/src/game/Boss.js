import * as THREE from "three";

export class Boss{
  constructor(scene){
    this.scene=scene; this.active=false; this.cooldown=0;
    this.object=new THREE.Group();
    const mat=new THREE.MeshStandardMaterial({color:0x5b4c58,roughness:.9,metalness:.1});
    const core=new THREE.Mesh(new THREE.IcosahedronGeometry(1.45,1),mat);
    core.position.y=1.7; this.object.add(core);
    const glow=new THREE.Mesh(new THREE.SphereGeometry(.35,16,12),new THREE.MeshBasicMaterial({color:0xa65cff}));
    glow.position.set(0,1.7,.9); this.object.add(glow);
    this.object.position.set(0,0,34); scene.add(this.object); this.core=core;
  }
  reset(){this.active=false;this.object.visible=false;this.object.position.set(0,0,34);}
  activate(){this.active=true;this.object.visible=true;}
  update(dt,player,input,state){
    if(!this.active)return;
    this.cooldown-=dt;
    const dx=player.object.position.x-this.object.position.x;
    const dz=player.object.position.z-this.object.position.z;
    const d=Math.hypot(dx,dz);
    this.object.rotation.y += dt*.45;
    if(d<5 && this.cooldown<=0){ state.hp=Math.max(0,state.hp-12); this.cooldown=1.25; }
    if(input.down("Space") && d<4 && this.cooldown<=0){
      state.bossHp=Math.max(0,state.bossHp-7); this.cooldown=.35;
      if(state.bossHp<=0){this.active=false;this.object.visible=false;state.kills++;}
    }
  }
}
