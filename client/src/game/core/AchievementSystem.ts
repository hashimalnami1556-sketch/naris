/**
 * Achievement System - نظام الإنجازات
 * إدارة الإنجازات والتحديات والجوائز
 */

import { Achievement } from '../../types/gameTypes';
import { gameEvents } from './EventSystem';
import { gameState } from './StateManager';

export interface AchievementTracker {
  achievement: Achievement;
  progress: number; // 0-100%
  unlockedAt?: number;
}

export interface AchievementProgress {
  combatKills: number;
  bossesDefeated: number;
  questsCompleted: number;
  shardCollected: number;
  damageDealt: number;
  damageTaken: number;
  timeSpent: number; // ملي ثانية
}

export class AchievementSystem {
  private static instance: AchievementSystem;
  private achievements: Map<string, AchievementTracker> = new Map();
  private progress: AchievementProgress;
  private achievementDatabase: Map<string, Achievement> = new Map();

  private constructor() {
    this.progress = this.getDefaultProgress();
    this.initializeAchievementDatabase();
    console.log('🏆 AchievementSystem initialized');
  }

  /**
   * الحصول على نسخة واحدة من نظام الإنجازات
   */
  static getInstance(): AchievementSystem {
    if (!AchievementSystem.instance) {
      AchievementSystem.instance = new AchievementSystem();
    }
    return AchievementSystem.instance;
  }

  /**
   * الحصول على التقدم الافتراضي
   */
  private getDefaultProgress(): AchievementProgress {
    return {
      combatKills: 0,
      bossesDefeated: 0,
      questsCompleted: 0,
      shardCollected: 0,
      damageDealt: 0,
      damageTaken: 0,
      timeSpent: 0,
    };
  }

  /**
   * تهيئة قاعدة بيانات الإنجازات
   */
  private initializeAchievementDatabase(): void {
    // إنجازات القتال
    this.registerAchievement({
      id: 'first_blood',
      name: 'First Blood',
      description: 'Defeat your first enemy',
      icon: '🗡️',
      condition: { type: 'enemy_kills', value: 1 },
      unlocked: false,
      reward: { type: 'shards', value: 50 },
    });

    this.registerAchievement({
      id: 'slayer',
      name: 'Slayer',
      description: 'Defeat 50 enemies',
      icon: '⚔️',
      condition: { type: 'enemy_kills', value: 50 },
      unlocked: false,
      reward: { type: 'shards', value: 200 },
    });

    this.registerAchievement({
      id: 'master_slayer',
      name: 'Master Slayer',
      description: 'Defeat 500 enemies',
      icon: '🔥',
      condition: { type: 'enemy_kills', value: 500 },
      unlocked: false,
      reward: { type: 'shards', value: 500 },
    });

    // إنجازات الزعماء
    this.registerAchievement({
      id: 'boss_slayer',
      name: 'Boss Slayer',
      description: 'Defeat your first boss',
      icon: '👑',
      condition: { type: 'boss_kills', value: 1 },
      unlocked: false,
      reward: { type: 'shards', value: 300 },
    });

    // إنجازات المهام
    this.registerAchievement({
      id: 'quest_master',
      name: 'Quest Master',
      description: 'Complete 10 quests',
      icon: '📜',
      condition: { type: 'quests_completed', value: 10 },
      unlocked: false,
      reward: { type: 'shards', value: 250 },
    });

    // إنجازات الاستكشاف
    this.registerAchievement({
      id: 'explorer',
      name: 'Explorer',
      description: 'Discover all realms',
      icon: '🗺️',
      condition: { type: 'realms_visited', value: 3 },
      unlocked: false,
      reward: { type: 'shards', value: 200 },
    });

    // إنجازات الشخصيات
    this.registerAchievement({
      id: 'ash_master',
      name: "Ash's Champion",
      description: 'Reach level 10 with Ash',
      icon: '⚡',
      condition: { type: 'ash_level', value: 10 },
      unlocked: false,
      reward: { type: 'shards', value: 150 },
    });

    this.registerAchievement({
      id: 'rune_master',
      name: "Rune's Champion",
      description: 'Reach level 10 with Rune',
      icon: '✨',
      condition: { type: 'rune_level', value: 10 },
      unlocked: false,
      reward: { type: 'shards', value: 150 },
    });

    this.registerAchievement({
      id: 'kor_master',
      name: "Kor's Champion",
      description: 'Reach level 10 with Kor',
      icon: '💪',
      condition: { type: 'kor_level', value: 10 },
      unlocked: false,
      reward: { type: 'shards', value: 150 },
    });

    // إنجازات التحديات
    this.registerAchievement({
      id: 'no_damage',
      name: 'Untouchable',
      description: 'Complete a level without taking damage',
      icon: '🛡️',
      condition: { type: 'perfect_level', value: 1 },
      unlocked: false,
      reward: { type: 'shards', value: 400 },
    });

    this.registerAchievement({
      id: 'speedrun',
      name: 'Swift',
      description: 'Complete a level under 5 minutes',
      icon: '⚡',
      condition: { type: 'speedrun', value: 1 },
      unlocked: false,
      reward: { type: 'shards', value: 400 },
    });

    console.log('✓ Achievement database initialized with 11 achievements');
  }

  /**
   * تسجيل إنجاز في قاعدة البيانات
   */
  registerAchievement(achievement: Achievement): void {
    this.achievementDatabase.set(achievement.id, achievement);

    // إنشاء متتبع للإنجاز
    if (!this.achievements.has(achievement.id)) {
      this.achievements.set(achievement.id, {
        achievement,
        progress: 0,
      });
    }
  }

  /**
   * تحديث تقدم الإنجاز
   */
  updateProgress(progressKey: keyof AchievementProgress, value: number): void {
    this.progress[progressKey] += value;

    // فحص الإنجازات التي قد تكون مكتملة
    this.checkAchievements();
  }

  /**
   * فحص جميع الإنجازات الممكنة
   */
  private checkAchievements(): void {
    this.achievements.forEach((tracker, achievementId) => {
      if (tracker.achievement.unlocked) return; // تم فتحها بالفعل

      let isUnlocked = false;
      let progress = 0;

      switch (achievementId) {
        case 'first_blood':
          isUnlocked = this.progress.combatKills >= 1;
          progress = Math.min(100, this.progress.combatKills * 100);
          break;

        case 'slayer':
          isUnlocked = this.progress.combatKills >= 50;
          progress = Math.min(100, (this.progress.combatKills / 50) * 100);
          break;

        case 'master_slayer':
          isUnlocked = this.progress.combatKills >= 500;
          progress = Math.min(100, (this.progress.combatKills / 500) * 100);
          break;

        case 'boss_slayer':
          isUnlocked = this.progress.bossesDefeated >= 1;
          progress = Math.min(100, this.progress.bossesDefeated * 100);
          break;

        case 'quest_master':
          isUnlocked = this.progress.questsCompleted >= 10;
          progress = Math.min(100, (this.progress.questsCompleted / 10) * 100);
          break;

        default:
          progress = tracker.progress;
      }

      tracker.progress = progress;

      if (isUnlocked && !tracker.achievement.unlocked) {
        this.unlockAchievement(achievementId);
      }
    });
  }

  /**
   * فتح إنجاز
   */
  unlockAchievement(achievementId: string): void {
    const tracker = this.achievements.get(achievementId);
    if (!tracker || tracker.achievement.unlocked) return;

    tracker.achievement.unlocked = true;
    tracker.achievement.unlockedAt = Date.now();
    tracker.progress = 100;

    // إضافة الجائزة
    if (tracker.achievement.reward) {
      gameState.addShards(tracker.achievement.reward);
    }

    // إضافة إلى حالة اللعبة
    gameState.unlockAchievement(tracker.achievement);

    gameEvents.emit('achievement_unlocked', {
      achievementId,
      title: tracker.achievement.name,
      reward: tracker.achievement.reward,
    });

    console.log(`🏆 Achievement unlocked: ${tracker.achievement.title}`);
  }

  /**
   * الحصول على جميع الإنجازات
   */
  getAllAchievements(): AchievementTracker[] {
    return Array.from(this.achievements.values());
  }

  /**
   * الحصول على الإنجازات المفتوحة
   */
  getUnlockedAchievements(): AchievementTracker[] {
    return Array.from(this.achievements.values()).filter((tracker) => tracker.achievement.unlocked);
  }

  /**
   * الحصول على إنجاز محدد
   */
  getAchievement(achievementId: string): AchievementTracker | undefined {
    return this.achievements.get(achievementId);
  }

  /**
   * الحصول على الإنجازات حسب النوع
   */
  getAchievementsByType(type: AchievementType): AchievementTracker[] {
    return Array.from(this.achievements.values()).filter((tracker) => tracker.achievement.type === type);
  }

  /**
   * فحص ما إذا كان الإنجاز مفتوحاً
   */
  isAchievementUnlocked(achievementId: string): boolean {
    return this.achievements.get(achievementId)?.achievement.unlocked || false;
  }

  /**
   * الحصول على نسبة اكتمال الإنجازات
   */
  getCompletionPercentage(): number {
    const total = this.achievements.size;
    const unlocked = this.getUnlockedAchievements().length;
    return total > 0 ? (unlocked / total) * 100 : 0;
  }

  /**
   * الحصول على إجمالي الشظايا المكتسبة من الإنجازات
   */
  getTotalRewards(): number {
    return this.getUnlockedAchievements().reduce((sum, tracker) => sum + (tracker.achievement.reward || 0), 0);
  }

  /**
   * طباعة معلومات الإنجازات
   */
  printAchievements(): void {
    const achievements = this.getAllAchievements();
    console.log('🏆 ACHIEVEMENTS:');
    achievements.forEach((tracker, index) => {
      const status = tracker.achievement.unlocked ? '✓' : '✗';
      console.log(
        `${status} ${index + 1}. ${tracker.achievement.title} (${tracker.achievement.type}) - ${tracker.progress.toFixed(1)}%`
      );
    });
  }

  /**
   * طباعة تفاصيل الإنجاز
   */
  printAchievementDetails(achievementId: string): void {
    const tracker = this.achievements.get(achievementId);
    if (!tracker) {
      console.log(`Achievement ${achievementId} not found`);
      return;
    }

    console.log(`
    🏆 ACHIEVEMENT: ${tracker.achievement.title}
    ─────────────────────
    Type: ${tracker.achievement.type}
    Rarity: ${tracker.achievement.rarity}
    Progress: ${tracker.progress.toFixed(1)}%
    Status: ${tracker.achievement.unlocked ? 'Unlocked' : 'Locked'}

    Description: ${tracker.achievement.description}
    Condition: ${tracker.achievement.condition}
    Reward: ${tracker.achievement.reward} shards

    ${tracker.achievement.unlockedAt ? `Unlocked at: ${new Date(tracker.achievement.unlockedAt).toLocaleString()}` : 'Not unlocked yet'}
    ─────────────────────
    `);
  }

  /**
   * طباعة إحصائيات الإنجازات
   */
  printAchievementStats(): void {
    const total = this.achievements.size;
    const unlocked = this.getUnlockedAchievements().length;
    const completion = this.getCompletionPercentage();
    const totalRewards = this.getTotalRewards();

    const byType: Record<AchievementType, number> = {
      combat: this.getAchievementsByType('combat').length,
      boss: this.getAchievementsByType('boss').length,
      quest: this.getAchievementsByType('quest').length,
      exploration: this.getAchievementsByType('exploration').length,
      challenge: this.getAchievementsByType('challenge').length,
      character: this.getAchievementsByType('character').length,
      special: this.getAchievementsByType('special').length,
    };

    console.log(`
    🏆 ACHIEVEMENT STATISTICS
    ─────────────────────
    Total: ${total}
    Unlocked: ${unlocked}
    Completion: ${completion.toFixed(1)}%
    Total Rewards: ${totalRewards} shards

    By Type:
      Combat: ${byType.combat}
      Boss: ${byType.boss}
      Quest: ${byType.quest}
      Exploration: ${byType.exploration}
      Challenge: ${byType.challenge}
      Character: ${byType.character}
      Special: ${byType.special}

    Progress:
      Kills: ${this.progress.combatKills}
      Bosses: ${this.progress.bossesDefeated}
      Quests: ${this.progress.questsCompleted}
      Shards: ${this.progress.shardCollected}
      Damage Dealt: ${this.progress.damageDealt}
    ─────────────────────
    `);
  }
}

// تصدير نسخة واحدة
export const achievementSystem = AchievementSystem.getInstance();
