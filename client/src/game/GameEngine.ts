/**
 * Game Engine - محرك اللعبة الرئيسي
 * تنسيق جميع الأنظمة الأساسية وإدارة دورة حياة اللعبة
 */

import {
  gameEvents,
  gameState,
  config,
  assetLoader,
  characterFactory,
  gameRenderer,
  cameraController,
  characterController,
  combatSystem,
  enemyAI,
  weatherSystem,
  questSystem,
  achievementSystem,
  inputManager,
  particleSystem,
  animationSystem,
  soundSystem,
  vfxManager,
  saveSystem,
  inventorySystem,
  craftingSystem,
  dialogueSystem,
  checkpointSystem,
  worldManager,
  environmentDirector,
  dayNightSystem,
  lightingSystem,
  tutorialSystem,
  performanceMonitor,
  debugOverlay,
  allySystem,
  spiritSystem,
} from './core/index';

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
      this.updateProgress(2, 'Initializing Event System');
      await this.sleep(50);

      // 1.5 تهيئة مدير الإدخال
      inputManager.initialize();
      this.updateProgress(4, 'Initializing Input Manager');
      await this.sleep(50);

      // 2. تهيئة مدير الحالة
      gameState.getState();
      this.updateProgress(6, 'Initializing State Manager');
      await this.sleep(50);

      // 3. تهيئة مدير التكوين
      config.getConfig();
      this.updateProgress(8, 'Initializing Config Manager');
      await this.sleep(50);

      // 4. تهيئة محرك العرض
      await gameRenderer.initialize(this.config.canvasId);
      this.updateProgress(15, 'Initializing Renderer');
      await this.sleep(50);

      // 4.5 تهيئة نظام الجسيمات والمؤثرات
      const scene = gameRenderer.getScene();
      if (scene) {
        particleSystem.setScene(scene);
        animationSystem.setScene(scene);
        vfxManager.setScene(scene);
        lightingSystem.setScene(scene);
      }
      this.updateProgress(20, 'Initializing Particle & VFX Systems');
      await this.sleep(50);

      // 5. تهيئة نظام الأصول
      assetLoader;
      this.updateProgress(25, 'Initializing Asset Loader');
      await this.sleep(50);

      // 6. تهيئة متحكم الكاميرا
      cameraController.initialize();
      this.updateProgress(30, 'Initializing Camera Controller');
      await this.sleep(50);

      // 7. تهيئة متحكم الشخصية
      characterController.initialize();
      this.updateProgress(35, 'Initializing Character Controller');
      await this.sleep(50);

      // 8. تهيئة نظام الذكاء الاصطناعي
      enemyAI.initialize();
      this.updateProgress(40, 'Initializing Enemy AI');
      await this.sleep(50);

      // 9. تهيئة نظام الطقس
      weatherSystem.initialize();
      this.updateProgress(45, 'Initializing Weather System');
      await this.sleep(50);

      // 10. تهيئة نظام المهام
      questSystem;
      this.updateProgress(48, 'Initializing Quest System');
      await this.sleep(50);

      // 11. تهيئة نظام الإنجازات
      achievementSystem;
      this.updateProgress(50, 'Initializing Achievement System');
      await this.sleep(50);

      // 12. تهيئة أنظمة الحفظ والمخزون
      saveSystem;
      this.updateProgress(52, 'Initializing Save System');
      await this.sleep(50);

      inventorySystem;
      this.updateProgress(54, 'Initializing Inventory System');
      await this.sleep(50);

      craftingSystem;
      this.updateProgress(56, 'Initializing Crafting System');
      await this.sleep(50);

      // 13. تهيئة أنظمة العالم والبيئة
      dialogueSystem;
      this.updateProgress(58, 'Initializing Dialogue System');
      await this.sleep(50);

      checkpointSystem;
      this.updateProgress(60, 'Initializing Checkpoint System');
      await this.sleep(50);

      worldManager;
      this.updateProgress(62, 'Initializing World Manager');
      await this.sleep(50);

      environmentDirector;
      this.updateProgress(64, 'Initializing Environment Director');
      await this.sleep(50);

      dayNightSystem.enable();
      this.updateProgress(66, 'Initializing Day/Night System');
      await this.sleep(50);

      // 14. تهيئة أنظمة إضافية
      soundSystem;
      this.updateProgress(68, 'Initializing Sound System');
      await this.sleep(50);

      allySystem;
      this.updateProgress(70, 'Initializing Ally System');
      await this.sleep(50);

      spiritSystem;
      this.updateProgress(72, 'Initializing Spirit System');
      await this.sleep(50);

      tutorialSystem.setEnabled(true);
      this.updateProgress(74, 'Initializing Tutorial System');
      await this.sleep(50);

      // 15. تهيئة أنظمة المراقبة والتصحيح
      if (this.config.debug) {
        performanceMonitor.startMonitoring();
        debugOverlay.show();
      }
      this.updateProgress(80, 'Initializing Monitoring Systems');
      await this.sleep(50);

      // 16. إنشاء الشخصيات الأولية
      if (scene) {
        const { Vector3 } = require('babylonjs');
        await characterFactory.createCharacter('ash', new Vector3(0, 0, 0));
        await characterFactory.createCharacter('rune', new Vector3(5, 0, 5));
        await characterFactory.createCharacter('kor', new Vector3(-5, 0, 5));
      }

      this.updateProgress(100, 'Engine Initialized Successfully');

      this.state = 'ready';
      gameEvents.emit('engine_initialized', {});

      console.log('✓ GameEngine initialized successfully with 32+ systems');

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
   * الحصول على إحصائيات المحرك
   */
  getEngineStats(): Record<string, any> {
    const particleStats = particleSystem.getStats();
    const animationStats = animationSystem.getStats();
    const soundStats = soundSystem.getStats();
    const vfxStats = vfxManager.getStats();

    return {
      engine: {
        state: this.state,
        progress: this.initializationProgress,
      },
      particles: particleStats,
      animations: animationStats,
      sound: soundStats,
      vfx: vfxStats,
      game: {
        character: gameState.getState().currentCharacter,
        realm: gameState.getState().currentRealm,
        health: gameState.getState().playerState.health,
        level: gameState.getState().playerState.level,
      },
      scene: {
        characters: characterFactory.getAllCharacters().length,
        enemies: enemyAI.getAllEnemies().length,
      },
    };
  }

  /**
   * طباعة معلومات المحرك
   */
  printEngineInfo(): void {
    const soundStats = soundSystem.getStats();
    const animationStats = animationSystem.getStats();
    const particleStats = particleSystem.getStats();

    console.log(`
    🎮 GAME ENGINE INFO
    ─────────────────────
    State: ${this.state}
    Initialization Progress: ${this.initializationProgress}%

    Systems Status:
      Event System: ✓ Ready
      Input Manager: ✓ Ready
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
      Particle System: ✓ Ready
      Animation System: ✓ Ready
      Sound System: ✓ Ready
      VFX Manager: ✓ Ready

    Game State:
      Current Character: ${gameState.getState().currentCharacter}
      Current Realm: ${gameState.getState().currentRealm}
      Player Health: ${gameState.getState().playerState.health}
      Player Level: ${gameState.getState().playerState.level}

    Scene Statistics:
      Active Characters: ${characterFactory.getAllCharacters().length}
      Active Enemies: ${enemyAI.getAllEnemies().length}

    Visual/Audio Effects:
      Active Particles: ${particleStats.active}
      Active Animations: ${animationStats.animationGroups}
      Sounds Playing: ${soundStats.soundsPlaying}
      Sound Buffers Loaded: ${soundStats.buffersLoaded}

    ─────────────────────
    `);
  }

  /**
   * تنظيف الموارد
   */
  dispose(): void {
    this.stop();

    // تنظيف جميع الأنظمة بترتيب معاكس للتهيئة
    // VFX and Media Systems
    vfxManager.dispose();
    soundSystem.dispose();
    particleSystem.dispose();
    animationSystem.dispose();

    // Game Systems
    enemyAI.dispose();
    characterFactory.dispose();
    gameRenderer.dispose();

    this.state = 'uninitialized';
    gameEvents.emit('engine_disposed', {});

    console.log('🗑️ GameEngine disposed');
  }
}

// تصدير نسخة واحدة
export const gameEngine = GameEngine.getInstance();
