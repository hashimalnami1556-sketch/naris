export type CharacterId = 'ash' | 'rune' | 'kor';
export type RealmId = 'ashen-forest' | 'bell-swamp' | 'twilight-castle';

export interface QuestState { id: string; state: 'available' | 'active' | 'completed' | 'turned_in'; progress: Record<string, number>; }
export interface SaveData {
  version: 2;
  timestamp: number;
  player: { x: number; y: number; z: number; health: number; maxHealth: number; shards: number; character: CharacterId };
  world: { realm: RealmId; unlocked: RealmId[]; waystones: string[] };
  quests: QuestState[];
}

export interface NarisGameState {
  player: SaveData['player'];
  world: SaveData['world'];
  quests: QuestState[];
  xp: number;
  level: number;
  paused: boolean;
}

export const INITIAL_STATE: NarisGameState = {
  player: { x: 0, y: 1, z: 10, health: 100, maxHealth: 100, shards: 0, character: 'ash' },
  world: { realm: 'ashen-forest', unlocked: ['ashen-forest'], waystones: [] },
  quests: [
    { id: 'ash-shards', state: 'active', progress: { collect: 0 } },
    { id: 'waystone-awakening', state: 'active', progress: { interact: 0 } }
  ],
  xp: 0,
  level: 1,
  paused: false
};

export class GameStateStore {
  private state: NarisGameState = structuredClone(INITIAL_STATE);
  get snapshot(): NarisGameState { return structuredClone(this.state); }
  patch(mutator: (state: NarisGameState) => void): void { mutator(this.state); }
  toSaveData(): SaveData { return { version: 2, timestamp: Date.now(), player: { ...this.state.player }, world: { ...this.state.world, unlocked: [...this.state.world.unlocked], waystones: [...this.state.world.waystones] }, quests: structuredClone(this.state.quests) }; }
  load(data: SaveData): void {
    if (data.version !== 2) throw new Error(`Unsupported save version: ${data.version}`);
    this.state.player = { ...data.player };
    this.state.world = { ...data.world, unlocked: [...data.world.unlocked], waystones: [...data.world.waystones] };
    this.state.quests = structuredClone(data.quests);
  }
}
