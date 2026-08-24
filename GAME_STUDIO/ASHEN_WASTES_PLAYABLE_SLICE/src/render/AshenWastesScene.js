import * as THREE from "three";

export class AshenWastesScene{
  constructor(){
    this.scene=new THREE.Scene();
    this.scene.background=new THREE.Color(0x070508);
    this.scene.fog=new THREE.FogExp2(0x0b090d,.035);
    this.camera=new THREE.PerspectiveCamera(58,innerWidth/innerHeight,.1,300);
    this.camera.position.set(0,8,10); this.camera.lookAt(0,0,0);
    this.renderer=new THREE.WebGLRenderer({antialias:true});
    this.renderer.setPixelRatio(Math.min(devicePixelRatio,2));
    this.renderer.setSize(innerWidth,innerHeight); this.renderer.shadowMap.enabled=true;
    this.build(); addEventListener("resize",()=>this.resize());
  }
  build(){
    this.scene.add(new THREE.HemisphereLight(0x655b78,0x120c0b,1.0));
    const key=new THREE.DirectionalLight(0xffb38a,1.4); key.position.set(6,14,8); key.castShadow=true; this.scene.add(key);
    const ground=new THREE.Mesh(new THREE.PlaneGeometry(22,86),new THREE.MeshStandardMaterial({color:0x242126,roughness:.95}));
    ground.rotation.x=-Math.PI/2; ground.position.z=7; ground.receiveShadow=true; this.scene.add(ground);
    const stoneMat=new THREE.MeshStandardMaterial({color:0x39343a,roughness:.92});
    for(let z=-28;z<43;z+=2){const tile=new THREE.Mesh(new THREE.BoxGeometry(4,.35,1.8),stoneMat);tile.position.set(0,.05,z);tile.castShadow=tile.receiveShadow=true;this.scene.add(tile);}
    for(const [x,z,h] of [[-6,-20,4],[6,-8,5],[-6,8,6],[6,20,4],[-6,31,7]]){
      const p=new THREE.Mesh(new THREE.CylinderGeometry(.65,.8,h,8),new THREE.MeshStandardMaterial({color:0x302b30,roughness:1}));
      p.position.set(x,h/2,z); p.castShadow=true; this.scene.add(p);
    }
    const ring=new THREE.Mesh(new THREE.TorusGeometry(5.5,.22,8,64),new THREE.MeshStandardMaterial({color:0x6b3a27,emissive:0x321006,emissiveIntensity:1}));
    ring.rotation.x=Math.PI/2; ring.position.set(0,.25,34); this.scene.add(ring);
  }
  update(dt,playerPos){
    const target=new THREE.Vector3(playerPos.x,5.7,playerPos.z+8);
    this.camera.position.lerp(target,1-Math.pow(.0001,dt));
    this.camera.lookAt(playerPos.x,1,playerPos.z+2);
  }
  resize(){this.camera.aspect=innerWidth/innerHeight;this.camera.updateProjectionMatrix();this.renderer.setSize(innerWidth,innerHeight);}
}
