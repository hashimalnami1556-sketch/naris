// NAR_AchievementSystem.h — نظام الإنجازات
// محرك اللعبة — Naris Realms

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NAR_AchievementSystem.generated.h"

// ============================================
// أنواع الإنجازات
// ============================================
UENUM(BlueprintType)
enum class EAchievementType : uint8
{
	Combat			UMETA(DisplayName = "قتال"),
	Exploration		UMETA(DisplayName = "استكشاف"),
	Crafting		UMETA(DisplayName = "صياغة"),
	Collection		UMETA(DisplayName = "جمع"),
	Milestone		UMETA(DisplayName = "معلم"),
	Challenge		UMETA(DisplayName = "تحدي"),
	Social			UMETA(DisplayName = "اجتماعي"),
	Skill			UMETA(DisplayName = "مهارة")
};

// ============================================
// بيانات الإنجاز
// ============================================
USTRUCT(BlueprintType)
struct FAchievement
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadWrite, Category = "Achievement")
	FString AchievementID = FString();

	UPROPERTY(BlueprintReadWrite, Category = "Achievement")
	FString Title = TEXT("");

	UPROPERTY(BlueprintReadWrite, Category = "Achievement")
	FString Description = TEXT("");

	UPROPERTY(BlueprintReadWrite, Category = "Achievement")
	EAchievementType Type = EAchievementType::Milestone;

	UPROPERTY(BlueprintReadWrite, Category = "Achievement")
	int32 RewardXP = 0;

	UPROPERTY(BlueprintReadWrite, Category = "Achievement")
	int32 RewardShards = 0;

	UPROPERTY(BlueprintReadWrite, Category = "Achievement")
	bool bIsUnlocked = false;

	UPROPERTY(BlueprintReadWrite, Category = "Achievement")
	float UnlockTime = 0.0f;

	UPROPERTY(BlueprintReadWrite, Category = "Achievement")
	int32 Progress = 0;

	UPROPERTY(BlueprintReadWrite, Category = "Achievement")
	int32 ProgressGoal = 1;

	UPROPERTY(BlueprintReadWrite, Category = "Achievement")
	bool bIsHidden = false;

	UPROPERTY(BlueprintReadWrite, Category = "Achievement")
	int32 Rarity = 1; // 1 = عام، 2 = نادر، 3 = نادر جداً، 4 = أسطوري
};

// ============================================
// نظام الإنجازات
// ============================================
/**
 * UNAR_AchievementSystem — نظام الإنجازات
 * يدير: الإنجازات + التقدم + المكافآت
 */
UCLASS(ClassGroup=(NAR), meta=(BlueprintSpawnableComponent))
class NARISREALMS_API UNAR_AchievementSystem : public UActorComponent
{
	GENERATED_BODY()

public:
	UNAR_AchievementSystem();

	virtual void BeginPlay() override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

	// ============================================
	// إدارة الإنجازات
	// ============================================
	UFUNCTION(BlueprintCallable, Category = "NAR|Achievements")
	void RegisterAchievement(const FAchievement& Achievement);

	UFUNCTION(BlueprintCallable, Category = "NAR|Achievements")
	FAchievement GetAchievement(const FString& AchievementID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Achievements")
	bool UnlockAchievement(const FString& AchievementID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Achievements")
	bool IsAchievementUnlocked(const FString& AchievementID);

	UFUNCTION(BlueprintPure, Category = "NAR|Achievements")
	TArray<FAchievement> GetAllAchievements() const;

	UFUNCTION(BlueprintPure, Category = "NAR|Achievements")
	TArray<FAchievement> GetUnlockedAchievements() const;

	UFUNCTION(BlueprintPure, Category = "NAR|Achievements")
	TArray<FAchievement> GetAchievementsByType(EAchievementType Type) const;

	// ============================================
	// تحديث التقدم
	// ============================================
	UFUNCTION(BlueprintCallable, Category = "NAR|Achievements|Progress")
	void UpdateProgress(const FString& AchievementID, int32 Amount = 1);

	UFUNCTION(BlueprintCallable, Category = "NAR|Achievements|Progress")
	int32 GetProgress(const FString& AchievementID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Achievements|Progress")
	float GetProgressPercentage(const FString& AchievementID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Achievements|Progress")
	void ResetProgress(const FString& AchievementID);

	// ============================================
	// الإحصائيات
	// ============================================
	UFUNCTION(BlueprintPure, Category = "NAR|Achievements|Stats")
	int32 GetTotalAchievements() const;

	UFUNCTION(BlueprintPure, Category = "NAR|Achievements|Stats")
	int32 GetUnlockedAchievementCount() const;

	UFUNCTION(BlueprintPure, Category = "NAR|Achievements|Stats")
	float GetCompletionPercentage() const;

	UFUNCTION(BlueprintPure, Category = "NAR|Achievements|Stats")
	int32 GetTotalRewardXP() const { return TotalRewardXP; }

	UFUNCTION(BlueprintPure, Category = "NAR|Achievements|Stats")
	int32 GetTotalRewardShards() const { return TotalRewardShards; }

	// ============================================
	// التصفية والبحث
	// ============================================
	UFUNCTION(BlueprintCallable, Category = "NAR|Achievements|Search")
	TArray<FAchievement> GetRecentAchievements(int32 Count = 10);

	UFUNCTION(BlueprintCallable, Category = "NAR|Achievements|Search")
	TArray<FAchievement> GetNextAchievements(int32 Count = 5);

	UFUNCTION(BlueprintCallable, Category = "NAR|Achievements|Search")
	TArray<FAchievement> GetAchievementsByRarity(int32 Rarity);

	// ============================================
	// الحفظ والتحميل
	// ============================================
	UFUNCTION(BlueprintCallable, Category = "NAR|Achievements|Save")
	void SaveAchievements();

	UFUNCTION(BlueprintCallable, Category = "NAR|Achievements|Save")
	void LoadAchievements();

	// ============================================
	// الأحداث
	// ============================================
	DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnAchievementUnlocked, FAchievement, Achievement);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Achievements|Events")
	FOnAchievementUnlocked OnAchievementUnlocked;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnProgressUpdated, FString, AchievementID, int32, Progress);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Achievements|Events")
	FOnProgressUpdated OnProgressUpdated;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnAchievementAlmostComplete, FString, AchievementID, float, PercentComplete);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Achievements|Events")
	FOnAchievementAlmostComplete OnAchievementAlmostComplete;

protected:
	// ============================================
	// بيانات الإنجازات
	// ============================================
	UPROPERTY(BlueprintReadOnly, Category = "NAR|Achievements|Data")
	TMap<FString, FAchievement> AchievementDatabase;

	UPROPERTY(BlueprintReadOnly, Category = "NAR|Achievements|Data")
	TArray<FAchievement> RecentlyUnlocked;

	// ============================================
	// الإحصائيات
	// ============================================
	UPROPERTY(BlueprintReadOnly, Category = "NAR|Achievements|Data")
	int32 TotalRewardXP = 0;

	UPROPERTY(BlueprintReadOnly, Category = "NAR|Achievements|Data")
	int32 TotalRewardShards = 0;

	UPROPERTY(BlueprintReadOnly, Category = "NAR|Achievements|Data")
	int32 UnlockedCount = 0;

	// ============================================
	// الإعدادات
	// ============================================
	UPROPERTY(EditDefaultsOnly, Category = "NAR|Achievements|Settings")
	int32 MaxRecentAchievements = 10;

	UPROPERTY(EditDefaultsOnly, Category = "NAR|Achievements|Settings")
	float NotificationDuration = 5.0f;

private:
	void CheckForCompletion(const FString& AchievementID);
};
