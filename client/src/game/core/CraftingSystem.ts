/**
 * Crafting System - نظام الحرف
 * تصنيع الأدوات والأسلحة من الشاردات والمكونات
 */

import { EventSystem, gameEvents } from './EventSystem';
import { InventorySystem, inventorySystem } from './InventorySystem';

export interface CraftingRecipe {
  id: string;
  name: string;
  resultItemId: string;
  resultQuantity: number;
  ingredients: Array<{
    id: string;
    quantity: number;
  }>;
  shards: Array<{
    type: string;
    quantity: number;
  }>;
  craftingTime: number; // ms
  level: number;
}

export class CraftingSystem {
  private static instance: CraftingSystem;
  private recipes: Map<string, CraftingRecipe> = new Map();
  private isCrafting: boolean = false;
  private craftingProgress: number = 0;
  private currentRecipeId: string | null = null;

  private constructor() {
    this.initializeRecipes();
  }

  static getInstance(): CraftingSystem {
    if (!CraftingSystem.instance) {
      CraftingSystem.instance = new CraftingSystem();
    }
    return CraftingSystem.instance;
  }

  /**
   * تسجيل وصفة
   */
  registerRecipe(recipe: CraftingRecipe): void {
    this.recipes.set(recipe.id, recipe);
  }

  /**
   * الحصول على وصفة
   */
  getRecipe(recipeId: string): CraftingRecipe | undefined {
    return this.recipes.get(recipeId);
  }

  /**
   * قائمة جميع الوصفات
   */
  getAllRecipes(): CraftingRecipe[] {
    return Array.from(this.recipes.values());
  }

  /**
   * التحقق من إمكانية الحرف
   */
  canCraft(recipeId: string): boolean {
    const recipe = this.recipes.get(recipeId);
    if (!recipe) return false;

    // التحقق من المكونات
    for (const ingredient of recipe.ingredients) {
      const item = inventorySystem.getItem(ingredient.id);
      if (!item || item.quantity < ingredient.quantity) {
        return false;
      }
    }

    // التحقق من الشاردات
    for (const shard of recipe.shards) {
      if (inventorySystem.getShardCount(shard.type) < shard.quantity) {
        return false;
      }
    }

    return true;
  }

  /**
   * بدء الحرف
   */
  startCrafting(recipeId: string): boolean {
    if (this.isCrafting) {
      console.warn('Already crafting');
      return false;
    }

    if (!this.canCraft(recipeId)) {
      gameEvents.emit('craft_failed', { reason: 'insufficient_resources' });
      return false;
    }

    this.currentRecipeId = recipeId;
    this.isCrafting = true;
    this.craftingProgress = 0;

    gameEvents.emit('craft_started', { recipeId });
    console.log(`✓ Crafting started: ${recipeId}`);

    // محاكاة وقت الحرف
    const recipe = this.recipes.get(recipeId)!;
    setTimeout(() => this.completeCrafting(), recipe.craftingTime);

    return true;
  }

  /**
   * إكمال الحرف
   */
  private completeCrafting(): void {
    if (!this.currentRecipeId) return;

    const recipe = this.recipes.get(this.currentRecipeId)!;

    // إزالة المكونات
    for (const ingredient of recipe.ingredients) {
      inventorySystem.removeItem(ingredient.id, ingredient.quantity);
    }

    // إزالة الشاردات
    for (const shard of recipe.shards) {
      inventorySystem.useShard(shard.type, shard.quantity);
    }

    // إضافة النتيجة
    inventorySystem.addItem({
      id: recipe.resultItemId,
      name: recipe.resultItemId,
      type: 'weapon',
      quantity: recipe.resultQuantity,
      rarity: 'rare',
      description: '',
    });

    this.isCrafting = false;
    this.craftingProgress = 100;
    this.currentRecipeId = null;

    gameEvents.emit('craft_completed', { recipeId: recipe.id });
    console.log(`✓ Crafting completed: ${recipe.name}`);
  }

  /**
   * الحصول على تقدم الحرف
   */
  getCraftingProgress(): number {
    return this.craftingProgress;
  }

  /**
   * هل نحن نحرف
   */
  isCraftingActive(): boolean {
    return this.isCrafting;
  }

  /**
   * إلغاء الحرف
   */
  cancelCrafting(): void {
    if (!this.isCrafting) return;

    const recipeId = this.currentRecipeId;
    this.isCrafting = false;
    this.craftingProgress = 0;
    this.currentRecipeId = null;

    gameEvents.emit('craft_cancelled', { recipeId });
    console.log('✓ Crafting cancelled');
  }

  /**
   * تهيئة الوصفات الافتراضية
   */
  private initializeRecipes(): void {
    const recipes: CraftingRecipe[] = [
      {
        id: 'emberedge_sword',
        name: 'Emberedge Sword',
        resultItemId: 'emberedge',
        resultQuantity: 1,
        ingredients: [
          { id: 'iron_ore', quantity: 3 },
          { id: 'ancient_wood', quantity: 2 },
        ],
        shards: [{ type: 'astral', quantity: 5 }],
        craftingTime: 5000,
        level: 1,
      },
      {
        id: 'ash_bow',
        name: 'Ash Bow',
        resultItemId: 'ash_bow',
        resultQuantity: 1,
        ingredients: [
          { id: 'ash_wood', quantity: 4 },
          { id: 'silver_string', quantity: 1 },
        ],
        shards: [{ type: 'echo', quantity: 3 }],
        craftingTime: 4000,
        level: 1,
      },
    ];

    recipes.forEach((recipe) => this.registerRecipe(recipe));
  }

  /**
   * الحصول على الوصفات المتاحة
   */
  getAvailableRecipes(): CraftingRecipe[] {
    return this.getAllRecipes().filter((recipe) => this.canCraft(recipe.id));
  }
}

export const craftingSystem = CraftingSystem.getInstance();
