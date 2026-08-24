import * as THREE from "three";
export class LavaSystem{
  constructor(scene){
    this.lava=[];
    const mat=new THREE.MeshStandardMaterial({color:0x7b160d,emissive:0xff3b0b,emissiveIntensity:2.8,roughness:.32,metalness:.05});
    for(const z of [-12,0,12,24]){
      const m=new THREE.Mesh(new THREE.BoxGeometry(14,.18,9.5),mat);
      m.position.set(0,-.15,z); scene.add(m); this.lava.push(m);
    }
  }
  update(t){ for(const m of this.lava) m.material.emissiveIntensity=2.3+Math.sin(performance.now()/260+m.position.z)*.45; }
  isDanger(p){ return this.lava.some(m=>Math.abs(p.x-m.position.x)<6.8&&Math.abs(p.z-m.position.z)<4.6); }
}
