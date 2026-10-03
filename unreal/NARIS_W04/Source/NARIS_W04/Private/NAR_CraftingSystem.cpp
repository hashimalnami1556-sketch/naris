// NAR_CraftingSystem.cpp — تنفيذ نظام الصياغة
#include "NAR_CraftingSystem.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/World.h"

UNAR_CraftingSystem::UNAR_CraftingSystem()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.TickInterval = 0.05f;
}

void UNAR_CraftingSystem::BeginPlay()
{
	Super::BeginPlay();
	UE_LOG(LogTemp, Log, TEXT("[NAR_Crafting] نظام الصياغة جاهز"));
}

void UNAR_CraftingSystem::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

	// تحديث الصياغة الحالية
	if (CraftingState.bIsCrafting)
	{
		CraftingState.RemainingTime -= DeltaTime;
		CraftingState.CraftingProgress = 1.0f - (CraftingState.RemainingTime / CraftingState.CurrentRecipe.CraftingTime);
		CraftingState.CraftingProgress = FMath::Clamp(CraftingState.CraftingProgress, 0.0f, 1.0f);

		OnCraftingProgressUpdated.Broadcast();

		if (CraftingState.RemainingTime <= 0.0f)
		{
			if (BatchCount > 0)
			{
				UpdateBatchCrafting();
			}
			else
			{
				CompleteCrafting();
			}
		}
	}
}

// ============================================
// إدارة الوصفات
// ============================================
void UNAR_CraftingSystem::RegisterRecipe(const FCraftingRecipe& Recipe)
{
	RecipeDatabase.Add(Recipe.RecipeID, Recipe);
	UE_LOG(LogTemp, Log, TEXT("[NAR_Crafting] تسجيل وصفة: %s"), *Recipe.RecipeName);
}

FCraftingRecipe UNAR_CraftingSystem::GetRecipe(const FString& RecipeID)
{
	if (RecipeDatabase.Contains(RecipeID))
	{
		return RecipeDatabase[RecipeID];
	}

	return FCraftingRecipe();
}

bool UNAR_CraftingSystem::UnlockRecipe(const FString& RecipeID)
{
	if (RecipeDatabase.Contains(RecipeID))
	{
		RecipeDatabase[RecipeID].bIsUnlocked = true;
		TotalRecipesUnlocked++;

		OnRecipeUnlocked.Broadcast(RecipeDatabase[RecipeID]);
		UE_LOG(LogTemp, Log, TEXT("[NAR_Crafting] فتح وصفة: %s"), *RecipeDatabase[RecipeID].RecipeName);
		return true;
	}

	return false;
}

void UNAR_CraftingSystem::LockRecipe(const FString& RecipeID)
{
	if (RecipeDatabase.Contains(RecipeID))
	{
		RecipeDatabase[RecipeID].bIsUnlocked = false;
		UE_LOG(LogTemp, Log, TEXT("[NAR_Crafting] غلق وصفة: %s"), *RecipeDatabase[RecipeID].RecipeName);
	}
}

bool UNAR_CraftingSystem::IsRecipeUnlocked(const FString& RecipeID)
{
	if (RecipeDatabase.Contains(RecipeID))
	{
		return RecipeDatabase[RecipeID].bIsUnlocked;
	}

	return false;
}

TArray<FCraftingRecipe> UNAR_CraftingSystem::GetAllRecipes() const
{
	TArray<FCraftingRecipe> AllRecipes;
	RecipeDatabase.GenerateValueArray(AllRecipes);
	return AllRecipes;
}

TArray<FCraftingRecipe> UNAR_CraftingSystem::GetUnlockedRecipes() const
{
	TArray<FCraftingRecipe> UnlockedRecipes;

	for (const auto& Pair : RecipeDatabase)
	{
		if (Pair.Value.bIsUnlocked)
		{
			UnlockedRecipes.Add(Pair.Value);
		}
	}

	return UnlockedRecipes;
}

TArray<FCraftingRecipe> UNAR_CraftingSystem::GetRecipesByLevel(int32 Level)
{
	TArray<FCraftingRecipe> RecipesByLevel;

	for (const auto& Pair : RecipeDatabase)
	{
		if (Pair.Value.RequiredLevel <= Level)
		{
			RecipesByLevel.Add(Pair.Value);
		}
	}

	return RecipesByLevel;
}

// ============================================
// الصياغة
// ============================================
bool UNAR_CraftingSystem::StartCrafting(const FString& RecipeID)
{
	if (CraftingState.bIsCrafting)
	{
		UE_LOG(LogTemp, Warning, TEXT("[NAR_Crafting] جاري بالفعل صياغة شيء آخر"));
		return false;
	}

	if (!RecipeDatabase.Contains(RecipeID))
	{
		UE_LOG(LogTemp, Error, TEXT("[NAR_Crafting] الوصفة غير موجودة: %s"), *RecipeID);
		return false;
	}

	if (!CanCraft(RecipeID))
	{
		UE_LOG(LogTemp, Warning, TEXT("[NAR_Crafting] لا يمكن صياغة: %s"), *RecipeID);
		return false;
	}

	CraftingState.CurrentRecipe = RecipeDatabase[RecipeID];
	CraftingState.bIsCrafting = true;
	CraftingState.RemainingTime = CraftingState.CurrentRecipe.CraftingTime;
	CraftingState.CraftingProgress = 0.0f;

	OnCraftingStarted.Broadcast(CraftingState.CurrentRecipe);
	UE_LOG(LogTemp, Warning, TEXT("[NAR_Crafting] بدء صياغة: %s (%.1f ثانية)"),
		*CraftingState.CurrentRecipe.RecipeName, CraftingState.CurrentRecipe.CraftingTime);

	return true;
}

void UNAR_CraftingSystem::CancelCrafting()
{
	if (!CraftingState.bIsCrafting)
	{
		return;
	}

	CraftingState.bIsCrafting = false;
	CraftingState.CraftingProgress = 0.0f;
	BatchQueue.Empty();
	BatchCount = 0;
	BatchProgress = 0;

	OnCraftingCancelled.Broadcast();
	UE_LOG(LogTemp, Log, TEXT("[NAR_Crafting] إلغاء الصياغة"));
}

bool UNAR_CraftingSystem::CanCraft(const FString& RecipeID)
{
	if (!RecipeDatabase.Contains(RecipeID))
	{
		return false;
	}

	const FCraftingRecipe& Recipe = RecipeDatabase[RecipeID];

	if (!Recipe.bIsUnlocked)
	{
		return false;
	}

	return HasAllIngredients(RecipeID);
}

// ============================================
// التحقق من المواد
// ============================================
bool UNAR_CraftingSystem::HasAllIngredients(const FString& RecipeID)
{
	if (!RecipeDatabase.Contains(RecipeID))
	{
		return false;
	}

	// في التطبيق الفعلي، سيتم التحقق من نظام الجرد
	// للآن، نعتبر أن جميع المواد متوفرة
	return true;
}

TArray<FRecipeIngredient> UNAR_CraftingSystem::GetMissingIngredients(const FString& RecipeID)
{
	TArray<FRecipeIngredient> MissingIngredients;

	if (!RecipeDatabase.Contains(RecipeID))
	{
		return MissingIngredients;
	}

	// في التطبيق الفعلي، سيتم التحقق من نظام الجرد
	return MissingIngredients;
}

bool UNAR_CraftingSystem::CanCraftMultiple(const FString& RecipeID, int32 Count)
{
	if (Count <= 0 || !RecipeDatabase.Contains(RecipeID))
	{
		return false;
	}

	const FCraftingRecipe& Recipe = RecipeDatabase[RecipeID];

	for (int32 i = 0; i < Count; ++i)
	{
		if (!HasAllIngredients(RecipeID))
		{
			return false;
		}
	}

	return true;
}

// ============================================
// دفعات الصياغة
// ============================================
bool UNAR_CraftingSystem::StartBatchCrafting(const FString& RecipeID, int32 Count)
{
	if (Count <= 0 || CraftingState.bIsCrafting)
	{
		return false;
	}

	if (!CanCraftMultiple(RecipeID, Count))
	{
		UE_LOG(LogTemp, Warning, TEXT("[NAR_Crafting] لا يمكن صياغة %d من %s"), Count, *RecipeID);
		return false;
	}

	BatchQueue.Empty();
	for (int32 i = 0; i < Count; ++i)
	{
		BatchQueue.Add(RecipeID);
	}

	BatchCount = Count;
	BatchProgress = 0;

	return StartCrafting(RecipeID);
}

// ============================================
// الحصول على البيانات
// ============================================
int32 UNAR_CraftingSystem::GetUnlockedRecipeCount() const
{
	int32 Count = 0;

	for (const auto& Pair : RecipeDatabase)
	{
		if (Pair.Value.bIsUnlocked)
		{
			Count++;
		}
	}

	return Count;
}

// ============================================
// وظائف داخلية
// ============================================
void UNAR_CraftingSystem::CompleteCrafting()
{
	CraftingState.bIsCrafting = false;
	CraftingState.CraftingProgress = 1.0f;

	TotalItemsCrafted += CraftingState.CurrentRecipe.ResultQuantity;

	OnCraftingCompleted.Broadcast();
	UE_LOG(LogTemp, Warning, TEXT("[NAR_Crafting] اكتمال صياغة: %s (الكمية: %d)"),
		*CraftingState.CurrentRecipe.RecipeName,
		CraftingState.CurrentRecipe.ResultQuantity);
}

void UNAR_CraftingSystem::UpdateBatchCrafting()
{
	if (BatchQueue.Num() > 0)
	{
		BatchProgress++;

		if (BatchProgress >= BatchCount)
		{
			// اكتملت جميع الدفعات
			CraftingState.bIsCrafting = false;
			BatchQueue.Empty();
			OnCraftingCompleted.Broadcast();

			UE_LOG(LogTemp, Warning, TEXT("[NAR_Crafting] اكتمال جميع الدفعات (%d عناصر)"), BatchCount);
		}
		else
		{
			// ابدأ الوصفة التالية
			FString NextRecipeID = BatchQueue[BatchProgress];
			if (RecipeDatabase.Contains(NextRecipeID))
			{
				CraftingState.CurrentRecipe = RecipeDatabase[NextRecipeID];
				CraftingState.RemainingTime = CraftingState.CurrentRecipe.CraftingTime;
				CraftingState.CraftingProgress = 0.0f;

				OnCraftingProgressUpdated.Broadcast();
			}
		}
	}
}
