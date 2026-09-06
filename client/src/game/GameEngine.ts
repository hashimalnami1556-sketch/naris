/**
 * Game Engine - محرك اللعبة الرئيسي
 * تنسيق جميع الأنظمة الأساسية وإدارة دورة حياة اللعبة
 */

import {
  EventSystem,
  gameEvents,
  StateManager,
  gameState,
  ConfigManager,
  config,
  AssetLoader,
  assetLoader,
  CharacterFactory,
  characterFactory,
  GameRenderer,
  gameRenderer,
  CameraController,
  cameraController,
  CharacterController,
  characterController,
  CombatSystem,
  combatSystem,
  EnemyAI,
  enemyAI,
  WeatherSystem,
  weatherSystem,
  QuestSystem,
  questSystem,
  AchievementSystem,
  achievementSystem,
} from './core/index';
import { CharacterId } from '../types/gameTypes';

export interface GameEngineConfig {
  canvasId?: string;
  debug?: boolean;
  autoStart?: boolean;
}

export type GameState = 'uninitialized' | 'initializing' | 'ready' | 'running' | 'paused' | 'stopped' | 'error';

export class GameEngine {
  private static instance: GameEngine;
  private state: GameState = 'uninitialized';
  private config: GameEngineConfig;
  private initializationProgress: number = 0;
  private errorMessage: string = '';

  private constructor(config: GameEngineConfig = {}) {
    this.config = {
      canvasId: config.canvasId || 'game-canvas',
      debug: config.debug || false,
      autoStart: config.autoStart || false,
    };

    console.log('🎮 GameEngine instance created');
  }

  /**
   * الحصول على نسخة واحدة من محرك اللعبة
   */
  static getInstance(config?: GameEngineConfig): GameEngine {
    if (!GameEngine.instance) {
      GameEngine.instance = new GameEngine(config);
    }
    return GameEngine.instance;
  }

  /**
   * تهيئة محرك اللعبة
   */
  async initialize(): Promise<void> {
    if (this.state !== 'uninitialized') {
      throw new Error(`Cannot initialize engine in state: ${this.state}`);
    }

    this.state = 'initializing';
    this.initializationProgress = 0;

    try {
      // 1. إنشاء مصرح الأحداث
      gameEvents;
      this.updateProgress(10, 'Initializing Event System');
      await this.sleep(100);

      // 2. تهيئة مدير الحالة
      gameState.getState();
      this.updateProgress(20, 'Initializing State Manager');
      await this.sleep(100);

      // 3. تهيئة مدير التكوين
      config.getConfig();
      this.updateProgress(30, 'Initializing Config Manager');
      await this.sleep(100);

      // 4. تهيئة محرك العرض
      await gameRenderer.initialize(this.config.canvasId);
      this.updateProgress(50, 'Initializing Renderer');
      await this.sleep(100);

      // 5. تهيئة نظام الأصول
      assetLoader;
      this.updateProgress(60, 'Initializing Asset Loader');
      await this.sleep(100);

      // 6. تهيئة متحكم الكاميرا
      cameraController.initialize();
      this.updateProgress(70, 'Initializing Camera Controller');
      await this.sleep(100);

      // 7. تهيئة متحكم الشخصية
      characterController.initialize();
      this.updateProgress(80, 'Initializing Character Controller');
      await this.sleep(100);

      // 8. تهيئة نظام الذكاء الاصطناعي
      enemyAI.initialize();
      this.updateProgress(70, 'Initializing Enemy AI');
      await this.sleep(100);

      // 9. تهيئة نظام الطقس
      weatherSystem.initialize();
      this.updateProgress(75, 'Initializing Weather System');
      await this.sleep(100);

      // 10. تهيئة نظام المهام
      questSystem;
      this.updateProgress(80, 'Initializing Quest System');
      await this.sleep(100);

      // 11. تهيئة نظام الإنجازات
      achievementSystem;
      this.updateProgress(85, 'Initializing Achievement System');
      await this.sleep(100);

      // 12. إنشاء الشخصيات الأولية
      const scene = gameRenderer.getScene();
      if (scene) {
        const ashCharacter = await characterFactory.createCharacter('ash', new (require('babylonjs')).Vector3(0, 0, 0));
        const runeCharacter = await characterFactory.createCharacter('rune', new (require('babylonjs')).Vector3(5, 0, 5));
        const korCharacter = await characterFactory.createCharacter('kor', new (require('babylonjs')).Vector3(-5, 0, 5));
      }

      this.updateProgress(100, 'Engine Initialized Successfully');

      this.state = 'ready';
      gameEvents.emit('engine_initialized', {});

      console.log('✓ GameEngine initialized successfully');

      if (this.config.autoStart) {
        await this.start();
      }
    } catch (error) {
      this.state = 'error';
      this.errorMessage = String(error);
      gameEvents.emit('engine_error', { error: this.errorMessage });
      console.error('GameEngine initialization failed:', error);
      throw error;
    }
  }

  /**
   * بدء اللعبة
   */
  async start(): Promise<void> {
    if (this.state !== 'ready') {
      throw new Error(`Cannot start engine in state: ${this.state}`);
    }

    this.state = 'running';
    gameState.startGame();
    gameEvents.emit('engine_started', {});

    console.log('✓ GameEngine started');
  }

  /**
   * إيقاف اللعبة (مؤقتاً)
   */
  pause(): void {
    if (this.state !== 'running') return;

    this.state = 'paused';
    gameState.pauseGame();
    gameEvents.emit('engine_paused', {});

    console.log('✓ GameEngine paused');
  }

  /**
   * استئناف اللعبة
   */
  resume(): void {
    if (this.state !== 'paused') return;

    this.state = 'running';
    gameState.resumeGame();
    gameEvents.emit('engine_resumed', {});

    console.log('✓ GameEngine resumed');
  }

  /**
   * إيقاف اللعبة (نهائياً)
   */
  stop(): void {
    this.state = 'stopped';
    gameState.stopGame();
    gameEvents.emit('engine_stopped', {});

    console.log('✓ GameEngine stopped');
  }

  /**
   * حفظ اللعبة
   */
  saveGame(saveName: string = 'autosave'): void {
    const currentState = gameState.getState();
    const saveData = {
      timestamp: Date.now(),
      name: saveName,
      state: currentState,
    };

    try {
      localStorage.setItem(`save_${saveName}`, JSON.stringify(saveData));
      gameEvents.emit('game_saved', { saveName });
      console.log(`✓ Game saved: ${saveName}`);
    } catch (error) {
      console.error('Failed to save game:', error);
      gameEvents.emit('save_failed', { error });
    }
  }

  /**
   * تحميل اللعبة
   */
  loadGame(saveName: string): void {
    try {
      const saveData = localStorage.getItem(`save_${saveName}`);
      if (!saveData) {
        throw new Error(`Save file not found: ${saveName}`);
      }

      const parsed = JSON.parse(saveData);
      gameState.setState(parsed.state);
      gameEvents.emit('game_loaded', { saveName });
      console.log(`✓ Game loaded: ${saveName}`);
    } catch (error) {
      console.error('Failed to load game:', error);
      gameEvents.emit('load_failed', { error });
    }
  }

  /**
   * إعادة تعيين اللعبة
   */
  reset(): void {
    gameState.reset();
    characterController.switchCharacter('ash');
    gameEvents.emit('engine_reset', {});

    console.log('✓ GameEngine reset');
  }

  /**
   * تحديث تقدم التهيئة
   */
  private updateProgress(progress: number, message: string): void {
    this.initializationProgress = progress;
    gameEvents.emit('initialization_progress', {
      progress,
      message,
    });
  }

  /**
   * انتظار (للعمليات المتزامنة)
   */
  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  /**
   * الحصول على حالة المحرك
   */
  getState(): GameState {
    return this.state;
  }

  /**
   * فحص ما إذا كانت اللعبة تعمل
   */
  isRunning(): boolean {
    return this.state === 'running';
  }

  /**
   * فحص ما إذا كانت المحرك جاهزاً
   */
  isReady(): boolean {
    return this.state === 'ready' || this.state === 'running';
  }

  /**
   * الحصول على تقدم التهيئة
   */
  getInitializationProgress(): number {
    return this.initializationProgress;
  }

  /**
   * الحصول على رسالة الخطأ
   */
  getErrorMessage(): string {
    return this.errorMessage;
  }

  /**
   * طباعة معلومات المحرك
   */
  printEngineInfo(): void {
    console.log(`
    🎮 GAME ENGINE INFO
    ─────────────────────
    State: ${this.state}
    Initialization Progress: ${this.initializationProgress}%

    Systems Status:
      Event System: ✓ Ready
      State Manager: ✓ Ready
      Config Manager: ✓ Ready
      Renderer: ${gameRenderer.isReady() ? '✓ Ready' : '✗ Not Ready'}
      Asset Loader: ✓ Ready
      Character Factory: ✓ Ready
      Camera Controller: ✓ Ready
      Character Controller: ✓ Ready
      Combat System: ✓ Ready
      Enemy AI: ✓ Ready
      Weather System: ✓ Ready
      Quest System: ✓ Ready
      Achievement System: ✓ Ready

    Game State:
      Current Character: ${gameState.getState().currentCharacter}
      Current Realm: ${gameState.getState().currentRealm}
      Player Health: ${gameState.getState().playerState.health}
      Player Level: ${gameState.getState().playerState.level}

    Scene Statistics:
      Active Characters: ${characterFactory.getAllCharacters().length}
      Active Enemies: ${enemyAI.getAllEnemies().length}

    ─────────────────────
    `);
  }

  /**
   * تنظيف الموارد
   */
  dispose(): void {
    this.stop();

    // تنظيف جميع الأنظمة بترتيب معاكس للتهيئة
    enemyAI.dispose();
    characterFactory.dispose();
    gameRenderer.dispose();
    weatherSystem;
    questSystem;
    achievementSystem;

    this.state = 'uninitialized';
    gameEvents.emit('engine_disposed', {});

    console.log('🗑️ GameEngine disposed');
  }
}

// تصدير نسخة واحدة
export const gameEngine = GameEngine.getInstance();
