import type { GameBus } from '../core/GameBus';
export class XPSystem{
  xp=0; level=1; maxHealth=100;
  constructor(private bus:GameBus){}
  grant(amount:number){this.xp+=Math.max(0,amount);while(this.xp>=100){this.xp-=100;this.level++;this.maxHealth+=10;this.bus.emit('progression.levelUp',{level:this.level,maxHealth:this.maxHealth});}this.bus.emit('progression.xp',{xp:this.xp,level:this.level});}
  snapshot(){return {xp:this.xp,level:this.level,maxHealth:this.maxHealth};}
  restore(v:{xp:number;level:number;maxHealth:number}){this.xp=v.xp;this.level=v.level;this.maxHealth=v.maxHealth;}
}
