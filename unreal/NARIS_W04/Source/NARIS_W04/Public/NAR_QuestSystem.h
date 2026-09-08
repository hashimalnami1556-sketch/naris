// NAR_QuestSystem.h — نظام المهام المتقدم
// محرك اللعبة — Naris Realms

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NAR_QuestSystem.generated.h"

// ============================================
// أنواع المهام
// ============================================
UENUM(BlueprintType)
enum class EQuestType : uint8
{
	MainStory			UMETA(DisplayName = "قصة رئيسية"),
	SideQuest			UMETA(DisplayName = "مهمة جانبية"),
	DailyQuest			UMETA(DisplayName = "مهمة يومية"),
	WeeklyQuest			UMETA(DisplayName = "مهمة أسبوعية"),
	RepeatableQuest		UMETA(DisplayName = "مهمة متكررة")
};

// ============================================
// أنواع الأهداف
// ============================================
UENUM(BlueprintType)
enum class EQuestObjectiveType : uint8
{
	Kill				UMETA(DisplayName = "قتل الأعداء"),
	Collect				UMETA(DisplayName = "جمع العناصر"),
	Talk				UMETA(DisplayName = "التحدث للشخصيات"),
	Reach				UMETA(DisplayName = "الوصول للموقع"),
	Defend				UMETA(DisplayName = "الدفاع عن الموقع"),
	Destroy				UMETA(DisplayName = "تدمير الأشياء"),
	Custom				UMETA(DisplayName = "هدف مخصص")
};

// ============================================
// مستويات صعوبة المهام
// ============================================
UENUM(BlueprintType)
enum class EQuestDifficulty : uint8
{
	Easy				UMETA(DisplayName = "سهلة"),
	Normal				UMETA(DisplayName = "عادية"),
	Hard				UMETA(DisplayName = "صعبة"),
	Legendary			UMETA(DisplayName = "أسطورية")
};

// ============================================
// حالة المهمة
// ============================================
UENUM(BlueprintType)
enum class EQuestState : uint8
{
	Inactive			UMETA(DisplayName = "غير نشطة"),
	Active				UMETA(DisplayName = "نشطة"),
	Completed			UMETA(DisplayName = "مكتملة"),
	Failed				UMETA(DisplayName = "فاشلة"),
	Abandoned			UMETA(DisplayName = "مهجورة")
};

// ============================================
// بيانات الهدف
// ============================================
USTRUCT(BlueprintType)
struct FQuestObjective
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadWrite, Category = "Quest")
	FString ObjectiveID = FString();

	UPROPERTY(BlueprintReadWrite, Category = "Quest")
	FString ObjectiveDescription = TEXT("");

	UPROPERTY(BlueprintReadWrite, Category = "Quest")
	EQuestObjectiveType ObjectiveType = EQuestObjectiveType::Custom;

	UPROPERTY(BlueprintReadWrite, Category = "Quest")
	int32 RequiredCount = 1;

	UPROPERTY(BlueprintReadWrite, Category = "Quest")
	int32 CurrentCount = 0;

	UPROPERTY(BlueprintReadWrite, Category = "Quest")
	bool bIsCompleted = false;

	UPROPERTY(BlueprintReadWrite, Category = "Quest")
	bool bIsOptional = false;

	UPROPERTY(BlueprintReadWrite, Category = "Quest")
	FVector TargetLocation = FVector::ZeroVector;

	UPROPERTY(BlueprintReadWrite, Category = "Quest")
	float ActivationRadius = 500.0f;
};

// ============================================
// بيانات المكافآت
// ============================================
USTRUCT(BlueprintType)
struct FQuestReward
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadWrite, Category = "Quest")
	int32 RewardXP = 0;

	UPROPERTY(BlueprintReadWrite, Category = "Quest")
	int32 RewardCurrency = 0;

	UPROPERTY(BlueprintReadWrite, Category = "Quest")
	TArray<FString> RewardItems;

	UPROPERTY(BlueprintReadWrite, Category = "Quest")
	int32 RewardReputation = 0;

	UPROPERTY(BlueprintReadWrite, Category = "Quest")
	FString RewardAchievementID = FString();

	UPROPERTY(BlueprintReadWrite, Category = "Quest")
	bool bRewardSkillPoint = false;
};

// ============================================
// بيانات المهمة
// ============================================
USTRUCT(BlueprintType)
struct FQuestData
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadWrite, Category = "Quest")
	FString QuestID = FString();

	UPROPERTY(BlueprintReadWrite, Category = "Quest")
	FString QuestName = TEXT("");

	UPROPERTY(BlueprintReadWrite, Category = "Quest")
	FString QuestDescription = TEXT("");

	UPROPERTY(BlueprintReadWrite, Category = "Quest")
	EQuestType QuestType = EQuestType::SideQuest;

	UPROPERTY(BlueprintReadWrite, Category = "Quest")
	EQuestDifficulty Difficulty = EQuestDifficulty::Normal;

	UPROPERTY(BlueprintReadWrite, Category = "Quest")
	EQuestState State = EQuestState::Inactive;

	UPROPERTY(BlueprintReadWrite, Category = "Quest")
	int32 RequiredLevel = 1;

	UPROPERTY(BlueprintReadWrite, Category = "Quest")
	TArray<FQuestObjective> Objectives;

	UPROPERTY(BlueprintReadWrite, Category = "Quest")
	FQuestReward Reward;

	UPROPERTY(BlueprintReadWrite, Category = "Quest")
	bool bIsHidden = false;

	UPROPERTY(BlueprintReadWrite, Category = "Quest")
	float TimeLimit = 0.0f;

	UPROPERTY(BlueprintReadWrite, Category = "Quest")
	float RemainingTime = 0.0f;

	UPROPERTY(BlueprintReadWrite, Category = "Quest")
	FString GiverNPC = FString();

	UPROPERTY(BlueprintReadWrite, Category = "Quest")
	FString TurnInNPC = FString();

	UPROPERTY(BlueprintReadWrite, Category = "Quest")
	TArray<FString> PrerequisiteQuests;

	UPROPERTY(BlueprintReadWrite, Category = "Quest")
	bool bCanFail = true;

	UPROPERTY(BlueprintReadWrite, Category = "Quest")
	float AcceptedTime = 0.0f;

	UPROPERTY(BlueprintReadWrite, Category = "Quest")
	float CompletedTime = 0.0f;
};

// ============================================
// نظام المهام
// ============================================
/**
 * UNAR_QuestSystem — نظام المهام المتقدم
 * يدير: المهام + الأهداف + المكافآت + التقدم
 */
UCLASS(ClassGroup=(NAR), meta=(BlueprintSpawnableComponent))
class NARISREALMS_API UNAR_QuestSystem : public UActorComponent
{
	GENERATED_BODY()

public:
	UNAR_QuestSystem();

	virtual void BeginPlay() override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

	// ============================================
	// إدارة المهام
	// ============================================
	UFUNCTION(BlueprintCallable, Category = "NAR|Quest")
	bool RegisterQuest(const FQuestData& QuestData);

	UFUNCTION(BlueprintCallable, Category = "NAR|Quest")
	bool UnregisterQuest(const FString& QuestID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Quest")
	FQuestData GetQuest(const FString& QuestID);

	UFUNCTION(BlueprintPure, Category = "NAR|Quest")
	TArray<FQuestData> GetAllQuests() const;

	UFUNCTION(BlueprintPure, Category = "NAR|Quest")
	TArray<FQuestData> GetActiveQuests() const;

	UFUNCTION(BlueprintPure, Category = "NAR|Quest")
	TArray<FQuestData> GetCompletedQuests() const;

	UFUNCTION(BlueprintPure, Category = "NAR|Quest")
	int32 GetQuestCount() const { return QuestDatabase.Num(); }

	// ============================================
	// قبول وإنهاء المهام
	// ============================================
	UFUNCTION(BlueprintCallable, Category = "NAR|Quest|Actions")
	bool AcceptQuest(const FString& QuestID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Quest|Actions")
	bool AbandonQuest(const FString& QuestID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Quest|Actions")
	bool CompleteQuest(const FString& QuestID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Quest|Actions")
	bool FailQuest(const FString& QuestID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Quest|Actions")
	bool CanAcceptQuest(const FString& QuestID, int32 PlayerLevel);

	// ============================================
	// إدارة الأهداف
	// ============================================
	UFUNCTION(BlueprintCallable, Category = "NAR|Quest|Objectives")
	bool UpdateObjectiveProgress(const FString& QuestID, const FString& ObjectiveID, int32 ProgressAmount);

	UFUNCTION(BlueprintCallable, Category = "NAR|Quest|Objectives")
	bool CompleteObjective(const FString& QuestID, const FString& ObjectiveID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Quest|Objectives")
	FQuestObjective GetObjective(const FString& QuestID, const FString& ObjectiveID);

	UFUNCTION(BlueprintPure, Category = "NAR|Quest|Objectives")
	TArray<FQuestObjective> GetQuestObjectives(const FString& QuestID);

	UFUNCTION(BlueprintPure, Category = "NAR|Quest|Objectives")
	float GetObjectiveProgress(const FString& QuestID, const FString& ObjectiveID);

	// ============================================
	// المكافآت
	// ============================================
	UFUNCTION(BlueprintCallable, Category = "NAR|Quest|Rewards")
	FQuestReward GetQuestReward(const FString& QuestID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Quest|Rewards")
	bool ClaimQuestReward(const FString& QuestID);

	UFUNCTION(BlueprintPure, Category = "NAR|Quest|Rewards")
	int32 GetTotalRewardXP() const { return TotalRewardXP; }

	UFUNCTION(BlueprintPure, Category = "NAR|Quest|Rewards")
	int32 GetTotalRewardCurrency() const { return TotalRewardCurrency; }

	// ============================================
	// الاستعلامات
	// ============================================
	UFUNCTION(BlueprintCallable, Category = "NAR|Quest|Query")
	TArray<FQuestData> GetQuestsByType(EQuestType QuestType);

	UFUNCTION(BlueprintCallable, Category = "NAR|Quest|Query")
	TArray<FQuestData> GetQuestsByDifficulty(EQuestDifficulty Difficulty);

	UFUNCTION(BlueprintCallable, Category = "NAR|Quest|Query")
	bool IsQuestAvailable(const FString& QuestID, int32 PlayerLevel);

	UFUNCTION(BlueprintCallable, Category = "NAR|Quest|Query")
	float GetCompletionPercentage() const;

	// ============================================
	// الحفظ والتحميل
	// ============================================
	UFUNCTION(BlueprintCallable, Category = "NAR|Quest|Save")
	void SaveQuestData();

	UFUNCTION(BlueprintCallable, Category = "NAR|Quest|Save")
	void LoadQuestData();

	UFUNCTION(BlueprintCallable, Category = "NAR|Quest|Save")
	void ResetAllQuests();

	// ============================================
	// الأحداث
	// ============================================
	DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnQuestAccepted, FQuestData, Quest);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Quest|Events")
	FOnQuestAccepted OnQuestAccepted;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnQuestCompleted, FQuestData, Quest);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Quest|Events")
	FOnQuestCompleted OnQuestCompleted;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnQuestFailed, FQuestData, Quest);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Quest|Events")
	FOnQuestFailed OnQuestFailed;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnObjectiveUpdated, FString, QuestID, FQuestObjective, Objective);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Quest|Events")
	FOnObjectiveUpdated OnObjectiveUpdated;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnRewardClaimed, FString, QuestID, FQuestReward, Reward);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Quest|Events")
	FOnRewardClaimed OnRewardClaimed;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnQuestAbandoned, FQuestData, Quest);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Quest|Events")
	FOnQuestAbandoned OnQuestAbandoned;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnQuestProgressChanged, FString, QuestID, float, Progress);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Quest|Events")
	FOnQuestProgressChanged OnQuestProgressChanged;

protected:
	// ============================================
	// بيانات المهام
	// ============================================
	UPROPERTY(BlueprintReadOnly, Category = "NAR|Quest|Data")
	TMap<FString, FQuestData> QuestDatabase;

	// ============================================
	// الإحصائيات
	// ============================================
	UPROPERTY(BlueprintReadOnly, Category = "NAR|Quest|Data")
	int32 TotalRewardXP = 0;

	UPROPERTY(BlueprintReadOnly, Category = "NAR|Quest|Data")
	int32 TotalRewardCurrency = 0;

	UPROPERTY(BlueprintReadOnly, Category = "NAR|Quest|Data")
	int32 CompletedQuestCount = 0;

	UPROPERTY(BlueprintReadOnly, Category = "NAR|Quest|Data")
	int32 FailedQuestCount = 0;

	UPROPERTY(BlueprintReadOnly, Category = "NAR|Quest|Data")
	TArray<FString> RecentlyCompleted;

	// ============================================
	// الإعدادات
	// ============================================
	UPROPERTY(EditDefaultsOnly, Category = "NAR|Quest|Settings")
	int32 MaxActiveQuests = 10;

	UPROPERTY(EditDefaultsOnly, Category = "NAR|Quest|Settings")
	int32 MaxRecentQuests = 20;

	UPROPERTY(EditDefaultsOnly, Category = "NAR|Quest|Settings")
	bool bAutoCompleteOnAllObjectives = true;

private:
	void UpdateQuestTimers(float DeltaTime);
	void CheckQuestFailures();
	int32 GetActiveQuestCount() const;
	void AddRecentCompletion(const FString& QuestID);
};
