/**
 * Inventory System - نظام الحقيبة
 * إدارة أشياء اللاعب والأسلحة والشاردات
 */

import { EventSystem, gameEvents } from './EventSystem';

export interface InventoryItem {
  id: string;
  name: string;
  type: 'weapon' | 'armor' | 'consumable' | 'quest' | 'misc';
  quantity: number;
  rarity: 'common' | 'uncommon' | 'rare' | 'epic' | 'legendary';
  description: string;
}

export interface Shard {
  id: string;
  type: 'astral' | 'decay' | 'echo' | 'void' | 'light';
  quantity: number;
  value: number;
}

export class InventorySystem {
  private static instance: InventorySystem;
  private items: Map<string, InventoryItem> = new Map();
  private shards: Map<string, Shard> = new Map();
  private maxSlots: number = 20;
  private selectedItemId: string | null = null;

  private constructor() {
    this.initializeShards();
  }

  static getInstance(): InventorySystem {
    if (!InventorySystem.instance) {
      InventorySystem.instance = new InventorySystem();
    }
    return InventorySystem.instance;
  }

  /**
   * إضافة عنصر إلى الحقيبة
   */
  addItem(item: InventoryItem): boolean {
    if (this.items.size >= this.maxSlots && !this.items.has(item.id)) {
      gameEvents.emit('inventory_full', {});
      return false;
    }

    if (this.items.has(item.id)) {
      const existing = this.items.get(item.id)!;
      existing.quantity += item.quantity;
    } else {
      this.items.set(item.id, { ...item });
    }

    gameEvents.emit('item_added', { itemId: item.id, quantity: item.quantity });
    console.log(`✓ Item added: ${item.name} x${item.quantity}`);
    return true;
  }

  /**
   * إزالة عنصر من الحقيبة
   */
  removeItem(itemId: string, quantity: number = 1): boolean {
    const item = this.items.get(itemId);
    if (!item) return false;

    item.quantity -= quantity;
    if (item.quantity <= 0) {
      this.items.delete(itemId);
      if (this.selectedItemId === itemId) {
        this.selectedItemId = null;
      }
    }

    gameEvents.emit('item_removed', { itemId, quantity });
    console.log(`✓ Item removed: ${item.name} x${quantity}`);
    return true;
  }

  /**
   * الحصول على عنصر
   */
  getItem(itemId: string): InventoryItem | undefined {
    return this.items.get(itemId);
  }

  /**
   * قائمة جميع الأشياء
   */
  getAllItems(): InventoryItem[] {
    return Array.from(this.items.values());
  }

  /**
   * اختيار عنصر
   */
  selectItem(itemId: string): boolean {
    if (!this.items.has(itemId)) return false;

    this.selectedItemId = itemId;
    gameEvents.emit('item_selected', { itemId });
    return true;
  }

  /**
   * الحصول على العنصر المختار
   */
  getSelectedItem(): InventoryItem | null {
    return this.selectedItemId ? this.items.get(this.selectedItemId) || null : null;
  }

  /**
   * إضافة شاردة
   */
  addShard(shardType: string, quantity: number): void {
    const shard = this.shards.get(shardType);
    if (shard) {
      shard.quantity += quantity;
    } else {
      this.shards.set(shardType, {
        id: shardType,
        type: shardType as any,
        quantity,
        value: this.getShardValue(shardType),
      });
    }

    gameEvents.emit('shard_added', { shardType, quantity });
    console.log(`✓ Shard added: ${shardType} x${quantity}`);
  }

  /**
   * استخدام شاردة
   */
  useShard(shardType: string, quantity: number): boolean {
    const shard = this.shards.get(shardType);
    if (!shard || shard.quantity < quantity) return false;

    shard.quantity -= quantity;
    if (shard.quantity === 0) {
      this.shards.delete(shardType);
    }

    gameEvents.emit('shard_used', { shardType, quantity });
    return true;
  }

  /**
   * الحصول على عدد الشاردات
   */
  getShardCount(shardType: string): number {
    return this.shards.get(shardType)?.quantity || 0;
  }

  /**
   * قيمة الشاردة
   */
  private getShardValue(shardType: string): number {
    const values: Record<string, number> = {
      astral: 10,
      decay: 15,
      echo: 20,
      void: 25,
      light: 30,
    };
    return values[shardType] || 0;
  }

  /**
   * تهيئة الشاردات
   */
  private initializeShards(): void {
    this.shards.set('astral', { id: 'astral', type: 'astral', quantity: 0, value: 10 });
    this.shards.set('decay', { id: 'decay', type: 'decay', quantity: 0, value: 15 });
    this.shards.set('echo', { id: 'echo', type: 'echo', quantity: 0, value: 20 });
    this.shards.set('void', { id: 'void', type: 'void', quantity: 0, value: 25 });
    this.shards.set('light', { id: 'light', type: 'light', quantity: 0, value: 30 });
  }

  /**
   * إجمالي قيمة الشاردات
   */
  getTotalShardValue(): number {
    return Array.from(this.shards.values()).reduce((sum, shard) => sum + shard.value * shard.quantity, 0);
  }

  /**
   * مسح الحقيبة
   */
  clear(): void {
    this.items.clear();
    this.selectedItemId = null;
    gameEvents.emit('inventory_cleared', {});
  }
}

export const inventorySystem = InventorySystem.getInstance();
