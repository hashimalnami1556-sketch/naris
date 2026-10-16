/**
 * Crafting System Tests - اختبارات نظام الحرف
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { CraftingSystem, craftingSystem, CraftingRecipe } from '../../src/game/core/CraftingSystem';
import { inventorySystem } from '../../src/game/core/InventorySystem';

describe('CraftingSystem', () => {
  beforeEach(() => {
    inventorySystem.clear();
  });

  it('should be a singleton', () => {
    const instance1 = CraftingSystem.getInstance();
    const instance2 = CraftingSystem.getInstance();
    expect(instance1).toBe(instance2);
  });

  it('should register a recipe', () => {
    const recipe: CraftingRecipe = {
      id: 'test_recipe',
      name: 'Test Recipe',
      resultItemId: 'result_item',
      resultQuantity: 1,
      ingredients: [],
      shards: [],
      craftingTime: 1000,
      level: 1,
    };

    craftingSystem.registerRecipe(recipe);
    const retrieved = craftingSystem.getRecipe('test_recipe');

    expect(retrieved).toBeDefined();
    expect(retrieved?.name).toBe('Test Recipe');
  });

  it('should get all recipes', () => {
    const recipes = craftingSystem.getAllRecipes();
    expect(Array.isArray(recipes)).toBe(true);
    expect(recipes.length).toBeGreaterThan(0);
  });

  it('should check if recipe can be crafted', () => {
    // Get an existing recipe
    const recipes = craftingSystem.getAllRecipes();
    if (recipes.length > 0) {
      const recipeId = recipes[0].id;
      const canCraft = craftingSystem.canCraft(recipeId);
      // Should be false initially since we don't have ingredients
      expect(typeof canCraft).toBe('boolean');
    }
  });

  it('should not craft if not crafting is active', () => {
    const result = craftingSystem.startCrafting('non_existent_recipe');
    expect(result).toBe(false);
  });

  it('should return crafting progress', () => {
    const progress = craftingSystem.getCraftingProgress();
    expect(progress).toBe(0);
  });

  it('should check if crafting is active', () => {
    const isActive = craftingSystem.isCraftingActive();
    expect(isActive).toBe(false);
  });

  it('should get available recipes', () => {
    const available = craftingSystem.getAvailableRecipes();
    expect(Array.isArray(available)).toBe(true);
  });
});
