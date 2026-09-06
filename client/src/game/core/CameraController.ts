/**
 * Camera Controller - متحكم الكاميرا
 * إدارة الكاميرا بصيغة الشخص الثالث والسلوكيات السينمائية
 */

import * as BABYLON from 'babylonjs';
import { gameEvents } from './EventSystem';
import { gameRenderer } from './GameRenderer';

export type CameraMode = 'follow' | 'cinematic' | 'free' | 'tactical';

export interface CameraConfig {
  mode: CameraMode;
  distance: number;
  height: number;
  smoothness: number;
  sensitivity: number;
}

export class CameraController {
  private static instance: CameraController;
  private camera: BABYLON.ArcRotateCamera | null = null;
  private target: BABYLON.Vector3 = BABYLON.Vector3.Zero();
  private targetSmooth: BABYLON.Vector3 = BABYLON.Vector3.Zero();
  private mode: CameraMode = 'follow';
  private config: CameraConfig;
  private isEnabled: boolean = true;
  private input: { forward: boolean; backward: boolean; left: boolean; right: boolean } = {
    forward: false,
    backward: false,
    left: false,
    right: false,
  };

  private constructor() {
    this.config = {
      mode: 'follow',
      distance: 20,
      height: 2,
      smoothness: 0.1,
      sensitivity: 1.0,
    };
    console.log('📷 CameraController initialized');
  }

  /**
   * الحصول على نسخة واحدة من متحكم الكاميرا
   */
  static getInstance(): CameraController {
    if (!CameraController.instance) {
      CameraController.instance = new CameraController();
    }
    return CameraController.instance;
  }

  /**
   * تهيئة متحكم الكاميرا
   */
  initialize(): void {
    const renderer = gameRenderer.getInstance();
    this.camera = renderer.getCamera();

    if (!this.camera) {
      throw new Error('Camera not available in renderer');
    }

    // إعداد الكاميرا الابتدائية
    this.camera.inertia = 0.7;
    this.camera.angularSensibilityX = 1000 / this.config.sensitivity;
    this.camera.angularSensibilityY = 1000 / this.config.sensitivity;

    // تسجيل الأحداث
    this.setupInputListeners();
    this.setupEventListeners();

    console.log('✓ CameraController initialized');
  }

  /**
   * إعداد استقبالات الإدخال
   */
  private setupInputListeners(): void {
    document.addEventListener('keydown', (e) => this.onKeyDown(e));
    document.addEventListener('keyup', (e) => this.onKeyUp(e));
    document.addEventListener('wheel', (e) => this.onMouseWheel(e));

    // دعم اللمس على الأجهزة المحمولة
    document.addEventListener('touchstart', (e) => this.onTouchStart(e));
    document.addEventListener('touchmove', (e) => this.onTouchMove(e));
    document.addEventListener('touchend', (e) => this.onTouchEnd(e));
  }

  /**
   * إعداد استقبالات الأحداث
   */
  private setupEventListeners(): void {
    gameEvents.subscribe('frame_update', () => this.update());
    gameEvents.subscribe('character_switched', (event) => {
      const data = event.data as any;
      console.log(`Camera follows character: ${data.to}`);
    });
  }

  /**
   * معالج الضغط على المفاتيح
   */
  private onKeyDown(event: KeyboardEvent): void {
    const key = event.key.toLowerCase();

    switch (key) {
      case 'w':
        this.input.forward = true;
        break;
      case 's':
        this.input.backward = true;
        break;
      case 'a':
        this.input.left = true;
        break;
      case 'd':
        this.input.right = true;
        break;
      case 'c':
        this.cycleCameraMode();
        break;
      case 'f':
        gameRenderer.getInstance().takeScreenshot();
        break;
    }
  }

  /**
   * معالج رفع المفاتيح
   */
  private onKeyUp(event: KeyboardEvent): void {
    const key = event.key.toLowerCase();

    switch (key) {
      case 'w':
        this.input.forward = false;
        break;
      case 's':
        this.input.backward = false;
        break;
      case 'a':
        this.input.left = false;
        break;
      case 'd':
        this.input.right = false;
        break;
    }
  }

  /**
   * معالج عجلة الماوس
   */
  private onMouseWheel(event: WheelEvent): void {
    if (!this.camera) return;

    const delta = event.deltaY > 0 ? 1 : -1;
    const newDistance = this.camera.radius + delta * 2;

    this.camera.radius = BABYLON.Scalar.Clamp(
      newDistance,
      this.camera.lowerRadiusLimit || 5,
      this.camera.upperRadiusLimit || 50
    );
  }

  /**
   * معالج بدء اللمس
   */
  private onTouchStart(event: TouchEvent): void {
    // معالجة اللمس المزدوج للتكبير/التصغير
    if (event.touches.length === 2) {
      const distance = this.getTouchDistance(event.touches[0], event.touches[1]);
      (this as any).lastTouchDistance = distance;
    }
  }

  /**
   * معالج حركة اللمس
   */
  private onTouchMove(event: TouchEvent): void {
    if (event.touches.length === 2 && !this.camera) return;

    if (event.touches.length === 2) {
      const distance = this.getTouchDistance(event.touches[0], event.touches[1]);
      const delta = distance - ((this as any).lastTouchDistance || distance);

      const newDistance = this.camera!.radius - delta * 0.1;
      this.camera!.radius = BABYLON.Scalar.Clamp(
        newDistance,
        this.camera!.lowerRadiusLimit || 5,
        this.camera!.upperRadiusLimit || 50
      );

      (this as any).lastTouchDistance = distance;
    }
  }

  /**
   * معالج نهاية اللمس
   */
  private onTouchEnd(event: TouchEvent): void {
    delete (this as any).lastTouchDistance;
  }

  /**
   * حساب المسافة بين نقطتي لمس
   */
  private getTouchDistance(touch1: Touch, touch2: Touch): number {
    const dx = touch2.clientX - touch1.clientX;
    const dy = touch2.clientY - touch1.clientY;
    return Math.sqrt(dx * dx + dy * dy);
  }

  /**
   * تحديث الكاميرا كل إطار
   */
  private update(): void {
    if (!this.camera || !this.isEnabled) return;

    switch (this.mode) {
      case 'follow':
        this.updateFollowMode();
        break;
      case 'cinematic':
        this.updateCinematicMode();
        break;
      case 'free':
        this.updateFreeMode();
        break;
      case 'tactical':
        this.updateTacticalMode();
        break;
    }

    // تطبيق الحركة الناعمة
    this.applyCameraSmoothing();
  }

  /**
   * تحديث وضع المتابعة
   */
  private updateFollowMode(): void {
    if (!this.camera) return;

    // في وضع المتابعة، تتابع الكاميرا الشخصية الحالية
    // سيتم تحديث الهدف من نظام الحركة
    const moveAmount = 0.5;

    if (this.input.forward) {
      this.targetSmooth.z -= moveAmount;
    }
    if (this.input.backward) {
      this.targetSmooth.z += moveAmount;
    }
    if (this.input.left) {
      this.targetSmooth.x -= moveAmount;
    }
    if (this.input.right) {
      this.targetSmooth.x += moveAmount;
    }
  }

  /**
   * تحديث الوضع السينمائي
   */
  private updateCinematicMode(): void {
    if (!this.camera) return;

    // دوران سلس حول الهدف
    const time = Date.now() * 0.0005;
    const angle = Math.sin(time) * 0.3;

    if (this.camera.alpha !== undefined) {
      this.camera.alpha += angle * 0.01;
    }
  }

  /**
   * تحديث الوضع الحر
   */
  private updateFreeMode(): void {
    if (!this.camera) return;

    // السماح للاعب بالتحكم الكامل في الكاميرا
    const moveAmount = 1;

    if (this.input.forward) {
      this.targetSmooth.y += moveAmount;
    }
    if (this.input.backward) {
      this.targetSmooth.y -= moveAmount;
    }
    if (this.input.left) {
      this.targetSmooth.x -= moveAmount;
    }
    if (this.input.right) {
      this.targetSmooth.x += moveAmount;
    }
  }

  /**
   * تحديث الوضع التكتيكي (العلوي)
   */
  private updateTacticalMode(): void {
    if (!this.camera) return;

    // عرض من الأعلى بزاوية ثابتة
    if (this.camera.beta !== undefined) {
      this.camera.beta = Math.PI / 4;
    }

    const moveAmount = 1;

    if (this.input.forward) {
      this.targetSmooth.z -= moveAmount;
    }
    if (this.input.backward) {
      this.targetSmooth.z += moveAmount;
    }
    if (this.input.left) {
      this.targetSmooth.x -= moveAmount;
    }
    if (this.input.right) {
      this.targetSmooth.x += moveAmount;
    }
  }

  /**
   * تطبيق التنعيم على الكاميرا
   */
  private applyCameraSmoothing(): void {
    if (!this.camera) return;

    this.target = BABYLON.Vector3.Lerp(
      this.target,
      this.targetSmooth,
      this.config.smoothness
    );

    this.camera.target = this.target;
  }

  /**
   * تحديث موضع الهدف
   */
  setTargetPosition(position: BABYLON.Vector3): void {
    this.targetSmooth = position.clone();
  }

  /**
   * تغيير وضع الكاميرا
   */
  setMode(mode: CameraMode): void {
    if (mode === this.mode) return;

    this.mode = mode;
    gameEvents.emit('camera_mode_changed', { mode });
    console.log(`✓ Camera mode: ${mode}`);
  }

  /**
   * التنقل بين أوضاع الكاميرا
   */
  cycleCameraMode(): void {
    const modes: CameraMode[] = ['follow', 'cinematic', 'free', 'tactical'];
    const currentIndex = modes.indexOf(this.mode);
    const nextIndex = (currentIndex + 1) % modes.length;
    this.setMode(modes[nextIndex]);
  }

  /**
   * الحصول على الوضع الحالي
   */
  getMode(): CameraMode {
    return this.mode;
  }

  /**
   * تعطيل/تفعيل متحكم الكاميرا
   */
  setEnabled(enabled: boolean): void {
    this.isEnabled = enabled;
    gameRenderer.getInstance().setCameraEnabled(enabled);
  }

  /**
   * تعديل الحساسية
   */
  setSensitivity(sensitivity: number): void {
    this.config.sensitivity = BABYLON.Scalar.Clamp(sensitivity, 0.1, 5.0);
    if (this.camera) {
      this.camera.angularSensibilityX = 1000 / this.config.sensitivity;
      this.camera.angularSensibilityY = 1000 / this.config.sensitivity;
    }
  }

  /**
   * تعديل المسافة
   */
  setDistance(distance: number): void {
    this.config.distance = distance;
    if (this.camera) {
      this.camera.radius = distance;
    }
  }

  /**
   * طباعة معلومات الكاميرا
   */
  printCameraInfo(): void {
    if (!this.camera) {
      console.log('Camera not initialized');
      return;
    }

    console.log(`
    📷 CAMERA INFO
    ─────────────────────
    Mode: ${this.mode}
    Position: [${this.camera.position.x.toFixed(2)}, ${this.camera.position.y.toFixed(2)}, ${this.camera.position.z.toFixed(2)}]
    Target: [${this.camera.target.x.toFixed(2)}, ${this.camera.target.y.toFixed(2)}, ${this.camera.target.z.toFixed(2)}]
    Radius: ${this.camera.radius.toFixed(2)}
    Alpha: ${this.camera.alpha.toFixed(2)}
    Beta: ${this.camera.beta.toFixed(2)}

    Config:
      Distance: ${this.config.distance}
      Height: ${this.config.height}
      Smoothness: ${this.config.smoothness}
      Sensitivity: ${this.config.sensitivity}

    Input:
      Forward: ${this.input.forward}
      Backward: ${this.input.backward}
      Left: ${this.input.left}
      Right: ${this.input.right}
    ─────────────────────
    `);
  }
}

// تصدير نسخة واحدة
export const cameraController = CameraController.getInstance();
