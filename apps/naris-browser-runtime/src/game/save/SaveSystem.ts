import type { GameBus } from '../core/GameBus';
import type { CharacterId, NarisGameState } from '../core/GameState';
import type { InventoryItem } from '../inventory/InventorySystem';

export type SaveData={version:2;timestamp:number;player:{x:number;y:number;z:number;character:CharacterId;health:number;maxHealth:number;shards:number};environment:string;quests:NarisGameState['quests'];inventory:InventoryItem[];unlockedEnvironments:string[]};
const KEY='naris.save.v2';
export class SaveSystem {
  constructor(private bus:GameBus){}
  save(data:Omit<SaveData,'version'|'timestamp'>){const payload:SaveData={...data,version:2,timestamp:Date.now()};localStorage.setItem(KEY,JSON.stringify(payload));this.bus.emit('save.completed',{timestamp:payload.timestamp});return payload;}
  load():SaveData|null{const raw=localStorage.getItem(KEY);if(!raw)return null;try{const d=JSON.parse(raw) as SaveData;if(d.version!==2)return null;this.bus.emit('save.loaded',{timestamp:d.timestamp});return d;}catch{return null;}}
  clear(){localStorage.removeItem(KEY);this.bus.emit('save.cleared',{});}
}
