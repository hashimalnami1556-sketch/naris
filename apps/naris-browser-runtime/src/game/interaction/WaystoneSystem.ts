import { Color3, MeshBuilder, StandardMaterial, type Scene, Vector3 } from '@babylonjs/core';
import type { GameBus } from '../core/GameBus';
export type Waystone={id:string;position:Vector3;active:boolean};
export class WaystoneSystem{
  readonly stones:Waystone[]=[]; private checkpoint:Waystone|null=null;
  constructor(private scene:Scene,private bus:GameBus){
    [[0,1,4],[8,1,-4],[-9,1,-8]].forEach((p,i)=>this.create(`waystone-${i+1}`,new Vector3(p[0],p[1],p[2])));
  }
  private create(id:string,pos:Vector3){const mesh=MeshBuilder.CreateCylinder(id,{height:2.2,diameter:0.65,tessellation:8},this.scene);mesh.position.copyFrom(pos);const mat=new StandardMaterial(`${id}-mat`,this.scene);mat.diffuseColor=new Color3(.16,.18,.22);mat.emissiveColor=new Color3(.02,.55,.7);mesh.material=mat;this.stones.push({id,position:pos.clone(),active:false});}
  activate(id:string){const s=this.stones.find(x=>x.id===id);if(!s)return false;s.active=true;this.checkpoint=s;this.bus.emit('world.waystoneActivated',{id,position:s.position.asArray()});return true;}
  get respawn(){return this.checkpoint?.position.clone()??new Vector3(0,1.1,10);}
}
