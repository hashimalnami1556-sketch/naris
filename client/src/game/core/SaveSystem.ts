/**
 * Save System - نظام حفظ اللعبة
 * إدارة حفظ وتحميل بيانات اللعبة
 */

import { EventSystem, gameEvents } from './EventSystem';
import { StateManager, gameState } from './StateManager';

export interface SaveData {
  timestamp: number;
  version: string;
  playerState: any;
  questProgress: any;
  inventory: any;
  achievements: any;
  worldState: any;
}

export class SaveSystem {
  private static instance: SaveSystem;
  private saves: Map<string, SaveData> = new Map();
  private currentSave: string | null = null;
  private autoSaveInterval: NodeJS.Timeout | null = null;

  private constructor() {
    this.loadFromLocalStorage();
  }

  static getInstance(): SaveSystem {
    if (!SaveSystem.instance) {
      SaveSystem.instance = new SaveSystem();
    }
    return SaveSystem.instance;
  }

  /**
   * حفظ اللعبة
   */
  save(saveName: string): void {
    const state = gameState.getState();
    const saveData: SaveData = {
      timestamp: Date.now(),
      version: '1.0.0',
      playerState: state.player,
      questProgress: state.quests,
      inventory: state.inventory,
      achievements: state.achievements,
      worldState: state.world,
    };

    this.saves.set(saveName, saveData);
    this.currentSave = saveName;
    this.saveToLocalStorage();

    gameEvents.emit('game_saved', { saveName, timestamp: saveData.timestamp });
    console.log(`✓ Game saved: ${saveName}`);
  }

  /**
   * تحميل اللعبة
   */
  load(saveName: string): boolean {
    const saveData = this.saves.get(saveName);
    if (!saveData) {
      console.warn(`Save file not found: ${saveName}`);
      return false;
    }

    try {
      gameState.setState({
        player: saveData.playerState,
        quests: saveData.questProgress,
        inventory: saveData.inventory,
        achievements: saveData.achievements,
        world: saveData.worldState,
      });

      this.currentSave = saveName;
      gameEvents.emit('game_loaded', { saveName });
      console.log(`✓ Game loaded: ${saveName}`);
      return true;
    } catch (error) {
      console.error('Failed to load game:', error);
      gameEvents.emit('load_failed', { error });
      return false;
    }
  }

  /**
   * حذف ملف الحفظ
   */
  deleteSave(saveName: string): boolean {
    if (!this.saves.has(saveName)) {
      return false;
    }

    this.saves.delete(saveName);
    this.saveToLocalStorage();

    if (this.currentSave === saveName) {
      this.currentSave = null;
    }

    gameEvents.emit('save_deleted', { saveName });
    console.log(`✓ Save deleted: ${saveName}`);
    return true;
  }

  /**
   * الحصول على قائمة الحفظات
   */
  getSavesList(): { name: string; timestamp: number }[] {
    return Array.from(this.saves.entries()).map(([name, data]) => ({
      name,
      timestamp: data.timestamp,
    }));
  }

  /**
   * حفظ تلقائي
   */
  enableAutoSave(intervalMs: number = 60000): void {
    if (this.autoSaveInterval) {
      clearInterval(this.autoSaveInterval);
    }

    this.autoSaveInterval = setInterval(() => {
      this.save('autosave');
    }, intervalMs);

    console.log(`✓ Auto-save enabled (${intervalMs}ms interval)`);
  }

  /**
   * إيقاف الحفظ التلقائي
   */
  disableAutoSave(): void {
    if (this.autoSaveInterval) {
      clearInterval(this.autoSaveInterval);
      this.autoSaveInterval = null;
    }

    console.log('✓ Auto-save disabled');
  }

  /**
   * حفظ إلى LocalStorage
   */
  private saveToLocalStorage(): void {
    try {
      const savesData = Array.from(this.saves.entries());
      localStorage.setItem('naris_saves', JSON.stringify(savesData));
    } catch (error) {
      console.error('Failed to save to localStorage:', error);
    }
  }

  /**
   * تحميل من LocalStorage
   */
  private loadFromLocalStorage(): void {
    try {
      const savesData = localStorage.getItem('naris_saves');
      if (savesData) {
        const parsed = JSON.parse(savesData);
        this.saves = new Map(parsed);
      }
    } catch (error) {
      console.error('Failed to load from localStorage:', error);
    }
  }

  /**
   * مسح جميع الحفظات
   */
  clearAllSaves(): void {
    this.saves.clear();
    this.currentSave = null;
    this.saveToLocalStorage();
    gameEvents.emit('all_saves_cleared', {});
    console.log('✓ All saves cleared');
  }
}

export const saveSystem = SaveSystem.getInstance();
