export type NarisEvents = {
  'character.changed': { id: string };
  'combat.playerAttack': { characterId: string };
  'combat.enemyDefeated': { enemyId: string; xp: number };
  'player.damaged': { amount: number; health: number };
  'player.died': { lostShards: number };
  'world.waystoneActivated': { id: string };
  'world.shardCollected': { amount: number };
  'world.gateUnlocked': { gateId: string };
  'boss.phaseChanged': { phase: string };
  'companion.command': { command: string };
  'quest.progress': { questId: string; objectiveId: string; current: number; required: number };
  'quest.completed': { questId: string };
  'inventory.changed': { itemId: string; quantity: number };
  'save.completed': { timestamp: number };
};

type Handler<T> = (payload: T) => void;

export class GameBus {
  private handlers = new Map<keyof NarisEvents, Set<Handler<any>>>();

  on<K extends keyof NarisEvents>(event: K, handler: Handler<NarisEvents[K]>): () => void {
    const set = this.handlers.get(event) ?? new Set<Handler<any>>();
    set.add(handler);
    this.handlers.set(event, set);
    return () => set.delete(handler);
  }

  emit<K extends keyof NarisEvents>(event: K, payload: NarisEvents[K]): void {
    this.handlers.get(event)?.forEach((handler) => handler(payload));
  }

  clear(): void { this.handlers.clear(); }
}
