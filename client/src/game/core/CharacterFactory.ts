/**
 * Character Factory - مصنع الشخصيات
 * نظام إنشاء وإدارة الشخصيات مع توليد أشكال ثلاثية الأبعاد إجرائي
 */

import * as BABYLON from 'babylonjs';
import { CharacterProfile, CharacterId, CharacterStats } from '../../types/gameTypes';
import { gameEvents } from './EventSystem';

export interface CharacterMesh {
  root: BABYLON.TransformNode;
  body: BABYLON.AbstractMesh;
  head: BABYLON.AbstractMesh;
  leftArm: BABYLON.AbstractMesh;
  rightArm: BABYLON.AbstractMesh;
  leftLeg: BABYLON.AbstractMesh;
  rightLeg: BABYLON.AbstractMesh;
  weapon?: BABYLON.AbstractMesh;
}

interface CharacterDefinition {
  id: CharacterId;
  profile: CharacterProfile;
  mesh?: CharacterMesh;
  position: BABYLON.Vector3;
}

export class CharacterFactory {
  private static instance: CharacterFactory;
  private scene: BABYLON.Scene | null = null;
  private characters: Map<CharacterId, CharacterDefinition> = new Map();
  private materials: Map<string, BABYLON.Material> = new Map();

  private constructor() {
    console.log('👥 CharacterFactory initialized');
  }

  /**
   * الحصول على نسخة واحدة من مصنع الشخصيات
   */
  static getInstance(): CharacterFactory {
    if (!CharacterFactory.instance) {
      CharacterFactory.instance = new CharacterFactory();
    }
    return CharacterFactory.instance;
  }

  /**
   * تعيين المشهد (يجب استدعاؤها بعد إنشاء المشهد)
   */
  setScene(scene: BABYLON.Scene): void {
    this.scene = scene;
    this.initializeMaterials();
    console.log('✓ CharacterFactory scene set');
  }

  /**
   * تهيئة المواد الأساسية للشخصيات
   */
  private initializeMaterials(): void {
    if (!this.scene) return;

    // مادة الرماد (Ash)
    const ashMaterial = new BABYLON.StandardMaterial('ashMaterial', this.scene);
    ashMaterial.diffuse = new BABYLON.Color3(0.3, 0.3, 0.35);
    ashMaterial.specularColor = new BABYLON.Color3(0.2, 0.2, 0.2);
    ashMaterial.alpha = 1;
    this.materials.set('ash', ashMaterial);

    // مادة الرون (Rune)
    const runeMaterial = new BABYLON.StandardMaterial('runeMaterial', this.scene);
    runeMaterial.diffuse = new BABYLON.Color3(0.25, 0.35, 0.5);
    runeMaterial.specularColor = new BABYLON.Color3(0.4, 0.4, 0.6);
    runeMaterial.alpha = 1;
    this.materials.set('rune', runeMaterial);

    // مادة كور (Kor)
    const korMaterial = new BABYLON.StandardMaterial('korMaterial', this.scene);
    korMaterial.diffuse = new BABYLON.Color3(0.45, 0.25, 0.15);
    korMaterial.specularColor = new BABYLON.Color3(0.3, 0.2, 0.1);
    korMaterial.alpha = 1;
    this.materials.set('kor', korMaterial);

    console.log('✓ Character materials initialized');
  }

  /**
   * إنشاء شخصية جديدة
   */
  async createCharacter(
    characterId: CharacterId,
    position: BABYLON.Vector3 = BABYLON.Vector3.Zero()
  ): Promise<CharacterMesh> {
    if (!this.scene) {
      throw new Error('Scene not initialized. Call setScene() first.');
    }

    // الحصول على ملف تعريف الشخصية
    const profile = this.getCharacterProfile(characterId);

    // إنشاء جذر الشخصية
    const root = new BABYLON.TransformNode(`character_${characterId}`, this.scene);
    root.position = position;

    // الحصول على المادة المناسبة
    const material = this.materials.get(characterId) || this.materials.get('ash')!;

    // إنشاء الأجزاء الجسدية
    const mesh = await this.buildCharacterMesh(characterId, profile, root, material);

    // تخزين في القائمة
    this.characters.set(characterId, {
      id: characterId,
      profile,
      mesh,
      position,
    });

    // بث حدث
    gameEvents.emit('character_created', {
      characterId,
      position: position.asArray(),
    });

    console.log(`✓ Character created: ${characterId}`);
    return mesh;
  }

  /**
   * بناء الشكل الثلاثي الأبعاد للشخصية
   */
  private async buildCharacterMesh(
    characterId: CharacterId,
    profile: CharacterProfile,
    root: BABYLON.TransformNode,
    material: BABYLON.Material
  ): Promise<CharacterMesh> {
    if (!this.scene) throw new Error('Scene not initialized');

    // حساب مقياس الشخصية
    const scale = this.getCharacterScale(characterId);

    // إنشاء الرأس
    const head = BABYLON.MeshBuilder.CreateSphere('head', { diameter: 0.4 * scale, segments: 16 }, this.scene);
    head.position.y = 0.8 * scale;
    head.parent = root;
    head.material = material;

    // إنشاء الجسم
    const body = BABYLON.MeshBuilder.CreateCylinder('body', { height: 0.8 * scale, diameter: 0.35 * scale, tessellation: 16 }, this.scene);
    body.position.y = 0.4 * scale;
    body.parent = root;
    body.material = material;

    // إنشاء الذراع الأيسر
    const leftArm = BABYLON.MeshBuilder.CreateCylinder('leftArm', { height: 0.7 * scale, diameter: 0.15 * scale, tessellation: 8 }, this.scene);
    leftArm.position.set(-0.25 * scale, 0.5 * scale, 0);
    leftArm.rotation.z = Math.PI / 6;
    leftArm.parent = root;
    leftArm.material = material;

    // إنشاء الذراع الأيمن
    const rightArm = BABYLON.MeshBuilder.CreateCylinder('rightArm', { height: 0.7 * scale, diameter: 0.15 * scale, tessellation: 8 }, this.scene);
    rightArm.position.set(0.25 * scale, 0.5 * scale, 0);
    rightArm.rotation.z = -Math.PI / 6;
    rightArm.parent = root;
    rightArm.material = material;

    // إنشاء الساق الأيسر
    const leftLeg = BABYLON.MeshBuilder.CreateCylinder('leftLeg', { height: 0.8 * scale, diameter: 0.2 * scale, tessellation: 8 }, this.scene);
    leftLeg.position.set(-0.12 * scale, -0.2 * scale, 0);
    leftLeg.parent = root;
    leftLeg.material = material;

    // إنشاء الساق الأيمن
    const rightLeg = BABYLON.MeshBuilder.CreateCylinder('rightLeg', { height: 0.8 * scale, diameter: 0.2 * scale, tessellation: 8 }, this.scene);
    rightLeg.position.set(0.12 * scale, -0.2 * scale, 0);
    rightLeg.parent = root;
    rightLeg.material = material;

    // إنشاء السلاح الأولي
    const weapon = this.createWeapon(characterId, profile, root, material, scale);

    return {
      root,
      body,
      head,
      leftArm,
      rightArm,
      leftLeg,
      rightLeg,
      weapon,
    };
  }

  /**
   * إنشاء السلاح للشخصية
   */
  private createWeapon(
    characterId: CharacterId,
    profile: CharacterProfile,
    parent: BABYLON.TransformNode,
    material: BABYLON.Material,
    scale: number
  ): BABYLON.AbstractMesh {
    if (!this.scene) throw new Error('Scene not initialized');

    let weapon: BABYLON.AbstractMesh;

    // إنشاء السلاح حسب نوع الشخصية
    switch (characterId) {
      case 'ash':
        // سيف الرماد (Ash Blade)
        weapon = BABYLON.MeshBuilder.CreateBox('ashBlade', { width: 0.1 * scale, height: 0.8 * scale, depth: 0.02 * scale }, this.scene);
        weapon.material = material;
        break;

      case 'rune':
        // هالة الأحرف (Rune Halo)
        weapon = BABYLON.MeshBuilder.CreateTorus('runeHalo', { diameter: 0.5 * scale, thickness: 0.06 * scale }, this.scene);
        weapon.material = material;
        break;

      case 'kor':
        // كماشة الوحش (Beast Claw)
        weapon = BABYLON.MeshBuilder.CreateBox('beastClaw', { width: 0.15 * scale, height: 0.6 * scale, depth: 0.1 * scale }, this.scene);
        weapon.material = material;
        break;

      default:
        weapon = BABYLON.MeshBuilder.CreateBox('genericWeapon', { width: 0.1 * scale, height: 0.7 * scale, depth: 0.02 * scale }, this.scene);
        weapon.material = material;
    }

    weapon.position.set(0.15 * scale, 0.3 * scale, 0);
    weapon.parent = parent;

    return weapon;
  }

  /**
   * الحصول على مقياس الشخصية
   */
  private getCharacterScale(characterId: CharacterId): number {
    switch (characterId) {
      case 'ash':
        return 1.0; // شخصية متوازنة
      case 'rune':
        return 1.05; // أطول قليلاً
      case 'kor':
        return 1.15; // أضخم وأقوى
      default:
        return 1.0;
    }
  }

  /**
   * الحصول على ملف تعريف الشخصية
   */
  private getCharacterProfile(characterId: CharacterId): CharacterProfile {
    const profiles: Record<CharacterId, CharacterProfile> = {
      ash: {
        id: 'ash',
        name: 'Ash',
        description: 'محارب الرماد',
        origin: 'ash_gate',
        stats: {
          health: 100,
          energy: 100,
          speed: 6,
          baseDamage: 15,
          defense: 8,
          weaponTier: 0,
        },
        startingAbilities: ['slash', 'parry'],
        weaponData: {
          type: 'sword',
          name: 'Ash Blade',
          damage: 15,
          speed: 0.8,
          range: 1.5,
        },
        colorScheme: { primary: 0x4d4d56, secondary: 0x999999 },
      },
      rune: {
        id: 'rune',
        name: 'Rune',
        description: 'ساحرة الأحرف',
        origin: 'bell_marsh',
        stats: {
          health: 75,
          energy: 150,
          speed: 6.5,
          baseDamage: 12,
          defense: 5,
          weaponTier: 0,
        },
        startingAbilities: ['fireball', 'shield'],
        weaponData: {
          type: 'staff',
          name: 'Rune Halo',
          damage: 12,
          speed: 1.2,
          range: 8,
        },
        colorScheme: { primary: 0x4059b0, secondary: 0x7a9fd0 },
      },
      kor: {
        id: 'kor',
        name: 'Kor',
        description: 'وحش القوة',
        origin: 'twilight_castle',
        stats: {
          health: 120,
          energy: 80,
          speed: 5,
          baseDamage: 20,
          defense: 12,
          weaponTier: 0,
        },
        startingAbilities: ['roar', 'charge'],
        weaponData: {
          type: 'claw',
          name: 'Beast Claw',
          damage: 20,
          speed: 0.6,
          range: 1.2,
        },
        colorScheme: { primary: 0x724628, secondary: 0xa0693d },
      },
    };

    return profiles[characterId];
  }

  /**
   * تحديث موضع الشخصية
   */
  updateCharacterPosition(characterId: CharacterId, position: BABYLON.Vector3): void {
    const character = this.characters.get(characterId);
    if (!character || !character.mesh) return;

    character.mesh.root.position = position;
    character.position = position;
  }

  /**
   * تحديث دوران الشخصية
   */
  updateCharacterRotation(characterId: CharacterId, rotation: BABYLON.Vector3): void {
    const character = this.characters.get(characterId);
    if (!character || !character.mesh) return;

    character.mesh.root.rotation = rotation;
  }

  /**
   * الحصول على شخصية
   */
  getCharacter(characterId: CharacterId): CharacterDefinition | undefined {
    return this.characters.get(characterId);
  }

  /**
   * الحصول على جميع الشخصيات
   */
  getAllCharacters(): CharacterDefinition[] {
    return Array.from(this.characters.values());
  }

  /**
   * حذف شخصية
   */
  removeCharacter(characterId: CharacterId): void {
    const character = this.characters.get(characterId);
    if (!character || !character.mesh) return;

    // حذف الأشكال الثلاثية الأبعاد
    character.mesh.root.dispose();

    // إزالة من القائمة
    this.characters.delete(characterId);

    // بث حدث
    gameEvents.emit('character_removed', { characterId });
    console.log(`🗑️ Character removed: ${characterId}`);
  }

  /**
   * تنظيف الموارد
   */
  dispose(): void {
    this.characters.forEach((_, characterId) => {
      this.removeCharacter(characterId);
    });

    this.materials.forEach((material) => {
      material.dispose();
    });

    this.characters.clear();
    this.materials.clear();
    console.log('🗑️ CharacterFactory disposed');
  }

  /**
   * طباعة معلومات الشخصيات
   */
  printCharacterInfo(characterId: CharacterId): void {
    const character = this.characters.get(characterId);
    if (!character) {
      console.log(`Character ${characterId} not found`);
      return;
    }

    console.log(`
    👥 CHARACTER INFO: ${characterId.toUpperCase()}
    ─────────────────────
    Name: ${character.profile.name}
    Description: ${character.profile.description}
    Origin: ${character.profile.origin}

    Stats:
      Health: ${character.profile.stats.health}
      Energy: ${character.profile.stats.energy}
      Speed: ${character.profile.stats.speed}
      Base Damage: ${character.profile.stats.baseDamage}
      Defense: ${character.profile.stats.defense}

    Weapon: ${character.profile.weaponData.name}
      Type: ${character.profile.weaponData.type}
      Damage: ${character.profile.weaponData.damage}
      Range: ${character.profile.weaponData.range}

    Position: [${character.position.x.toFixed(2)}, ${character.position.y.toFixed(2)}, ${character.position.z.toFixed(2)}]
    ─────────────────────
    `);
  }
}

// تصدير نسخة واحدة
export const characterFactory = CharacterFactory.getInstance();
