import type { GameBus } from '../core/GameBus';

export type QuestState = 'available' | 'active' | 'completed' | 'turned_in';
export type ObjectiveType = 'collect' | 'interact' | 'kill' | 'reach';
export type QuestObjective = { id:string; type:ObjectiveType; target:string; requiredAmount:number; currentAmount:number; description:string };
export type Quest = { id:string; title:string; description:string; objectives:QuestObjective[]; rewardShards:number; rewardXp:number; state:QuestState };

export class QuestManager {
  private quests = new Map<string, Quest>();
  constructor(private bus: GameBus) {
    this.add({ id:'ash-shards', title:'شظايا الرماد', description:'اجمع شظايا الرماد لفتح البوابة.', rewardShards:50, rewardXp:40, state:'active', objectives:[{id:'shards',type:'collect',target:'ash-shard',requiredAmount:5,currentAmount:0,description:'اجمع 5 شظايا الرماد'}] });
    this.add({ id:'waystone-awakening', title:'إيقاظ أحجار الطريق', description:'فعّل أحجار الطريق القديمة.', rewardShards:25, rewardXp:60, state:'available', objectives:[{id:'stones',type:'interact',target:'waystone',requiredAmount:3,currentAmount:0,description:'فعّل 3 أحجار طريق'}] });
    this.add({ id:'gate-guardian', title:'حارس البوابة', description:'اهزم حارس البوابة للوصول إلى القلعة.', rewardShards:100, rewardXp:150, state:'available', objectives:[{id:'boss',type:'kill',target:'gate-guardian',requiredAmount:1,currentAmount:0,description:'اهزم حارس البوابة'}] });
  }
  add(q:Quest){ this.quests.set(q.id,q); }
  get(id:string){ return this.quests.get(id); }
  all(){ return [...this.quests.values()]; }
  activate(id:string){ const q=this.quests.get(id); if(q && q.state==='available'){q.state='active'; this.bus.emit('quest.changed',{id,state:q.state});} }
  progress(type:ObjectiveType,target:string,amount=1){
    for(const q of this.quests.values()){
      if(q.state!=='active') continue;
      const o=q.objectives.find(x=>x.type===type&&x.target===target&&x.currentAmount<x.requiredAmount); if(!o) continue;
      o.currentAmount=Math.min(o.requiredAmount,o.currentAmount+amount);
      this.bus.emit('quest.progress',{questId:q.id,objectiveId:o.id,current:o.currentAmount,required:o.requiredAmount});
      if(q.objectives.every(x=>x.currentAmount>=x.requiredAmount)){q.state='completed';this.bus.emit('quest.changed',{id:q.id,state:q.state});}
    }
  }
  turnIn(id:string){ const q=this.quests.get(id); if(!q||q.state!=='completed') return null; q.state='turned_in'; this.bus.emit('quest.rewarded',{id,rewardShards:q.rewardShards,rewardXp:q.rewardXp}); return q; }
}
