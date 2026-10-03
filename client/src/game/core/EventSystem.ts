/**
 * Event System - نظام الأحداث المركزي
 * إدارة جميع أحداث اللعبة من خلال نمط Observer
 */

import { GameEvent, GameEventType, EventCallback } from '../../types/gameTypes';

export class EventSystem {
  private static instance: EventSystem;
  private listeners: Map<GameEventType | string, EventCallback[]> = new Map();
  private eventHistory: GameEvent[] = [];
  private maxHistorySize: number = 1000;

  private constructor() {
    console.log('🎯 EventSystem initialized');
  }

  /**
   * الحصول على نسخة واحدة من نظام الأحداث (Singleton)
   */
  static getInstance(): EventSystem {
    if (!EventSystem.instance) {
      EventSystem.instance = new EventSystem();
    }
    return EventSystem.instance;
  }

  /**
   * الاشتراك في حدث معين
   */
  subscribe(eventType: GameEventType | string, callback: EventCallback): void {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, []);
    }
    this.listeners.get(eventType)!.push(callback);
    console.log(`✓ Subscribed to event: ${eventType}`);
  }

  /**
   * إلغاء الاشتراك من حدث معين
   */
  unsubscribe(eventType: GameEventType | string, callback: EventCallback): void {
    if (!this.listeners.has(eventType)) return;

    const callbacks = this.listeners.get(eventType)!;
    const index = callbacks.indexOf(callback);
    if (index > -1) {
      callbacks.splice(index, 1);
      console.log(`✓ Unsubscribed from event: ${eventType}`);
    }
  }

  /**
   * بث حدث إلى جميع المشتركين
   */
  emit(eventType: GameEventType | string, data: any = {}): void {
    const event: GameEvent = {
      type: eventType,
      data,
      timestamp: Date.now(),
    };

    // إضافة للسجل
    this.eventHistory.push(event);
    if (this.eventHistory.length > this.maxHistorySize) {
      this.eventHistory.shift();
    }

    // تنفيذ جميع المستمعين
    if (this.listeners.has(eventType)) {
      const callbacks = this.listeners.get(eventType)!;
      for (const callback of callbacks) {
        try {
          callback(event);
        } catch (error) {
          console.error(`Error in event callback for ${eventType}:`, error);
        }
      }
    }

    // Log للتطوير
    if (eventType !== 'frame_update') {
      console.log(`📢 Event emitted: ${eventType}`, data);
    }
  }

  /**
   * الاشتراك في حدث مرة واحدة فقط
   */
  once(eventType: GameEventType | string, callback: EventCallback): void {
    const wrappedCallback = (event: GameEvent) => {
      callback(event);
      this.unsubscribe(eventType, wrappedCallback);
    };
    this.subscribe(eventType, wrappedCallback);
  }

  /**
   * حذف جميع المستمعين لحدث معين
   */
  clear(eventType?: GameEventType | string): void {
    if (eventType) {
      this.listeners.delete(eventType);
    } else {
      this.listeners.clear();
    }
  }

  /**
   * الحصول على سجل الأحداث
   */
  getHistory(limit: number = 50): GameEvent[] {
    return this.eventHistory.slice(-limit);
  }

  /**
   * طباعة سجل الأحداث للتطوير
   */
  printHistory(limit: number = 20): void {
    console.log('📋 Event History:');
    const history = this.getHistory(limit);
    history.forEach((event, index) => {
      console.log(`${index + 1}. [${event.type}]`, event.data);
    });
  }

  /**
   * الحصول على عدد المستمعين لحدث معين
   */
  getListenerCount(eventType: GameEventType | string): number {
    return this.listeners.get(eventType)?.length || 0;
  }

  /**
   * طباعة إحصائيات المستمعين
   */
  printListenerStats(): void {
    console.log('📊 Event Listener Statistics:');
    let totalListeners = 0;
    this.listeners.forEach((callbacks, eventType) => {
      console.log(`  ${eventType}: ${callbacks.length} listeners`);
      totalListeners += callbacks.length;
    });
    console.log(`  Total: ${totalListeners} listeners`);
  }
}

// تصدير instance واحد
export const gameEvents = EventSystem.getInstance();
