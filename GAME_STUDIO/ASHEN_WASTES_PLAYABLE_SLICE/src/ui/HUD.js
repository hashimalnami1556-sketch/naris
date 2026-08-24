export class HUD{
  constructor(){this.hp=document.querySelector("#hp");this.status=document.querySelector("#status");this.boss=document.querySelector("#boss");this.bossHp=document.querySelector("#bossHp");}
  update(state,player){
    this.hp.style.width=`${Math.max(0,state.hp)}%`;
    this.bossHp.style.width=`${Math.max(0,state.bossHp)}%`;
    if(state.inLava) this.status.textContent="LAVA — MOVE!";
    if(state.kills>0) this.status.textContent="Bone Beast defeated.";
  }
  setStatus(t){this.status.textContent=t}
  showBoss(){this.boss.style.display="block"}
  hideBoss(){this.boss.style.display="none"}
}
