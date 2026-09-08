// NAR_CraftingSystem.h — نظام الصياغة
// محرك اللعبة — Naris Realms

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NAR_InventorySystem.h"
#include "NAR_CraftingSystem.generated.h"

// ============================================
// بيانات الوصفة
// ============================================
USTRUCT(BlueprintType)
struct FRecipeIngredient
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadWrite, Category = "Recipe")
	FString ItemID = FString();

	UPROPERTY(BlueprintReadWrite, Category = "Recipe")
	int32 RequiredQuantity = 1;

	UPROPERTY(BlueprintReadWrite, Category = "Recipe")
	FString DisplayName = TEXT("");
};

USTRUCT(BlueprintType)
struct FCraftingRecipe
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadWrite, Category = "Recipe")
	FString RecipeID = FString();

	UPROPERTY(BlueprintReadWrite, Category = "Recipe")
	FString RecipeName = TEXT("");

	UPROPERTY(BlueprintReadWrite, Category = "Recipe")
	FString Description = TEXT("");

	UPROPERTY(BlueprintReadWrite, Category = "Recipe")
	TArray<FRecipeIngredient> Ingredients;

	UPROPERTY(BlueprintReadWrite, Category = "Recipe")
	FInventoryItem ResultItem;

	UPROPERTY(BlueprintReadWrite, Category = "Recipe")
	int32 ResultQuantity = 1;

	UPROPERTY(BlueprintReadWrite, Category = "Recipe")
	float CraftingTime = 5.0f;

	UPROPERTY(BlueprintReadWrite, Category = "Recipe")
	int32 RequiredLevel = 1;

	UPROPERTY(BlueprintReadWrite, Category = "Recipe")
	int32 XPReward = 10;

	UPROPERTY(BlueprintReadWrite, Category = "Recipe")
	bool bIsUnlocked = false;

	UPROPERTY(BlueprintReadWrite, Category = "Recipe")
	int32 Rarity = 1;
};

// ============================================
// حالة الصياغة
// ============================================
USTRUCT(BlueprintType)
struct FCraftingState
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadWrite, Category = "Crafting")
	bool bIsCrafting = false;

	UPROPERTY(BlueprintReadWrite, Category = "Crafting")
	FCraftingRecipe CurrentRecipe;

	UPROPERTY(BlueprintReadWrite, Category = "Crafting")
	float CraftingProgress = 0.0f;

	UPROPERTY(BlueprintReadWrite, Category = "Crafting")
	float RemainingTime = 0.0f;
};

// ============================================
// نظام الصياغة
// ============================================
/**
 * UNAR_CraftingSystem — نظام الصياغة
 * يدير: الوصفات + الصياغة + فتح الوصفات
 */
UCLASS(ClassGroup=(NAR), meta=(BlueprintSpawnableComponent))
class NARISREALMS_API UNAR_CraftingSystem : public UActorComponent
{
	GENERATED_BODY()

public:
	UNAR_CraftingSystem();

	virtual void BeginPlay() override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

	// ============================================
	// إدارة الوصفات
	// ============================================
	UFUNCTION(BlueprintCallable, Category = "NAR|Crafting")
	void RegisterRecipe(const FCraftingRecipe& Recipe);

	UFUNCTION(BlueprintCallable, Category = "NAR|Crafting")
	FCraftingRecipe GetRecipe(const FString& RecipeID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Crafting")
	bool UnlockRecipe(const FString& RecipeID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Crafting")
	void LockRecipe(const FString& RecipeID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Crafting")
	bool IsRecipeUnlocked(const FString& RecipeID);

	UFUNCTION(BlueprintPure, Category = "NAR|Crafting")
	TArray<FCraftingRecipe> GetAllRecipes() const;

	UFUNCTION(BlueprintPure, Category = "NAR|Crafting")
	TArray<FCraftingRecipe> GetUnlockedRecipes() const;

	UFUNCTION(BlueprintPure, Category = "NAR|Crafting")
	TArray<FCraftingRecipe> GetRecipesByLevel(int32 Level);

	// ============================================
	// الصياغة
	// ============================================
	UFUNCTION(BlueprintCallable, Category = "NAR|Crafting|Craft")
	bool StartCrafting(const FString& RecipeID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Crafting|Craft")
	void CancelCrafting();

	UFUNCTION(BlueprintCallable, Category = "NAR|Crafting|Craft")
	bool CanCraft(const FString& RecipeID);

	UFUNCTION(BlueprintPure, Category = "NAR|Crafting|Craft")
	bool IsCrafting() const { return CraftingState.bIsCrafting; }

	UFUNCTION(BlueprintPure, Category = "NAR|Crafting|Craft")
	float GetCraftingProgress() const { return CraftingState.CraftingProgress; }

	UFUNCTION(BlueprintPure, Category = "NAR|Crafting|Craft")
	float GetRemainingTime() const { return CraftingState.RemainingTime; }

	// ============================================
	// التحقق من المواد
	// ============================================
	UFUNCTION(BlueprintCallable, Category = "NAR|Crafting|Check")
	bool HasAllIngredients(const FString& RecipeID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Crafting|Check")
	TArray<FRecipeIngredient> GetMissingIngredients(const FString& RecipeID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Crafting|Check")
	bool CanCraftMultiple(const FString& RecipeID, int32 Count);

	// ============================================
	// دفعات الصياغة
	// ============================================
	UFUNCTION(BlueprintCallable, Category = "NAR|Crafting|Batch")
	bool StartBatchCrafting(const FString& RecipeID, int32 Count);

	UFUNCTION(BlueprintPure, Category = "NAR|Crafting|Batch")
	int32 GetBatchCount() const { return BatchCount; }

	UFUNCTION(BlueprintPure, Category = "NAR|Crafting|Batch")
	int32 GetBatchProgress() const { return BatchProgress; }

	// ============================================
	// الحصول على البيانات
	// ============================================
	UFUNCTION(BlueprintPure, Category = "NAR|Crafting|Data")
	FCraftingState GetCraftingState() const { return CraftingState; }

	UFUNCTION(BlueprintPure, Category = "NAR|Crafting|Data")
	int32 GetRecipeCount() const { return RecipeDatabase.Num(); }

	UFUNCTION(BlueprintPure, Category = "NAR|Crafting|Data")
	int32 GetUnlockedRecipeCount() const;

	// ============================================
	// الأحداث
	// ============================================
	DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnCraftingStarted, FCraftingRecipe, Recipe);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Crafting|Events")
	FOnCraftingStarted OnCraftingStarted;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnCraftingCompleted);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Crafting|Events")
	FOnCraftingCompleted OnCraftingCompleted;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnCraftingCancelled);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Crafting|Events")
	FOnCraftingCancelled OnCraftingCancelled;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnRecipeUnlocked, FCraftingRecipe, Recipe);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Crafting|Events")
	FOnRecipeUnlocked OnRecipeUnlocked;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnCraftingProgressUpdated);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Crafting|Events")
	FOnCraftingProgressUpdated OnCraftingProgressUpdated;

protected:
	// ============================================
	// بيانات الوصفات
	// ============================================
	UPROPERTY(BlueprintReadOnly, Category = "NAR|Crafting|Data")
	TMap<FString, FCraftingRecipe> RecipeDatabase;

	UPROPERTY(BlueprintReadOnly, Category = "NAR|Crafting|Data")
	FCraftingState CraftingState;

	// ============================================
	// الصياغة الجماعية
	// ============================================
	UPROPERTY(BlueprintReadOnly, Category = "NAR|Crafting|Data")
	int32 BatchCount = 0;

	UPROPERTY(BlueprintReadOnly, Category = "NAR|Crafting|Data")
	int32 BatchProgress = 0;

	UPROPERTY(BlueprintReadOnly, Category = "NAR|Crafting|Data")
	TArray<FString> BatchQueue;

	// ============================================
	// المؤشرات
	// ============================================
	UPROPERTY(BlueprintReadOnly, Category = "NAR|Crafting|Data")
	int32 TotalItemsCrafted = 0;

	UPROPERTY(BlueprintReadOnly, Category = "NAR|Crafting|Data")
	int32 TotalRecipesUnlocked = 0;

private:
	void CompleteCrafting();
	void UpdateBatchCrafting();
};
