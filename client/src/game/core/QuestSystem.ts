/**
 * Quest System - نظام المهام
 * إدارة المهام والأهداف والمكافآت
 */

import { Quest, QuestObjective, QuestStatus, InventoryItem } from '../../types/gameTypes';
import { gameEvents } from './EventSystem';
import { gameState } from './StateManager';

export interface QuestTracker {
  questId: string;
  quest: Quest;
  objectives: Map<string, number>; // objectiveId -> progress
  startedAt: number;
  completedAt?: number;
  progress: number; // 0-100%
}

export type QuestFilter = 'active' | 'completed' | 'failed' | 'all';

export class QuestSystem {
  private static instance: QuestSystem;
  private questTrackers: Map<string, QuestTracker> = new Map();
  private questIdCounter: number = 0;
  private questDatabase: Map<string, Quest> = new Map();

  private constructor() {
    this.initializeQuestDatabase();
    console.log('📜 QuestSystem initialized');
  }

  /**
   * الحصول على نسخة واحدة من نظام المهام
   */
  static getInstance(): QuestSystem {
    if (!QuestSystem.instance) {
      QuestSystem.instance = new QuestSystem();
    }
    return QuestSystem.instance;
  }

  /**
   * تهيئة قاعدة بيانات المهام
   */
  private initializeQuestDatabase(): void {
    // مهام الحكاية الرئيسية (Main Quest)
    this.registerQuest({
      id: 'main_01',
      title: 'Awaken in the Ash',
      description: 'Escape the Ash Gate and discover the truth',
      type: 'main',
      difficulty: 1,
      status: 'available',
      objectives: [
        {
          id: 'obj_1',
          description: 'Defeat corrupted guardians',
          type: 'kill',
          targetCount: 5,
          completed: false,
        },
        {
          id: 'obj_2',
          description: 'Reach the Ash Gate exit',
          type: 'location',
          targetCount: 1,
          completed: false,
        },
      ],
      rewards: {
        experience: 500,
        shards: 100,
        items: [],
      },
    });

    this.registerQuest({
      id: 'side_01',
      title: 'Help the Lost Traveler',
      description: 'A traveler in Bell Marsh needs assistance',
      type: 'side',
      difficulty: 1,
      status: 'available',
      objectives: [
        {
          id: 'obj_1',
          description: 'Gather 5 healing herbs',
          type: 'collect',
          targetCount: 5,
          completed: false,
        },
        {
          id: 'obj_2',
          description: 'Return to the traveler',
          type: 'dialogue',
          targetCount: 1,
          completed: false,
        },
      ],
      rewards: {
        experience: 100,
        shards: 50,
        items: [
          {
            itemId: 'healing_potion',
            quantity: 3,
            slot: 'inventory',
            equipped: false,
          },
        ],
      },
    });

    this.registerQuest({
      id: 'daily_01',
      title: 'Daily Hunt',
      description: 'Hunt and defeat enemies for rewards',
      type: 'daily',
      difficulty: 2,
      status: 'available',
      objectives: [
        {
          id: 'obj_1',
          description: 'Defeat 10 enemies',
          type: 'kill',
          targetCount: 10,
          completed: false,
        },
      ],
      rewards: {
        experience: 250,
        shards: 75,
        items: [],
      },
    });

    console.log('✓ Quest database initialized with 3 quests');
  }

  /**
   * تسجيل مهمة في قاعدة البيانات
   */
  registerQuest(quest: Quest): void {
    this.questDatabase.set(quest.id, quest);
  }

  /**
   * بدء مهمة جديدة
   */
  startQuest(questId: string): string | null {
    const quest = this.questDatabase.get(questId);
    if (!quest) {
      console.error(`Quest ${questId} not found`);
      return null;
    }

    if (this.questTrackers.has(questId)) {
      console.warn(`Quest ${questId} is already active`);
      return questId;
    }

    // إنشاء متتبع المهمة
    const tracker: QuestTracker = {
      questId,
      quest: JSON.parse(JSON.stringify(quest)), // نسخة عميقة
      objectives: new Map(),
      startedAt: Date.now(),
      progress: 0,
    };

    // تهيئة الأهداف
    quest.objectives.forEach((obj) => {
      tracker.objectives.set(obj.id, 0);
    });

    this.questTrackers.set(questId, tracker);

    // إضافة إلى حالة اللعبة
    gameState.addQuest(quest);

    gameEvents.emit('quest_started', {
      questId,
      questTitle: quest.title,
    });

    console.log(`📜 Quest started: ${quest.title}`);
    return questId;
  }

  /**
   * تحديث تقدم الهدف
   */
  updateObjectiveProgress(questId: string, objectiveId: string, progress: number): void {
    const tracker = this.questTrackers.get(questId);
    if (!tracker) {
      console.error(`Quest ${questId} not found in active quests`);
      return;
    }

    const currentProgress = tracker.objectives.get(objectiveId) || 0;
    tracker.objectives.set(objectiveId, Math.min(progress, 100));

    // فحص اكتمال المهمة
    this.updateQuestProgress(questId);

    // بث حدث تحديث الهدف
    gameEvents.emit('objective_updated', {
      questId,
      objectiveId,
      progress,
    });

    console.log(`✓ Objective updated: ${objectiveId} -> ${progress}%`);
  }

  /**
   * تحديث تقدم المهمة الكلي
   */
  private updateQuestProgress(questId: string): void {
    const tracker = this.questTrackers.get(questId);
    if (!tracker) return;

    const objectives = Array.from(tracker.objectives.values());
    const totalProgress = objectives.reduce((sum, p) => sum + p, 0) / objectives.length;
    tracker.progress = totalProgress;

    // فحص اكتمال المهمة
    if (totalProgress >= 100) {
      this.completeQuest(questId);
    }
  }

  /**
   * إكمال المهمة
   */
  completeQuest(questId: string): void {
    const tracker = this.questTrackers.get(questId);
    if (!tracker) return;

    tracker.completedAt = Date.now();

    // إضافة المكافآت
    const rewards = tracker.quest.rewards;
    if (rewards.experience) {
      gameState.addExperience(rewards.experience);
    }
    if (rewards.shards) {
      gameState.addShards(rewards.shards);
    }
    if (rewards.items) {
      rewards.items.forEach((item) => {
        gameState.addToInventory(item);
      });
    }

    // تحديث حالة اللعبة
    gameState.completeQuest(questId);

    gameEvents.emit('quest_completed', {
      questId,
      questTitle: tracker.quest.title,
      rewards,
    });

    console.log(`🎉 Quest completed: ${tracker.quest.title}`);
  }

  /**
   * فشل المهمة
   */
  failQuest(questId: string): void {
    const tracker = this.questTrackers.get(questId);
    if (!tracker) return;

    tracker.quest.status = 'failed';

    this.questTrackers.delete(questId);

    gameEvents.emit('quest_failed', {
      questId,
      questTitle: tracker.quest.title,
    });

    console.log(`❌ Quest failed: ${tracker.quest.title}`);
  }

  /**
   * التخلي عن المهمة
   */
  abandonQuest(questId: string): void {
    const tracker = this.questTrackers.get(questId);
    if (!tracker) return;

    this.questTrackers.delete(questId);

    gameEvents.emit('quest_abandoned', {
      questId,
      questTitle: tracker.quest.title,
    });

    console.log(`⚠️ Quest abandoned: ${tracker.quest.title}`);
  }

  /**
   * الحصول على المهام النشطة
   */
  getActiveQuests(): QuestTracker[] {
    return Array.from(this.questTrackers.values());
  }

  /**
   * الحصول على مهمة محددة
   */
  getQuest(questId: string): QuestTracker | undefined {
    return this.questTrackers.get(questId);
  }

  /**
   * الحصول على مهام حسب النوع
   */
  getQuestsByType(type: 'main' | 'side' | 'daily'): QuestTracker[] {
    return Array.from(this.questTrackers.values()).filter((tracker) => tracker.quest.type === type);
  }

  /**
   * الحصول على مهام حسب الصعوبة
   */
  getQuestsByDifficulty(difficulty: number): QuestTracker[] {
    return Array.from(this.questTrackers.values()).filter((tracker) => tracker.quest.difficulty === difficulty);
  }

  /**
   * الحصول على مهام من قاعدة البيانات
   */
  getAvailableQuests(): Quest[] {
    return Array.from(this.questDatabase.values()).filter((q) => q.status === 'available');
  }

  /**
   * فحص ما إذا كانت المهمة نشطة
   */
  isQuestActive(questId: string): boolean {
    return this.questTrackers.has(questId);
  }

  /**
   * طباعة معلومات المهام النشطة
   */
  printActiveQuests(): void {
    const quests = this.getActiveQuests();
    console.log('📜 ACTIVE QUESTS:');
    quests.forEach((tracker, index) => {
      console.log(`
      ${index + 1}. ${tracker.quest.title}
         Type: ${tracker.quest.type}
         Difficulty: ${tracker.quest.difficulty}
         Progress: ${tracker.progress.toFixed(1)}%
         Objectives: ${tracker.objectives.size}`);
    });
  }

  /**
   * طباعة تفاصيل المهمة
   */
  printQuestDetails(questId: string): void {
    const tracker = this.questTrackers.get(questId);
    if (!tracker) {
      console.log(`Quest ${questId} not found`);
      return;
    }

    console.log(`
    📜 QUEST: ${tracker.quest.title}
    ─────────────────────
    ID: ${questId}
    Type: ${tracker.quest.type}
    Difficulty: ${tracker.quest.difficulty}
    Description: ${tracker.quest.description}

    Progress: ${tracker.progress.toFixed(1)}%

    Objectives:
    ${tracker.quest.objectives
      .map((obj, i) => {
        const progress = tracker.objectives.get(obj.id) || 0;
        return `  ${i + 1}. ${obj.description} (${progress}/${obj.targetCount})`;
      })
      .join('\n')}

    Rewards:
      Experience: ${tracker.quest.rewards.experience}
      Shards: ${tracker.quest.rewards.shards}
      Items: ${tracker.quest.rewards.items?.length || 0}

    ─────────────────────
    `);
  }

  /**
   * طباعة إحصائيات المهام
   */
  printQuestStats(): void {
    const allQuests = this.getActiveQuests();
    const byType = {
      main: this.getQuestsByType('main').length,
      side: this.getQuestsByType('side').length,
      daily: this.getQuestsByType('daily').length,
    };

    const avgProgress = allQuests.length > 0 ? allQuests.reduce((sum, q) => sum + q.progress, 0) / allQuests.length : 0;

    console.log(`
    📊 QUEST STATISTICS
    ─────────────────────
    Total Active: ${allQuests.length}

    By Type:
      Main Quests: ${byType.main}
      Side Quests: ${byType.side}
      Daily Quests: ${byType.daily}

    Average Progress: ${avgProgress.toFixed(1)}%
    Database Size: ${this.questDatabase.size}
    ─────────────────────
    `);
  }
}

// تصدير نسخة واحدة
export const questSystem = QuestSystem.getInstance();
