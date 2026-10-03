import type { GameBus } from '../core/GameBus';
export type ItemId='ash-shard'|'ash-potion'|'stone-key';
export type InventoryItem={id:ItemId;name:string;quantity:number};
export class InventorySystem {
  private items:Record<ItemId,InventoryItem>={
    'ash-shard':{id:'ash-shard',name:'شظية الرماد',quantity:0},
    'ash-potion':{id:'ash-potion',name:'جرعة الرماد',quantity:2},
    'stone-key':{id:'stone-key',name:'مفتاح حجري',quantity:0}
  };
  constructor(private bus:GameBus){}
  add(id:ItemId,amount=1){this.items[id].quantity+=amount;this.bus.emit('inventory.changed',{id,quantity:this.items[id].quantity});}
  has(id:ItemId,amount=1){return this.items[id].quantity>=amount;}
  consume(id:ItemId,amount=1){if(!this.has(id,amount))return false;this.items[id].quantity-=amount;this.bus.emit('inventory.changed',{id,quantity:this.items[id].quantity});return true;}
  snapshot(){return Object.values(this.items).map(x=>({...x}));}
  restore(items:InventoryItem[]){for(const item of items){if(this.items[item.id])this.items[item.id].quantity=Math.max(0,item.quantity);}}
  usePotion(maxHealth:number,currentHealth:number){if(!this.consume('ash-potion'))return currentHealth;const next=Math.min(maxHealth,currentHealth+maxHealth*.3);this.bus.emit('inventory.potionUsed',{health:next});return next;}
}
