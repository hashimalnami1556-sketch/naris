// NAR_CompanionSystem.h — نظام الرفاق المتقدم
// محرك اللعبة — Naris Realms

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NAR_CompanionSystem.generated.h"

// ============================================
// أنواع الرفاق
// ============================================
UENUM(BlueprintType)
enum class ECompanionType : uint8
{
	Warrior			UMETA(DisplayName = "محارب"),
	Archer			UMETA(DisplayName = "رامي سهام"),
	Mage			UMETA(DisplayName = "ساحر"),
	Healer			UMETA(DisplayName = "معالج"),
	Rogue			UMETA(DisplayName = "لص"),
	Beast			UMETA(DisplayName = "وحش")
};

// ============================================
// أنماط الشخصية
// ============================================
UENUM(BlueprintType)
enum class EPersonality : uint8
{
	Loyal			UMETA(DisplayName = "وفي"),
	Ambitious		UMETA(DisplayName = "طموح"),
	Neutral			UMETA(DisplayName = "محايد"),
	Dark			UMETA(DisplayName = "مظلم")
};

// ============================================
// إحصائيات الرفيق
// ============================================
USTRUCT(BlueprintType)
struct FCompanionStats
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadWrite, Category = "Companion")
	int32 Level = 1;

	UPROPERTY(BlueprintReadWrite, Category = "Companion")
	int32 Experience = 0;

	UPROPERTY(BlueprintReadWrite, Category = "Companion")
	int32 Health = 100;

	UPROPERTY(BlueprintReadWrite, Category = "Companion")
	int32 MaxHealth = 100;

	UPROPERTY(BlueprintReadWrite, Category = "Companion")
	int32 Damage = 10;

	UPROPERTY(BlueprintReadWrite, Category = "Companion")
	float AttackSpeed = 1.0f;

	UPROPERTY(BlueprintReadWrite, Category = "Companion")
	float MovementSpeed = 600.0f;

	UPROPERTY(BlueprintReadWrite, Category = "Companion")
	int32 Armor = 5;

	UPROPERTY(BlueprintReadWrite, Category = "Companion")
	int32 MagicResist = 0;
};

// ============================================
// بيانات العلاقة
// ============================================
USTRUCT(BlueprintType)
struct FRelationshipData
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadWrite, Category = "Companion")
	int32 Loyalty = 50;

	UPROPERTY(BlueprintReadWrite, Category = "Companion")
	int32 Trust = 50;

	UPROPERTY(BlueprintReadWrite, Category = "Companion")
	int32 Affection = 0;

	UPROPERTY(BlueprintReadWrite, Category = "Companion")
	float BetrayalRisk = 0.0f;

	UPROPERTY(BlueprintReadWrite, Category = "Companion")
	int32 InteractionCount = 0;

	UPROPERTY(BlueprintReadWrite, Category = "Companion")
	float LastInteractionTime = 0.0f;
};

// ============================================
// بيانات الرفيق
// ============================================
USTRUCT(BlueprintType)
struct FCompanionData
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadWrite, Category = "Companion")
	FString CompanionID = FString();

	UPROPERTY(BlueprintReadWrite, Category = "Companion")
	FString CompanionName = TEXT("");

	UPROPERTY(BlueprintReadWrite, Category = "Companion")
	ECompanionType CompanionType = ECompanionType::Warrior;

	UPROPERTY(BlueprintReadWrite, Category = "Companion")
	EPersonality Personality = EPersonality::Loyal;

	UPROPERTY(BlueprintReadWrite, Category = "Companion")
	FCompanionStats Stats;

	UPROPERTY(BlueprintReadWrite, Category = "Companion")
	FRelationshipData Relationship;

	UPROPERTY(BlueprintReadWrite, Category = "Companion")
	AActor* CompanionActor = nullptr;

	UPROPERTY(BlueprintReadWrite, Category = "Companion")
	FString PersonalQuestID = FString();

	UPROPERTY(BlueprintReadWrite, Category = "Companion")
	bool bIsRecruited = false;

	UPROPERTY(BlueprintReadWrite, Category = "Companion")
	bool bIsActive = false;

	UPROPERTY(BlueprintReadWrite, Category = "Companion")
	float JoinedTime = 0.0f;

	UPROPERTY(BlueprintReadWrite, Category = "Companion")
	TArray<FString> UnlockedSkills;

	UPROPERTY(BlueprintReadWrite, Category = "Companion")
	TArray<FString> FavoriteGifts;
};

// ============================================
// نظام الرفاق
// ============================================
/**
 * UNAR_CompanionSystem — نظام الرفاق المتقدم
 * يدير: الرفاق + العلاقات + المهارات + المهام الفردية
 */
UCLASS(ClassGroup=(NAR), meta=(BlueprintSpawnableComponent))
class NARISREALMS_API UNAR_CompanionSystem : public UActorComponent
{
	GENERATED_BODY()

public:
	UNAR_CompanionSystem();

	virtual void BeginPlay() override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

	// ============================================
	// إدارة الرفاق
	// ============================================
	UFUNCTION(BlueprintCallable, Category = "NAR|Companion")
	bool RecruitCompanion(const FCompanionData& CompanionData);

	UFUNCTION(BlueprintCallable, Category = "NAR|Companion")
	bool RemoveCompanion(const FString& CompanionID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Companion")
	FCompanionData GetCompanion(const FString& CompanionID);

	UFUNCTION(BlueprintPure, Category = "NAR|Companion")
	TArray<FCompanionData> GetAllCompanions() const;

	UFUNCTION(BlueprintPure, Category = "NAR|Companion")
	TArray<FCompanionData> GetActiveCompanions() const;

	UFUNCTION(BlueprintPure, Category = "NAR|Companion")
	int32 GetCompanionCount() const { return CompanionDatabase.Num(); }

	// ============================================
	// إدارة العلاقات
	// ============================================
	UFUNCTION(BlueprintCallable, Category = "NAR|Companion|Relationship")
	bool ModifyRelationship(const FString& CompanionID, int32 LoyaltyChange, int32 TrustChange);

	UFUNCTION(BlueprintCallable, Category = "NAR|Companion|Relationship")
	int32 GetLoyalty(const FString& CompanionID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Companion|Relationship")
	int32 GetTrust(const FString& CompanionID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Companion|Relationship")
	bool GiftCompanion(const FString& CompanionID, const FString& GiftItemID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Companion|Relationship")
	float GetBetrayalRisk(const FString& CompanionID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Companion|Relationship")
	bool CheckBetray(const FString& CompanionID);

	// ============================================
	// إدارة المستويات والخبرة
	// ============================================
	UFUNCTION(BlueprintCallable, Category = "NAR|Companion|Growth")
	bool LevelUpCompanion(const FString& CompanionID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Companion|Growth")
	bool GainExperience(const FString& CompanionID, int32 ExperienceAmount);

	UFUNCTION(BlueprintCallable, Category = "NAR|Companion|Growth")
	int32 GetExperienceNeeded(const FString& CompanionID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Companion|Growth")
	bool BoostCompanionStats(const FString& CompanionID, int32 HealthBoost, int32 DamageBoost, int32 ArmorBoost);

	// ============================================
	// المهام الفردية
	// ============================================
	UFUNCTION(BlueprintCallable, Category = "NAR|Companion|Quest")
	bool StartPersonalQuest(const FString& CompanionID, const FString& QuestID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Companion|Quest")
	bool CompletePersonalQuest(const FString& CompanionID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Companion|Quest")
	FString GetPersonalQuest(const FString& CompanionID);

	// ============================================
	// المهارات
	// ============================================
	UFUNCTION(BlueprintCallable, Category = "NAR|Companion|Skills")
	bool UnlockSkill(const FString& CompanionID, const FString& SkillID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Companion|Skills")
	bool LearnSkill(const FString& CompanionID, const FString& SkillID);

	UFUNCTION(BlueprintPure, Category = "NAR|Companion|Skills")
	TArray<FString> GetUnlockedSkills(const FString& CompanionID);

	// ============================================
	// الحوار والديناميكية
	// ============================================
	UFUNCTION(BlueprintCallable, Category = "NAR|Companion|Dialogue")
	FString GetCompanionDialogue(const FString& CompanionID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Companion|Dialogue")
	bool UpdateCompanionMood(const FString& CompanionID, int32 MoodChange);

	UFUNCTION(BlueprintPure, Category = "NAR|Companion|Dialogue")
	EPersonality GetPersonality(const FString& CompanionID);

	// ============================================
	// الاستعلامات والإحصائيات
	// ============================================
	UFUNCTION(BlueprintCallable, Category = "NAR|Companion|Query")
	TArray<FCompanionData> GetCompanionsByType(ECompanionType CompanionType);

	UFUNCTION(BlueprintCallable, Category = "NAR|Companion|Query")
	int32 GetTotalCompanions() const { return CompanionDatabase.Num(); }

	UFUNCTION(BlueprintPure, Category = "NAR|Companion|Query")
	int32 GetRecruitedCount() const;

	UFUNCTION(BlueprintCallable, Category = "NAR|Companion|Query")
	bool IsCompanionRecruited(const FString& CompanionID);

	// ============================================
	// الحفظ والتحميل
	// ============================================
	UFUNCTION(BlueprintCallable, Category = "NAR|Companion|Save")
	void SaveCompanionData();

	UFUNCTION(BlueprintCallable, Category = "NAR|Companion|Save")
	void LoadCompanionData();

	UFUNCTION(BlueprintCallable, Category = "NAR|Companion|Save")
	void ResetAllCompanions();

	// ============================================
	// الأحداث
	// ============================================
	DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnCompanionRecruited, FCompanionData, Companion);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Companion|Events")
	FOnCompanionRecruited OnCompanionRecruited;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnCompanionRemoved, FCompanionData, Companion);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Companion|Events")
	FOnCompanionRemoved OnCompanionRemoved;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnRelationshipChanged, FString, CompanionID, FRelationshipData, Relationship);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Companion|Events")
	FOnRelationshipChanged OnRelationshipChanged;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnCompanionLeveledUp, FString, CompanionID, int32, NewLevel);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Companion|Events")
	FOnCompanionLeveledUp OnCompanionLeveledUp;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnCompanionBetray, FCompanionData, Companion);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Companion|Events")
	FOnCompanionBetray OnCompanionBetray;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnPersonalQuestStarted, FString, CompanionID, FString, QuestID);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Companion|Events")
	FOnPersonalQuestStarted OnPersonalQuestStarted;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnPersonalQuestCompleted, FString, CompanionID);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Companion|Events")
	FOnPersonalQuestCompleted OnPersonalQuestCompleted;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnSkillUnlocked, FString, CompanionID, FString, SkillID);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Companion|Events")
	FOnSkillUnlocked OnSkillUnlocked;

protected:
	// ============================================
	// بيانات الرفاق
	// ============================================
	UPROPERTY(BlueprintReadOnly, Category = "NAR|Companion|Data")
	TMap<FString, FCompanionData> CompanionDatabase;

	// ============================================
	// الإحصائيات
	// ============================================
	UPROPERTY(BlueprintReadOnly, Category = "NAR|Companion|Data")
	int32 RecruitedCount = 0;

	UPROPERTY(BlueprintReadOnly, Category = "NAR|Companion|Data")
	int32 BetrayalCount = 0;

	// ============================================
	// الإعدادات
	// ============================================
	UPROPERTY(EditDefaultsOnly, Category = "NAR|Companion|Settings")
	int32 MaxCompanions = 3;

	UPROPERTY(EditDefaultsOnly, Category = "NAR|Companion|Settings")
	int32 ExperiencePerLevel = 100;

	UPROPERTY(EditDefaultsOnly, Category = "NAR|Companion|Settings")
	float LoyaltyDecayRate = 0.5f;

private:
	void UpdateCompanionRelationships(float DeltaTime);
	int32 GetExperienceThreshold(int32 Level) const;
};
