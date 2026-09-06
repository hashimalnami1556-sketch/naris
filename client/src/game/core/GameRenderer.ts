/**
 * Game Renderer - محرك العرض
 * إدارة مشهد Babylon.js وتصيير اللعبة
 */

import * as BABYLON from 'babylonjs';
import { config } from './ConfigManager';
import { gameState } from './StateManager';
import { gameEvents } from './EventSystem';
import { characterFactory } from './CharacterFactory';

export class GameRenderer {
  private static instance: GameRenderer;
  private canvas: HTMLCanvasElement | null = null;
  private engine: BABYLON.Engine | null = null;
  private scene: BABYLON.Scene | null = null;
  private camera: BABYLON.ArcRotateCamera | null = null;
  private light: BABYLON.Light | null = null;
  private isInitialized: boolean = false;
  private lastFrameTime: number = 0;
  private frameCount: number = 0;
  private fpsSamples: number[] = [];

  private constructor() {
    console.log('🎮 GameRenderer initialized');
  }

  /**
   * الحصول على نسخة واحدة من محرك العرض
   */
  static getInstance(): GameRenderer {
    if (!GameRenderer.instance) {
      GameRenderer.instance = new GameRenderer();
    }
    return GameRenderer.instance;
  }

  /**
   * تهيئة محرك العرض
   */
  async initialize(canvasId: string = 'game-canvas'): Promise<void> {
    try {
      // الحصول على عنصر Canvas
      this.canvas = document.getElementById(canvasId) as HTMLCanvasElement;
      if (!this.canvas) {
        throw new Error(`Canvas element with id "${canvasId}" not found`);
      }

      // إنشاء محرك Babylon.js
      this.engine = new BABYLON.Engine(
        this.canvas,
        true,
        {
          antialias: true,
          stencil: true,
          preserveDrawingBuffer: false,
          doNotHandleContextLost: false,
        }
      );

      // إنشاء المشهد
      this.scene = new BABYLON.Scene(this.engine);
      this.scene.collisionsEnabled = true;
      this.scene.fogEnabled = false;

      // إضافة الأضواء
      this.setupLighting();

      // إضافة الكاميرا
      this.setupCamera();

      // إضافة السماء والأرضية
      this.setupEnvironment();

      // تعيين المشهد للمصانع
      characterFactory.setScene(this.scene);

      // معالجة تغيير حجم النافذة
      window.addEventListener('resize', () => this.onWindowResize());

      // دورة التصيير الرئيسية
      this.engine.runRenderLoop(() => this.render());

      this.isInitialized = true;
      gameEvents.emit('renderer_initialized', {});
      console.log('✓ GameRenderer initialized successfully');
    } catch (error) {
      console.error('Failed to initialize GameRenderer:', error);
      throw error;
    }
  }

  /**
   * إعداد الإضاءة
   */
  private setupLighting(): void {
    if (!this.scene) return;

    // ضوء الشمس الرئيسي
    const sunLight = new BABYLON.DirectionalLight('sunLight', new BABYLON.Vector3(-1, -2, -1), this.scene);
    sunLight.intensity = 0.8;
    sunLight.range = 1000;

    // ضوء محيطي
    const ambientLight = new BABYLON.HemisphericLight('ambientLight', new BABYLON.Vector3(0, 1, 0), this.scene);
    ambientLight.intensity = 0.5;
    ambientLight.groundColor = new BABYLON.Color3(0.2, 0.2, 0.25);

    this.light = sunLight;
    console.log('✓ Lighting setup complete');
  }

  /**
   * إعداد الكاميرا
   */
  private setupCamera(): void {
    if (!this.scene || !this.canvas) return;

    // كاميرا ثلاثية الأبعاد دوارة
    this.camera = new BABYLON.ArcRotateCamera(
      'camera',
      Math.PI / 4, // alpha (rotation around Y-axis)
      Math.PI / 3, // beta (rotation around X-axis)
      25, // radius
      BABYLON.Vector3.Zero() // target
    );

    this.camera.attachControl(this.canvas, true);
    this.camera.inertia = 0.8;
    this.camera.angularSensibilityX = 1000;
    this.camera.angularSensibilityY = 1000;
    this.camera.wheelPrecision = 50;

    // حدود الكاميرا
    this.camera.lowerRadiusLimit = 5;
    this.camera.upperRadiusLimit = 50;
    this.camera.lowerBetaLimit = 0.1;
    this.camera.upperBetaLimit = Math.PI * 0.9;

    console.log('✓ Camera setup complete');
  }

  /**
   * إعداد البيئة (السماء والأرضية)
   */
  private setupEnvironment(): void {
    if (!this.scene) return;

    // لون السماء
    this.scene.clearColor = new BABYLON.Color3(0.15, 0.15, 0.2);

    // إنشاء أرضية بسيطة
    const ground = BABYLON.MeshBuilder.CreateGround('ground', { width: 200, height: 200 }, this.scene);
    const groundMaterial = new BABYLON.StandardMaterial('groundMaterial', this.scene);
    groundMaterial.diffuse = new BABYLON.Color3(0.3, 0.3, 0.35);
    groundMaterial.specularColor = new BABYLON.Color3(0.1, 0.1, 0.1);
    ground.material = groundMaterial;
    ground.checkCollisions = true;

    // إنشاء سماء (skybox)
    const skybox = BABYLON.MeshBuilder.CreateBox('skybox', { size: 500 }, this.scene);
    const skyboxMaterial = new BABYLON.StandardMaterial('skyboxMaterial', this.scene);
    skyboxMaterial.emissiveColor = new BABYLON.Color3(0.2, 0.2, 0.25);
    skyboxMaterial.backFaceCulling = false;
    skybox.material = skyboxMaterial;

    console.log('✓ Environment setup complete');
  }

  /**
   * دورة التصيير الرئيسية
   */
  private render(): void {
    if (!this.engine || !this.scene) return;

    // حساب FPS
    this.updateFrameStats();

    // تحديث حالة اللعبة
    gameState.updateFPS(Math.round(1000 / (Date.now() - this.lastFrameTime)));

    // بث حدث تحديث الإطار
    gameEvents.emit('frame_update', {
      deltaTime: Date.now() - this.lastFrameTime,
    });

    // تصيير المشهد
    this.scene.render();

    this.lastFrameTime = Date.now();
  }

  /**
   * تحديث إحصائيات الإطارات
   */
  private updateFrameStats(): void {
    this.frameCount++;
    const now = Date.now();

    if (!this.fpsSamples) {
      this.fpsSamples = [];
    }

    if (this.lastFrameTime > 0) {
      const deltaTime = now - this.lastFrameTime;
      const fps = 1000 / deltaTime;
      this.fpsSamples.push(fps);

      if (this.fpsSamples.length > 60) {
        this.fpsSamples.shift();
      }
    }
  }

  /**
   * الحصول على متوسط FPS
   */
  getAverageFPS(): number {
    if (this.fpsSamples.length === 0) return 0;
    const sum = this.fpsSamples.reduce((a, b) => a + b, 0);
    return sum / this.fpsSamples.length;
  }

  /**
   * معالجة تغيير حجم النافذة
   */
  private onWindowResize(): void {
    if (this.engine) {
      this.engine.resize();
      console.log('✓ Engine resized');
    }
  }

  /**
   * تعيين هدف الكاميرا
   */
  setCameraTarget(target: BABYLON.Vector3): void {
    if (this.camera) {
      this.camera.target = target;
    }
  }

  /**
   * تعيين موضع الكاميرا
   */
  setCameraPosition(position: BABYLON.Vector3): void {
    if (this.camera) {
      this.camera.position = position;
    }
  }

  /**
   * الحصول على المشهد
   */
  getScene(): BABYLON.Scene | null {
    return this.scene;
  }

  /**
   * الحصول على المحرك
   */
  getEngine(): BABYLON.Engine | null {
    return this.engine;
  }

  /**
   * الحصول على الكاميرا
   */
  getCamera(): BABYLON.ArcRotateCamera | null {
    return this.camera;
  }

  /**
   * فحص حالة التهيئة
   */
  isReady(): boolean {
    return this.isInitialized && this.engine !== null && this.scene !== null;
  }

  /**
   * تفعيل/تعطيل الكاميرا
   */
  setCameraEnabled(enabled: boolean): void {
    if (this.camera) {
      this.camera.attachControl(this.canvas, enabled);
    }
  }

  /**
   * التقاط لقطة شاشة
   */
  async takeScreenshot(filename: string = 'screenshot'): Promise<void> {
    if (!this.engine) return;

    try {
      BABYLON.Tools.CreateScreenshot(this.engine, this.camera, 1920, 1080, filename);
      console.log(`✓ Screenshot saved: ${filename}`);
    } catch (error) {
      console.error('Failed to take screenshot:', error);
    }
  }

  /**
   * طباعة معلومات المحرك
   */
  printEngineInfo(): void {
    if (!this.engine || !this.scene) {
      console.log('Engine not initialized');
      return;
    }

    const renderingCanvas = this.engine.getRenderingCanvas();
    console.log(`
    🎮 ENGINE INFO
    ─────────────────────
    Canvas: ${renderingCanvas?.width}x${renderingCanvas?.height}
    Render Target Size: ${this.engine.getRenderWidth()}x${this.engine.getRenderHeight()}
    WebGL Version: ${this.engine.webGLVersion}

    Scene:
      Active Meshes: ${this.scene.getActiveMeshes().length}
      Total Meshes: ${this.scene.meshes.length}
      Lights: ${this.scene.lights.length}
      Cameras: ${this.scene.cameras.length}

    Performance:
      Average FPS: ${this.getAverageFPS().toFixed(1)}
      Frame Count: ${this.frameCount}

    Features:
      Collisions: ${this.scene.collisionsEnabled}
      Fog: ${this.scene.fogEnabled}
      Shadows: ${this.scene.shadowsEnabled}
    ─────────────────────
    `);
  }

  /**
   * تنظيف الموارد
   */
  dispose(): void {
    if (this.scene) {
      this.scene.dispose();
    }

    if (this.engine) {
      this.engine.dispose();
    }

    this.isInitialized = false;
    gameEvents.emit('renderer_disposed', {});
    console.log('🗑️ GameRenderer disposed');
  }
}

// تصدير نسخة واحدة
export const gameRenderer = GameRenderer.getInstance();
