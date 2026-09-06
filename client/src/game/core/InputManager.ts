/**
 * Input Manager - مدير الإدخال المركزي
 * إدارة جميع مدخلات لوحة المفاتيح والماوس واللمس
 */

import { gameEvents } from './EventSystem';

export type InputAction =
  | 'move_forward'
  | 'move_backward'
  | 'move_left'
  | 'move_right'
  | 'sprint'
  | 'jump'
  | 'attack'
  | 'ability_1'
  | 'ability_2'
  | 'ability_3'
  | 'defend'
  | 'dodge'
  | 'interact'
  | 'pause'
  | 'inventory'
  | 'map'
  | 'character_next'
  | 'character_prev'
  | 'camera_cycle';

export interface InputBinding {
  action: InputAction;
  key?: string; // keyboard key code
  mouseButton?: number; // 0=left, 1=middle, 2=right
  touchGesture?: string; // 'tap', 'double-tap', 'swipe', etc.
}

export interface InputState {
  keyboard: Map<string, boolean>;
  mouse: {
    position: { x: number; y: number };
    buttons: Map<number, boolean>;
    wheel: number;
  };
  touch: {
    active: boolean;
    position: { x: number; y: number };
    gestureType: string;
  };
}

export class InputManager {
  private static instance: InputManager;
  private inputState: InputState;
  private bindings: Map<InputAction, InputBinding[]> = new Map();
  private isEnabled: boolean = true;
  private actionListeners: Map<InputAction, Set<(pressed: boolean) => void>> = new Map();

  private constructor() {
    this.inputState = {
      keyboard: new Map(),
      mouse: {
        position: { x: 0, y: 0 },
        buttons: new Map(),
        wheel: 0,
      },
      touch: {
        active: false,
        position: { x: 0, y: 0 },
        gestureType: '',
      },
    };

    this.initializeDefaultBindings();
    console.log('⌨️ InputManager initialized');
  }

  /**
   * الحصول على نسخة واحدة من مدير الإدخال
   */
  static getInstance(): InputManager {
    if (!InputManager.instance) {
      InputManager.instance = new InputManager();
    }
    return InputManager.instance;
  }

  /**
   * تهيئة ربط المفاتيح الافتراضي
   */
  private initializeDefaultBindings(): void {
    // الحركة
    this.bindAction('move_forward', { action: 'move_forward', key: 'KeyW' });
    this.bindAction('move_backward', { action: 'move_backward', key: 'KeyS' });
    this.bindAction('move_left', { action: 'move_left', key: 'KeyA' });
    this.bindAction('move_right', { action: 'move_right', key: 'KeyD' });

    // الإجراءات
    this.bindAction('sprint', { action: 'sprint', key: 'ShiftLeft' });
    this.bindAction('jump', { action: 'jump', key: 'Space' });
    this.bindAction('attack', { action: 'attack', key: 'KeyZ' });

    // القدرات
    this.bindAction('ability_1', { action: 'ability_1', key: 'KeyX' });
    this.bindAction('ability_2', { action: 'ability_2', key: 'KeyC' });
    this.bindAction('ability_3', { action: 'ability_3', key: 'KeyV' });

    // الدفاع
    this.bindAction('defend', { action: 'defend', key: 'KeyQ' });
    this.bindAction('dodge', { action: 'dodge', key: 'KeyE' });

    // التفاعل
    this.bindAction('interact', { action: 'interact', key: 'KeyF' });

    // القائمة
    this.bindAction('pause', { action: 'pause', key: 'Escape' });
    this.bindAction('inventory', { action: 'inventory', key: 'KeyI' });
    this.bindAction('map', { action: 'map', key: 'KeyM' });

    // تبديل الشخصيات
    this.bindAction('character_next', { action: 'character_next', key: 'Digit1' });
    this.bindAction('character_prev', { action: 'character_prev', key: 'Digit2' });

    // الكاميرا
    this.bindAction('camera_cycle', { action: 'camera_cycle', key: 'KeyG' });

    console.log('✓ Default input bindings initialized');
  }

  /**
   * تهيئة مدير الإدخال
   */
  initialize(): void {
    document.addEventListener('keydown', (e) => this.onKeyDown(e));
    document.addEventListener('keyup', (e) => this.onKeyUp(e));
    document.addEventListener('mousemove', (e) => this.onMouseMove(e));
    document.addEventListener('mousedown', (e) => this.onMouseDown(e));
    document.addEventListener('mouseup', (e) => this.onMouseUp(e));
    document.addEventListener('wheel', (e) => this.onMouseWheel(e));

    // اللمس
    document.addEventListener('touchstart', (e) => this.onTouchStart(e));
    document.addEventListener('touchmove', (e) => this.onTouchMove(e));
    document.addEventListener('touchend', (e) => this.onTouchEnd(e));

    console.log('✓ InputManager event listeners attached');
  }

  /**
   * ربط إجراء بمفتاح
   */
  bindAction(action: InputAction, binding: InputBinding): void {
    if (!this.bindings.has(action)) {
      this.bindings.set(action, []);
    }

    this.bindings.get(action)!.push(binding);
    console.log(`✓ Bound ${action} to key ${binding.key || 'unknown'}`);
  }

  /**
   * إزالة ربط إجراء
   */
  unbindAction(action: InputAction, key?: string): void {
    if (!this.bindings.has(action)) return;

    const bindings = this.bindings.get(action)!;
    const index = bindings.findIndex((b) => (key ? b.key === key : true));

    if (index > -1) {
      bindings.splice(index, 1);
      console.log(`✓ Unbound ${action}`);
    }
  }

  /**
   * الاشتراك في حدث الإجراء
   */
  onAction(action: InputAction, callback: (pressed: boolean) => void): void {
    if (!this.actionListeners.has(action)) {
      this.actionListeners.set(action, new Set());
    }

    this.actionListeners.get(action)!.add(callback);
  }

  /**
   * إلغاء الاشتراك من حدث الإجراء
   */
  offAction(action: InputAction, callback: (pressed: boolean) => void): void {
    if (!this.actionListeners.has(action)) return;

    this.actionListeners.get(action)!.delete(callback);
  }

  /**
   * بث حدث الإجراء
   */
  private emitAction(action: InputAction, pressed: boolean): void {
    const listeners = this.actionListeners.get(action);
    if (listeners) {
      listeners.forEach((callback) => callback(pressed));
    }

    gameEvents.emit('input_action', {
      action,
      pressed,
    });
  }

  /**
   * معالج الضغط على المفتاح
   */
  private onKeyDown(event: KeyboardEvent): void {
    if (!this.isEnabled) return;

    this.inputState.keyboard.set(event.code, true);

    // العثور على الإجراءات المرتبطة بهذا المفتاح
    this.bindings.forEach((bindingList, action) => {
      bindingList.forEach((binding) => {
        if (binding.key === event.code) {
          this.emitAction(action, true);
        }
      });
    });
  }

  /**
   * معالج رفع المفتاح
   */
  private onKeyUp(event: KeyboardEvent): void {
    if (!this.isEnabled) return;

    this.inputState.keyboard.set(event.code, false);

    // العثور على الإجراءات المرتبطة بهذا المفتاح
    this.bindings.forEach((bindingList, action) => {
      bindingList.forEach((binding) => {
        if (binding.key === event.code) {
          this.emitAction(action, false);
        }
      });
    });
  }

  /**
   * معالج حركة الماوس
   */
  private onMouseMove(event: MouseEvent): void {
    this.inputState.mouse.position = { x: event.clientX, y: event.clientY };

    gameEvents.emit('mouse_move', {
      x: event.clientX,
      y: event.clientY,
    });
  }

  /**
   * معالج الضغط على زر الماوس
   */
  private onMouseDown(event: MouseEvent): void {
    if (!this.isEnabled) return;

    this.inputState.mouse.buttons.set(event.button, true);

    // العثور على الإجراءات المرتبطة بزر الماوس
    this.bindings.forEach((bindingList, action) => {
      bindingList.forEach((binding) => {
        if (binding.mouseButton === event.button) {
          this.emitAction(action, true);
        }
      });
    });
  }

  /**
   * معالج رفع زر الماوس
   */
  private onMouseUp(event: MouseEvent): void {
    if (!this.isEnabled) return;

    this.inputState.mouse.buttons.set(event.button, false);

    // العثور على الإجراءات المرتبطة بزر الماوس
    this.bindings.forEach((bindingList, action) => {
      bindingList.forEach((binding) => {
        if (binding.mouseButton === event.button) {
          this.emitAction(action, false);
        }
      });
    });
  }

  /**
   * معالج عجلة الماوس
   */
  private onMouseWheel(event: WheelEvent): void {
    this.inputState.mouse.wheel = event.deltaY;

    gameEvents.emit('mouse_wheel', {
      delta: event.deltaY,
    });
  }

  /**
   * معالج بدء اللمس
   */
  private onTouchStart(event: TouchEvent): void {
    if (!this.isEnabled || event.touches.length === 0) return;

    const touch = event.touches[0];
    this.inputState.touch.active = true;
    this.inputState.touch.position = { x: touch.clientX, y: touch.clientY };

    gameEvents.emit('touch_start', {
      x: touch.clientX,
      y: touch.clientY,
    });
  }

  /**
   * معالج حركة اللمس
   */
  private onTouchMove(event: TouchEvent): void {
    if (!this.isEnabled || event.touches.length === 0) return;

    const touch = event.touches[0];
    this.inputState.touch.position = { x: touch.clientX, y: touch.clientY };

    gameEvents.emit('touch_move', {
      x: touch.clientX,
      y: touch.clientY,
    });
  }

  /**
   * معالج نهاية اللمس
   */
  private onTouchEnd(event: TouchEvent): void {
    this.inputState.touch.active = false;

    gameEvents.emit('touch_end', {
      x: this.inputState.touch.position.x,
      y: this.inputState.touch.position.y,
    });
  }

  /**
   * فحص ما إذا كان إجراء نشطاً
   */
  isActionPressed(action: InputAction): boolean {
    const bindings = this.bindings.get(action) || [];

    for (const binding of bindings) {
      if (binding.key && this.inputState.keyboard.get(binding.key)) {
        return true;
      }
      if (binding.mouseButton !== undefined && this.inputState.mouse.buttons.get(binding.mouseButton)) {
        return true;
      }
    }

    return false;
  }

  /**
   * الحصول على موضع الماوس
   */
  getMousePosition(): { x: number; y: number } {
    return { ...this.inputState.mouse.position };
  }

  /**
   * الحصول على موضع اللمس
   */
  getTouchPosition(): { x: number; y: number } {
    return { ...this.inputState.touch.position };
  }

  /**
   * تفعيل/تعطيل الإدخال
   */
  setEnabled(enabled: boolean): void {
    this.isEnabled = enabled;
    console.log(`✓ Input ${enabled ? 'enabled' : 'disabled'}`);
  }

  /**
   * طباعة معلومات الإدخال
   */
  printInputInfo(): void {
    const mousePos = this.getMousePosition();
    const touchPos = this.getTouchPosition();

    console.log(`
    ⌨️ INPUT INFO
    ─────────────────────
    Enabled: ${this.isEnabled}

    Keyboard:
      Keys Pressed: ${Array.from(this.inputState.keyboard.entries())
        .filter(([, pressed]) => pressed)
        .map(([key]) => key)
        .join(', ')}

    Mouse:
      Position: [${mousePos.x}, ${mousePos.y}]
      Buttons: ${Array.from(this.inputState.mouse.buttons.entries())
        .filter(([, pressed]) => pressed)
        .map(([button]) => button)
        .join(', ')}
      Wheel: ${this.inputState.mouse.wheel}

    Touch:
      Active: ${this.inputState.touch.active}
      Position: [${touchPos.x}, ${touchPos.y}]

    Bindings: ${this.bindings.size} actions
    ─────────────────────
    `);
  }

  /**
   * طباعة جميع الربط
   */
  printBindings(): void {
    console.log('⌨️ INPUT BINDINGS:');
    this.bindings.forEach((bindingList, action) => {
      bindingList.forEach((binding) => {
        const keyInfo = binding.key ? `Key: ${binding.key}` : binding.mouseButton !== undefined ? `Mouse: ${binding.mouseButton}` : 'Unknown';
        console.log(`  ${action}: ${keyInfo}`);
      });
    });
  }
}

// تصدير نسخة واحدة
export const inputManager = InputManager.getInstance();
