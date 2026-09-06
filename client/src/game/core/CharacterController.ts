/**
 * Character Controller - متحكم الشخصية
 * إدارة حركة وتفاعلات الشخصية الرئيسية
 */

import * as BABYLON from 'babylonjs';
import { CharacterId } from '../../types/gameTypes';
import { gameEvents } from './EventSystem';
import { gameState } from './StateManager';
import { characterFactory } from './CharacterFactory';
import { gameRenderer } from './GameRenderer';
import { cameraController } from './CameraController';

export interface CharacterMovementConfig {
  walkSpeed: number;
  sprintSpeed: number;
  acceleration: number;
  friction: number;
  jumpPower: number;
}

export class CharacterController {
  private static instance: CharacterController;
  private currentCharacterId: CharacterId = 'ash';
  private characterMovement: BABYLON.Vector3 = BABYLON.Vector3.Zero();
  private characterVelocity: BABYLON.Vector3 = BABYLON.Vector3.Zero();
  private isGrounded: boolean = false;
  private isSprinting: boolean = false;
  private isJumping: boolean = false;
  private movementConfig: CharacterMovementConfig;
  private input: { forward: boolean; backward: boolean; left: boolean; right: boolean; sprint: boolean; jump: boolean } = {
    forward: false,
    backward: false,
    left: false,
    right: false,
    sprint: false,
    jump: false,
  };

  private constructor() {
    this.movementConfig = this.getMovementConfigForCharacter('ash');
    console.log('👤 CharacterController initialized');
  }

  /**
   * الحصول على نسخة واحدة من متحكم الشخصية
   */
  static getInstance(): CharacterController {
    if (!CharacterController.instance) {
      CharacterController.instance = new CharacterController();
    }
    return CharacterController.instance;
  }

  /**
   * تهيئة متحكم الشخصية
   */
  initialize(): void {
    this.setupInputListeners();
    this.setupEventListeners();
    console.log('✓ CharacterController initialized');
  }

  /**
   * إعداد استقبالات الإدخال
   */
  private setupInputListeners(): void {
    document.addEventListener('keydown', (e) => this.onKeyDown(e));
    document.addEventListener('keyup', (e) => this.onKeyUp(e));
  }

  /**
   * إعداد استقبالات الأحداث
   */
  private setupEventListeners(): void {
    gameEvents.subscribe('frame_update', () => this.update());
    gameEvents.subscribe('character_switched', (event) => {
      const data = event.data as any;
      this.switchCharacter(data.to);
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
        event.preventDefault();
        break;
      case 's':
        this.input.backward = true;
        event.preventDefault();
        break;
      case 'a':
        this.input.left = true;
        event.preventDefault();
        break;
      case 'd':
        this.input.right = true;
        event.preventDefault();
        break;
      case 'shift':
        this.input.sprint = true;
        event.preventDefault();
        break;
      case ' ':
        this.input.jump = true;
        event.preventDefault();
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
      case 'shift':
        this.input.sprint = false;
        break;
      case ' ':
        this.input.jump = false;
        break;
    }
  }

  /**
   * تحديث الشخصية كل إطار
   */
  private update(): void {
    const character = characterFactory.getCharacter(this.currentCharacterId);
    if (!character || !character.mesh) return;

    const deltaTime = 0.016; // ~60fps
    const scene = gameRenderer.getInstance().getScene();
    if (!scene) return;

    // حساب اتجاه الحركة
    this.calculateMovementDirection();

    // تطبيق الحركة
    this.applyMovement(character.mesh.root, deltaTime);

    // تحديث موضع الكاميرا
    cameraController.setTargetPosition(character.mesh.root.position);

    // تحديث حالة اللعبة
    gameState.updateEnergy(this.isSprinting ? -0.5 : 0.2); // استنزاف الطاقة عند الركض، استعادة في حالة الراحة
  }

  /**
   * حساب اتجاه الحركة
   */
  private calculateMovementDirection(): void {
    this.characterMovement = BABYLON.Vector3.Zero();

    const camera = cameraController['camera']; // الوصول إلى الكاميرا
    if (!camera) return;

    // الحصول على اتجاهات الكاميرا
    const forward = BABYLON.Vector3.Normalize(
      BABYLON.Vector3.Zero()
        .subtractInPlace(camera.target)
        .addInPlace(new BABYLON.Vector3(0, 0, 1))
    );

    const right = BABYLON.Vector3.Cross(forward, BABYLON.Vector3.Up());

    // حساب المدخلات النسبية للكاميرا
    if (this.input.forward) {
      this.characterMovement.addInPlace(BABYLON.Vector3.Scale(forward, 1));
    }
    if (this.input.backward) {
      this.characterMovement.subtractInPlace(BABYLON.Vector3.Scale(forward, 1));
    }
    if (this.input.right) {
      this.characterMovement.addInPlace(BABYLON.Vector3.Scale(right, 1));
    }
    if (this.input.left) {
      this.characterMovement.subtractInPlace(BABYLON.Vector3.Scale(right, 1));
    }

    // تطبيع الحركة
    if (this.characterMovement.length() > 0) {
      this.characterMovement = BABYLON.Vector3.Normalize(this.characterMovement);
    }

    // تعيين حالة الركض
    this.isSprinting = this.input.sprint && this.input.forward;
  }

  /**
   * تطبيق الحركة على الشخصية
   */
  private applyMovement(characterRoot: BABYLON.TransformNode, deltaTime: number): void {
    const speed = this.isSprinting ? this.movementConfig.sprintSpeed : this.movementConfig.walkSpeed;
    const targetVelocity = BABYLON.Vector3.Scale(this.characterMovement, speed);

    // تطبيق التسارع والاحتكاك
    this.characterVelocity = BABYLON.Vector3.Lerp(
      this.characterVelocity,
      targetVelocity,
      this.movementConfig.acceleration * deltaTime
    );

    // تطبيق السرعة على الموضع
    characterRoot.position.addInPlace(BABYLON.Vector3.Scale(this.characterVelocity, deltaTime));

    // تدوير الشخصية نحو اتجاه الحركة
    if (this.characterMovement.length() > 0.1) {
      const targetRotation = Math.atan2(this.characterMovement.x, this.characterMovement.z);
      characterRoot.rotation.y = BABYLON.Scalar.Lerp(
        characterRoot.rotation.y,
        targetRotation,
        0.1
      );

      // بث حدث الحركة
      gameEvents.emit('character_moved', {
        characterId: this.currentCharacterId,
        position: characterRoot.position.asArray(),
        velocity: this.characterVelocity.asArray(),
      });
    }

    // معالجة القفز
    if (this.input.jump && this.isGrounded) {
      this.characterVelocity.y = this.movementConfig.jumpPower;
      this.isGrounded = false;
      this.isJumping = true;

      gameEvents.emit('character_jumped', {
        characterId: this.currentCharacterId,
        position: characterRoot.position.asArray(),
      });
    }

    // تطبيق الجاذبية
    this.characterVelocity.y -= 9.8 * deltaTime;

    // فحص الاصطدام مع الأرضية
    if (characterRoot.position.y <= 0.5) {
      characterRoot.position.y = 0.5;
      this.characterVelocity.y = 0;
      this.isGrounded = true;
      this.isJumping = false;
    } else {
      this.isGrounded = false;
    }
  }

  /**
   * تبديل الشخصية
   */
  switchCharacter(characterId: CharacterId): void {
    if (this.currentCharacterId === characterId) return;

    const oldCharacterId = this.currentCharacterId;
    this.currentCharacterId = characterId;
    this.movementConfig = this.getMovementConfigForCharacter(characterId);
    this.characterVelocity = BABYLON.Vector3.Zero();

    gameEvents.emit('character_controller_switched', {
      from: oldCharacterId,
      to: characterId,
    });

    console.log(`✓ Character controller switched to: ${characterId}`);
  }

  /**
   * الحصول على إعدادات الحركة للشخصية
   */
  private getMovementConfigForCharacter(characterId: CharacterId): CharacterMovementConfig {
    const configs: Record<CharacterId, CharacterMovementConfig> = {
      ash: {
        walkSpeed: 8,
        sprintSpeed: 12,
        acceleration: 15,
        friction: 0.9,
        jumpPower: 12,
      },
      rune: {
        walkSpeed: 8.5,
        sprintSpeed: 13,
        acceleration: 18,
        friction: 0.85,
        jumpPower: 14,
      },
      kor: {
        walkSpeed: 7,
        sprintSpeed: 10,
        acceleration: 12,
        friction: 0.95,
        jumpPower: 10,
      },
    };

    return configs[characterId];
  }

  /**
   * الحصول على معرف الشخصية الحالية
   */
  getCurrentCharacterId(): CharacterId {
    return this.currentCharacterId;
  }

  /**
   * فحص ما إذا كانت الشخصية تركض
   */
  isSprinting_(): boolean {
    return this.isSprinting;
  }

  /**
   * فحص ما إذا كانت الشخصية في الهواء
   */
  isInAir(): boolean {
    return !this.isGrounded;
  }

  /**
   * الحصول على السرعة الحالية
   */
  getVelocity(): BABYLON.Vector3 {
    return this.characterVelocity.clone();
  }

  /**
   * الحصول على موضع الشخصية
   */
  getPosition(): BABYLON.Vector3 | null {
    const character = characterFactory.getCharacter(this.currentCharacterId);
    return character?.mesh?.root.position.clone() || null;
  }

  /**
   * طباعة معلومات الشخصية
   */
  printCharacterControllerInfo(): void {
    const character = characterFactory.getCharacter(this.currentCharacterId);

    console.log(`
    👤 CHARACTER CONTROLLER INFO
    ─────────────────────
    Current Character: ${this.currentCharacterId}
    Position: [${character?.position.x.toFixed(2)}, ${character?.position.y.toFixed(2)}, ${character?.position.z.toFixed(2)}]
    Velocity: [${this.characterVelocity.x.toFixed(2)}, ${this.characterVelocity.y.toFixed(2)}, ${this.characterVelocity.z.toFixed(2)}]

    State:
      Grounded: ${this.isGrounded}
      Sprinting: ${this.isSprinting}
      Jumping: ${this.isJumping}

    Movement Config:
      Walk Speed: ${this.movementConfig.walkSpeed}
      Sprint Speed: ${this.movementConfig.sprintSpeed}
      Jump Power: ${this.movementConfig.jumpPower}

    Input:
      Forward: ${this.input.forward}
      Backward: ${this.input.backward}
      Left: ${this.input.left}
      Right: ${this.input.right}
      Sprint: ${this.input.sprint}
      Jump: ${this.input.jump}
    ─────────────────────
    `);
  }
}

// تصدير نسخة واحدة
export const characterController = CharacterController.getInstance();
