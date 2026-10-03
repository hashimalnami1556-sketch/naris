/**
 * HUD System - نظام واجهة المستخدم
 * إدارة العناصر البصرية والمعلومات الحية والعناصر التفاعلية
 */

import { gameEvents } from './EventSystem';
import { gameState } from './StateManager';

export interface HUDElement {
  id: string;
  type: 'health_bar' | 'energy_bar' | 'ability_bar' | 'quest_marker' | 'enemy_health' | 'status_effect' | 'world_marker' | 'interaction_prompt';
  isVisible: boolean;
  position?: { x: number; y: number };
  data?: any;
}

export interface HUDState {
  characterHealth: number;
  characterMaxHealth: number;
  characterEnergy: number;
  characterMaxEnergy: number;
  characterLevel: number;
  characterShards: number;
  currentRealm: string;
  fps: number;
  activeTarget: string | null;
  targetHealth: number;
  targetMaxHealth: number;
  questMarkers: any[];
  activeStatusEffects: string[];
  worldMarkers: any[];
  interactionPrompts: string[];
}

export class HUDSystem {
  private static instance: HUDSystem;
  private hudElements: Map<string, HUDElement> = new Map();
  private hudState: HUDState = {
    characterHealth: 100,
    characterMaxHealth: 100,
    characterEnergy: 100,
    characterMaxEnergy: 100,
    characterLevel: 1,
    characterShards: 0,
    currentRealm: 'ash_gate',
    fps: 60,
    activeTarget: null,
    targetHealth: 0,
    targetMaxHealth: 100,
    questMarkers: [],
    activeStatusEffects: [],
    worldMarkers: [],
    interactionPrompts: [],
  };
  private animatingElements: Set<string> = new Set();
  private elementUpdateCallbacks: Map<string, (element: HUDElement) => void> = new Map();

  private constructor() {
    console.log('🎮 HUDSystem initialized');
    this.initializeEventSubscriptions();
  }

  /**
   * الحصول على نسخة واحدة من نظام الواجهة
   */
  static getInstance(): HUDSystem {
    if (!HUDSystem.instance) {
      HUDSystem.instance = new HUDSystem();
    }
    return HUDSystem.instance;
  }

  /**
   * تهيئة اشتراكات الأحداث
   */
  private initializeEventSubscriptions(): void {
    // Character health updates
    gameEvents.subscribe('health_changed', (data: any) => {
      this.hudState.characterHealth = data.health;
      this.updateElement('health_bar', {
        data: { health: data.health, maxHealth: this.hudState.characterMaxHealth },
      });
      this.animateElementUpdate('health_bar');
    });

    // Character energy updates
    gameEvents.subscribe('energy_changed', (data: any) => {
      this.hudState.characterEnergy = data.energy;
      this.updateElement('energy_bar', {
        data: { energy: data.energy, maxEnergy: this.hudState.characterMaxEnergy },
      });
    });

    // Level changes
    gameEvents.subscribe('level_changed', (data: any) => {
      this.hudState.characterLevel = data.level;
      this.showLevelUpNotification(data.level);
    });

    // Shards collection
    gameEvents.subscribe('shards_changed', (data: any) => {
      this.hudState.characterShards = data.shards;
      this.floatingText('Shards: +' + data.amount, 'resource');
    });

    // Realm switches
    gameEvents.subscribe('realm_switched', (data: any) => {
      this.hudState.currentRealm = data.realmId;
      this.showRealmIndicator(data.realmId);
    });

    // Enemy targeted
    gameEvents.subscribe('enemy_targeted', (data: any) => {
      this.hudState.activeTarget = data.entityId;
      this.hudState.targetHealth = data.health;
      this.hudState.targetMaxHealth = data.maxHealth;
      this.updateElement('enemy_health', {
        isVisible: true,
        data: { health: data.health, maxHealth: data.maxHealth, name: data.name },
      });
    });

    // Enemy defeated
    gameEvents.subscribe('enemy_defeated', () => {
      this.hudState.activeTarget = null;
      this.updateElement('enemy_health', { isVisible: false });
      this.floatingText('Victory!', 'success');
    });

    // Hit effects with HUD feedback
    gameEvents.subscribe('attack_executed', (data: any) => {
      this.floatingText('-' + data.damage, 'damage');
      if (data.hasWeakness > 1) {
        this.floatingText('CRITICAL!', 'critical');
      }
    });

    // Status effects
    gameEvents.subscribe('status_effect_applied', (data: any) => {
      this.addStatusEffect(data.effect, data.duration);
      this.floatingText(data.effect.toUpperCase(), 'status');
    });

    // Performance updates
    gameEvents.subscribe('fps_changed', (data: any) => {
      this.hudState.fps = data.fps;
    });

    // Quest updates
    gameEvents.subscribe('quest_updated', (data: any) => {
      this.updateQuestMarkers(data);
    });

    // Interaction prompts
    gameEvents.subscribe('interaction_available', (data: any) => {
      this.showInteractionPrompt(data.prompt, data.key);
    });

    gameEvents.subscribe('interaction_unavailable', () => {
      this.hideInteractionPrompt();
    });
  }

  /**
   * تحديث عنصر واجهة المستخدم
   */
  private updateElement(elementId: string, update: Partial<HUDElement>): void {
    const element = this.hudElements.get(elementId);
    if (element) {
      Object.assign(element, update);
      const callback = this.elementUpdateCallbacks.get(elementId);
      if (callback) {
        callback(element);
      }
    }
  }

  /**
   * تحريك تحديث عنصر
   */
  private animateElementUpdate(elementId: string): void {
    if (this.animatingElements.has(elementId)) return;

    this.animatingElements.add(elementId);
    gameEvents.emit('hud_element_animate', {
      elementId,
      animation: 'pulse',
      duration: 0.3,
    });

    setTimeout(() => {
      this.animatingElements.delete(elementId);
    }, 300);
  }

  /**
   * إنشاء أو تسجيل عنصر واجهة المستخدم
   */
  registerHUDElement(
    id: string,
    type: HUDElement['type'],
    updateCallback?: (element: HUDElement) => void
  ): void {
    const element: HUDElement = {
      id,
      type,
      isVisible: true,
    };

    this.hudElements.set(id, element);

    if (updateCallback) {
      this.elementUpdateCallbacks.set(id, updateCallback);
    }

    console.log(`✓ HUD Element registered: ${id} (${type})`);
  }

  /**
   * إظهار/إخفاء عنصر واجهة المستخدم
   */
  setElementVisibility(elementId: string, visible: boolean): void {
    const element = this.hudElements.get(elementId);
    if (element) {
      element.isVisible = visible;
      gameEvents.emit('hud_element_visibility_changed', { elementId, visible });
    }
  }

  /**
   * عرض إشعار زيادة المستوى
   */
  private showLevelUpNotification(level: number): void {
    gameEvents.emit('hud_notification', {
      type: 'level_up',
      message: `Level Up! Lvl ${level}`,
      duration: 3000,
      position: 'center',
    });
  }

  /**
   * عرض مؤشر تبديل المملكة
   */
  private showRealmIndicator(realmId: string): void {
    gameEvents.emit('hud_notification', {
      type: 'realm_switch',
      message: `Entered: ${realmId}`,
      duration: 2000,
      position: 'top-center',
    });
  }

  /**
   * إضافة تأثير حالة للشخصية
   */
  private addStatusEffect(effect: string, duration: number): void {
    if (!this.hudState.activeStatusEffects.includes(effect)) {
      this.hudState.activeStatusEffects.push(effect);

      setTimeout(() => {
        this.hudState.activeStatusEffects = this.hudState.activeStatusEffects.filter(
          (e) => e !== effect
        );
        gameEvents.emit('hud_status_effect_removed', { effect });
      }, duration * 1000);

      gameEvents.emit('hud_status_effect_added', { effect, duration });
    }
  }

  /**
   * عرض نص عائم (Floating Text)
   */
  floatingText(text: string, type: 'damage' | 'heal' | 'critical' | 'resource' | 'success' | 'status' | 'default'): void {
    const colors: Record<string, string> = {
      damage: '#FF6B6B',
      heal: '#51CF66',
      critical: '#FFD93D',
      resource: '#6C5CE7',
      success: '#00B894',
      status: '#74B9FF',
      default: '#FFFFFF',
    };

    gameEvents.emit('floating_text_display', {
      text,
      color: colors[type],
      type,
      duration: 1500,
    });

    console.log(`💬 Floating text: ${text} (${type})`);
  }

  /**
   * تحديث علامات المهمات
   */
  private updateQuestMarkers(data: any): void {
    this.hudState.questMarkers = data.markers || [];
    gameEvents.emit('quest_markers_updated', {
      markers: this.hudState.questMarkers,
    });
  }

  /**
   * عرض طلب التفاعل
   */
  private showInteractionPrompt(prompt: string, key: string): void {
    this.hudState.interactionPrompts.push(prompt);
    gameEvents.emit('interaction_prompt_show', {
      prompt,
      key,
    });
  }

  /**
   * إخفاء طلب التفاعل
   */
  private hideInteractionPrompt(): void {
    this.hudState.interactionPrompts = [];
    gameEvents.emit('interaction_prompt_hide', {});
  }

  /**
   * إضافة علامة عالمية (مثل الكنوز أو نقاط المصلحة)
   */
  addWorldMarker(
    id: string,
    position: { x: number; y: number; z: number },
    type: 'treasure' | 'waypoint' | 'objective' | 'npc'
  ): void {
    const marker = { id, position, type, isVisible: true };
    this.hudState.worldMarkers.push(marker);

    gameEvents.emit('world_marker_added', marker);
    console.log(`📍 World marker added: ${id} (${type})`);
  }

  /**
   * إزالة علامة عالمية
   */
  removeWorldMarker(id: string): void {
    this.hudState.worldMarkers = this.hudState.worldMarkers.filter((m) => m.id !== id);
    gameEvents.emit('world_marker_removed', { id });
  }

  /**
   * تحديث موضع علامة عالمية
   */
  updateWorldMarkerPosition(id: string, position: { x: number; y: number; z: number }): void {
    const marker = this.hudState.worldMarkers.find((m) => m.id === id);
    if (marker) {
      marker.position = position;
      gameEvents.emit('world_marker_moved', { id, position });
    }
  }

  /**
   * الحصول على حالة الواجهة الحالية
   */
  getHUDState(): Readonly<HUDState> {
    return { ...this.hudState };
  }

  /**
   * تحديث حالة الواجهة من StateManager
   */
  syncWithGameState(): void {
    const state = gameState.getState();

    this.hudState.characterHealth = state.playerState.health;
    this.hudState.characterMaxHealth = (state.playerState as any).maxHealth || 100;
    this.hudState.characterEnergy = state.playerState.energy;
    this.hudState.characterMaxEnergy = (state.playerState as any).maxEnergy || 100;
    this.hudState.characterLevel = state.playerState.level;
    this.hudState.characterShards = state.playerState.shards;
    this.hudState.currentRealm = state.currentRealm;

    console.log('✓ HUD synced with game state');
  }

  /**
   * عرض تأثير قتالي في الواجهة
   */
  showCombatFeedback(type: 'hit' | 'miss' | 'crit' | 'heal', magnitude: number): void {
    const messages: Record<string, string> = {
      hit: 'Hit!',
      miss: 'Miss!',
      crit: 'Critical Hit!',
      heal: 'Healed!',
    };

    const colors: Record<string, string> = {
      hit: '#FF6B6B',
      miss: '#888888',
      crit: '#FFD93D',
      heal: '#51CF66',
    };

    gameEvents.emit('combat_feedback', {
      type,
      message: messages[type],
      color: colors[type],
      magnitude,
    });

    console.log(`⚔️ Combat feedback: ${type} (${magnitude})`);
  }

  /**
   * تظهير الواجهة بأكملها
   */
  showHUD(): void {
    this.hudElements.forEach((element) => {
      element.isVisible = true;
    });
    gameEvents.emit('hud_show', {});
    console.log('✓ HUD shown');
  }

  /**
   * إخفاء الواجهة بأكملها
   */
  hideHUD(): void {
    this.hudElements.forEach((element) => {
      element.isVisible = false;
    });
    gameEvents.emit('hud_hide', {});
    console.log('✓ HUD hidden');
  }

  /**
   * تنظيف نظام الواجهة
   */
  cleanup(): void {
    this.hudElements.clear();
    this.elementUpdateCallbacks.clear();
    this.animatingElements.clear();
    console.log('✓ HUD System cleaned up');
  }

  /**
   * طباعة معلومات الواجهة
   */
  printHUDInfo(): void {
    console.log(`
    🎮 HUD SYSTEM STATUS
    ─────────────────────
    Health: ${this.hudState.characterHealth}/${this.hudState.characterMaxHealth}
    Energy: ${this.hudState.characterEnergy}/${this.hudState.characterMaxEnergy}
    Level: ${this.hudState.characterLevel}
    Shards: ${this.hudState.characterShards}
    Current Realm: ${this.hudState.currentRealm}
    FPS: ${this.hudState.fps.toFixed(1)}

    Active Elements: ${this.hudElements.size}
    Visible Elements: ${Array.from(this.hudElements.values()).filter((e) => e.isVisible).length}
    Status Effects: ${this.hudState.activeStatusEffects.join(', ') || 'None'}
    World Markers: ${this.hudState.worldMarkers.length}
    ─────────────────────
    `);
  }
}

// تصدير نسخة واحدة
export const hudSystem = HUDSystem.getInstance();
