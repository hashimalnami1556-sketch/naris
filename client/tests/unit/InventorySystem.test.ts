/**
 * Inventory System Tests - اختبارات نظام الحقيبة
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { InventorySystem, inventorySystem, InventoryItem } from '../../src/game/core/InventorySystem';

describe('InventorySystem', () => {
  beforeEach(() => {
    inventorySystem.clear();
  });

  it('should be a singleton', () => {
    const instance1 = InventorySystem.getInstance();
    const instance2 = InventorySystem.getInstance();
    expect(instance1).toBe(instance2);
  });

  it('should add item to inventory', () => {
    const item: InventoryItem = {
      id: 'sword1',
      name: 'Iron Sword',
      type: 'weapon',
      quantity: 1,
      rarity: 'common',
      description: 'A basic iron sword',
    };

    const result = inventorySystem.addItem(item);
    expect(result).toBe(true);

    const retrieved = inventorySystem.getItem('sword1');
    expect(retrieved).toBeDefined();
    expect(retrieved?.quantity).toBe(1);
  });

  it('should increment quantity when adding duplicate item', () => {
    const item: InventoryItem = {
      id: 'potion1',
      name: 'Health Potion',
      type: 'consumable',
      quantity: 1,
      rarity: 'common',
      description: 'Restores health',
    };

    inventorySystem.addItem(item);
    inventorySystem.addItem(item);

    const retrieved = inventorySystem.getItem('potion1');
    expect(retrieved?.quantity).toBe(2);
  });

  it('should remove item from inventory', () => {
    const item: InventoryItem = {
      id: 'item1',
      name: 'Item',
      type: 'misc',
      quantity: 3,
      rarity: 'common',
      description: 'Test item',
    };

    inventorySystem.addItem(item);
    const removed = inventorySystem.removeItem('item1', 1);

    expect(removed).toBe(true);
    const retrieved = inventorySystem.getItem('item1');
    expect(retrieved?.quantity).toBe(2);
  });

  it('should add shards', () => {
    inventorySystem.addShard('astral', 10);
    const count = inventorySystem.getShardCount('astral');
    expect(count).toBe(10);
  });

  it('should use shards', () => {
    inventorySystem.addShard('decay', 20);
    const used = inventorySystem.useShard('decay', 5);

    expect(used).toBe(true);
    expect(inventorySystem.getShardCount('decay')).toBe(15);
  });

  it('should return false when using more shards than available', () => {
    inventorySystem.addShard('echo', 5);
    const used = inventorySystem.useShard('echo', 10);

    expect(used).toBe(false);
  });

  it('should select and get selected item', () => {
    const item: InventoryItem = {
      id: 'weapon1',
      name: 'Weapon',
      type: 'weapon',
      quantity: 1,
      rarity: 'rare',
      description: 'A rare weapon',
    };

    inventorySystem.addItem(item);
    inventorySystem.selectItem('weapon1');

    const selected = inventorySystem.getSelectedItem();
    expect(selected?.id).toBe('weapon1');
  });

  it('should get all items', () => {
    const item1: InventoryItem = {
      id: 'item1',
      name: 'Item 1',
      type: 'misc',
      quantity: 1,
      rarity: 'common',
      description: 'Item 1',
    };

    const item2: InventoryItem = {
      id: 'item2',
      name: 'Item 2',
      type: 'misc',
      quantity: 1,
      rarity: 'common',
      description: 'Item 2',
    };

    inventorySystem.addItem(item1);
    inventorySystem.addItem(item2);

    const all = inventorySystem.getAllItems();
    expect(all.length).toBe(2);
  });

  it('should calculate total shard value', () => {
    inventorySystem.addShard('astral', 5); // 5 * 10 = 50
    inventorySystem.addShard('decay', 2); // 2 * 15 = 30
    // Total = 80

    const value = inventorySystem.getTotalShardValue();
    expect(value).toBeGreaterThan(0);
  });
});
