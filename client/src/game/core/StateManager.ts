/**
 * State Manager - مدير الحالة المركزي
 * إدارة حالة اللعبة الكاملة والحفاظ على التزامن
 */

import {
  GameState,
  GameSettings,
  CharacterId,
  RealmId,
  PlayerGameState,
  InventoryItem,
  Quest,
  Achievement,
} from '../../types/gameTypes';
import { gameEvents } from './EventSystem';

export class StateManager {
  private static instance: StateManager;
  private state: GameState;

  private constructor() {
    this.state = this.initializeDefaultState();
    console.log('🎮 StateManager initialized');
  }

  /**
   * الحصول على نسخة واحدة من مدير الحالة
   */
  static getInstance(): StateManager {
    if (!StateManager.instance) {
      StateManager.instance = new StateManager();
    }
    return StateManager.instance;
  }

  /**
   * تهيئة الحالة الافتراضية
   */
  private initializeDefaultState(): GameState {
    const defaultSettings: GameSettings = {
      difficulty: 'normal',
      language: 'ar',
      masterVolume: 100,
      musicVolume: 80,
      sfxVolume: 90,
      ambientVolume: 70,
      graphicsQuality: 'high',
      resolution: '1920x1080',
      fpsTarget: 60,
      vSync: true,
      reducedMotion: false,
      subtitles: true,
      hudScale: 1.0,
      showMinimap: true,
      showQuestMarkers: true,
    };

    const defaultPlayerState: PlayerGameState = {
      health: 100,
      energy: 100,
      shards: 0,
      experience: 0,
      level: 1,
      weaponTier: 0,
      unlockedAbilities: [],
      currentQuests: [],
      completedQuests: [],
      allies: [],
    };

    return {
      isRunning: false,
      isPaused: false,
      currentRealm: 'ash_gate',
      currentCharacter: 'ash',
      playerState: defaultPlayerState,
      inventory: [],
      quests: [],
      achievements: [],
      settings: defaultSettings,
      weather: {
        type: 'clear',
        intensity: 0,
        duration: 0,
      },
      timeOfDay: 360, // الصباح
      fps: 60,
    };
  }

  /**
   * الحصول على الحالة الكاملة
   */
  getState(): GameState {
    return { ...this.state };
  }

  /**
   * تحديث الحالة الكاملة
   */
  setState(newState: Partial<GameState>): void {
    this.state = {
      ...this.state,
      ...newState,
    };
    gameEvents.emit('game_state_changed', { oldState: this.state, newState });
  }

  /**
   * تبديل الشخصية
   */
  switchCharacter(characterId: CharacterId): void {
    const oldCharacter = this.state.currentCharacter;
    this.state.currentCharacter = characterId;
    gameEvents.emit('character_switched', {
      from: oldCharacter,
      to: characterId,
    });
    console.log(`🎭 Switched to character: ${characterId}`);
  }

  /**
   * الانتقال إلى بيئة جديدة
   */
  switchRealm(realmId: RealmId): void {
    const oldRealm = this.state.currentRealm;
    this.state.currentRealm = realmId;
    gameEvents.emit('realm_changed', { from: oldRealm, to: realmId });
    console.log(`🌍 Switched to realm: ${realmId}`);
  }

  /**
   * إضافة عنصر للجرد
   */
  addToInventory(item: InventoryItem): void {
    const existing = this.state.inventory.find((i) => i.itemId === item.itemId);
    if (existing) {
      existing.quantity += item.quantity;
    } else {
      this.state.inventory.push(item);
    }
    gameEvents.emit('inventory_changed', { item, action: 'added' });
  }

  /**
   * إزالة عنصر من الجرد
   */
  removeFromInventory(itemId: string, quantity: number = 1): void {
    const item = this.state.inventory.find((i) => i.itemId === itemId);
    if (item) {
      item.quantity -= quantity;
      if (item.quantity <= 0) {
        this.state.inventory = this.state.inventory.filter(
          (i) => i.itemId !== itemId
        );
      }
      gameEvents.emit('inventory_changed', {
        itemId,
        quantity,
        action: 'removed',
      });
    }
  }

  /**
   * تحديث صحة اللاعب
   */
  updateHealth(amount: number): void {
    const oldHealth = this.state.playerState.health;
    this.state.playerState.health = Math.max(
      0,
      Math.min(this.state.playerState.health + amount, 100)
    );

    if (amount > 0) {
      gameEvents.emit('heal_applied', { amount, newHealth: this.state.playerState.health });
    } else {
      gameEvents.emit('damage_taken', {
        damage: Math.abs(amount),
        newHealth: this.state.playerState.health,
      });
    }

    if (this.state.playerState.health === 0) {
      gameEvents.emit('player_died', { lastHealth: oldHealth });
    }
  }

  /**
   * تحديث الطاقة
   */
  updateEnergy(amount: number): void {
    this.state.playerState.energy = Math.max(
      0,
      Math.min(this.state.playerState.energy + amount, 100)
    );
  }

  /**
   * إضافة الشظايا
   */
  addShards(amount: number): void {
    this.state.playerState.shards += amount;
    gameEvents.emit('shards_added', { amount, total: this.state.playerState.shards });
  }

  /**
   * إضافة الخبرة (تطويرها)
   */
  addExperience(amount: number): void {
    this.state.playerState.experience += amount;
    gameEvents.emit('experience_gained', {
      amount,
      total: this.state.playerState.experience,
    });

    // فحص ترقية المستوى (مثال بسيط)
    if (this.state.playerState.experience >= this.state.playerState.level * 100) {
      this.levelUp();
    }
  }

  /**
   * ترقية المستوى
   */
  private levelUp(): void {
    this.state.playerState.level += 1;
    this.state.playerState.health = 100; // شفاء كامل
    this.state.playerState.energy = 100; // طاقة كاملة
    gameEvents.emit('level_up', { newLevel: this.state.playerState.level });
  }

  /**
   * إضافة مهمة
   */
  addQuest(quest: Quest): void {
    this.state.quests.push(quest);
    this.state.playerState.currentQuests.push(quest.id);
    gameEvents.emit('quest_started', quest);
  }

  /**
   * إكمال مهمة
   */
  completeQuest(questId: string): void {
    const questIndex = this.state.quests.findIndex((q) => q.id === questId);
    if (questIndex > -1) {
      this.state.quests[questIndex].status = 'completed';
      this.state.playerState.currentQuests = this.state.playerState.currentQuests.filter(
        (id) => id !== questId
      );
      this.state.playerState.completedQuests.push(questId);
      gameEvents.emit('quest_completed', {
        questId,
        quest: this.state.quests[questIndex],
      });
    }
  }

  /**
   * فتح إنجاز
   */
  unlockAchievement(achievement: Achievement): void {
    const existing = this.state.achievements.find((a) => a.id === achievement.id);
    if (!existing) {
      achievement.unlocked = true;
      achievement.unlockedAt = Date.now();
      this.state.achievements.push(achievement);
      gameEvents.emit('achievement_unlocked', achievement);
    }
  }

  /**
   * تحديث الطقس
   */
  updateWeather(weatherType: any, intensity: number, duration: number): void {
    this.state.weather = {
      type: weatherType,
      intensity,
      duration,
    };
    gameEvents.emit('weather_changed', this.state.weather);
  }

  /**
   * تحديث الوقت من اليوم
   */
  updateTimeOfDay(minutes: number): void {
    this.state.timeOfDay = minutes % 1440; // دورة 24 ساعة
    gameEvents.emit('time_changed', { timeOfDay: this.state.timeOfDay });
  }

  /**
   * تحديث معدل الإطارات
   */
  updateFPS(fps: number): void {
    this.state.fps = fps;
  }

  /**
   * إيقاف اللعبة
   */
  pauseGame(): void {
    this.state.isPaused = true;
    gameEvents.emit('game_paused', {});
  }

  /**
   * استئناف اللعبة
   */
  resumeGame(): void {
    this.state.isPaused = false;
    gameEvents.emit('game_resumed', {});
  }

  /**
   * بدء اللعبة
   */
  startGame(): void {
    this.state.isRunning = true;
    gameEvents.emit('game_started', {});
  }

  /**
   * إيقاف اللعبة نهائيًا
   */
  stopGame(): void {
    this.state.isRunning = false;
    gameEvents.emit('game_stopped', {});
  }

  /**
   * تحديث الإعدادات
   */
  updateSettings(settings: Partial<GameSettings>): void {
    this.state.settings = {
      ...this.state.settings,
      ...settings,
    };
    gameEvents.emit('settings_changed', this.state.settings);
  }

  /**
   * الحصول على إعدادات محددة
   */
  getSetting(key: keyof GameSettings): any {
    return this.state.settings[key];
  }

  /**
   * إعادة تعيين الحالة
   */
  reset(): void {
    this.state = this.initializeDefaultState();
    gameEvents.emit('game_reset', {});
  }

  /**
   * طباعة حالة اللعبة الحالية (للتطوير)
   */
  printState(): void {
    console.log('📊 Current Game State:', this.state);
  }

  /**
   * الحصول على ملخص الحالة
   */
  getSummary(): string {
    return `
    🎮 GAME STATE SUMMARY
    ─────────────────────
    Character: ${this.state.currentCharacter}
    Realm: ${this.state.currentRealm}
    Health: ${this.state.playerState.health}/100
    Energy: ${this.state.playerState.energy}/100
    Shards: ${this.state.playerState.shards}
    Level: ${this.state.playerState.level}
    Difficulty: ${this.state.settings.difficulty}
    Active Quests: ${this.state.playerState.currentQuests.length}
    Completed Quests: ${this.state.playerState.completedQuests.length}
    Achievements: ${this.state.achievements.length}
    Inventory Items: ${this.state.inventory.length}
    ─────────────────────
    `;
  }
}

// تصدير نسخة واحدة
export const gameState = StateManager.getInstance();
