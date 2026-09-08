// NAR_ReputationSystem.h — نظام السمعة المتقدم
// محرك اللعبة — Naris Realms

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NAR_ReputationSystem.generated.h"

// ============================================
// الفصائل
// ============================================
UENUM(BlueprintType)
enum class EFaction : uint8
{
	Nomads			UMETA(DisplayName = "البدو"),
	Merchants		UMETA(DisplayName = "التجار"),
	Templars		UMETA(DisplayName = "الفرسان"),
	Assassins		UMETA(DisplayName = "القاتلون"),
	Mages			UMETA(DisplayName = "الساحرون"),
	Guardians		UMETA(DisplayName = "الحماة"),
	Bandits			UMETA(DisplayName = "اللصوص"),
	Clergy			UMETA(DisplayName = "رجال الدين"),
	Nobles			UMETA(DisplayName = "النبلاء"),
	Beasts			UMETA(DisplayName = "الوحوش")
};

// ============================================
// مستويات السمعة
// ============================================
UENUM(BlueprintType)
enum class EReputationLevel : uint8
{
	Enemy			UMETA(DisplayName = "عدو"),
	Hostile			UMETA(DisplayName = "معادي"),
	Neutral			UMETA(DisplayName = "محايد"),
	Friendly		UMETA(DisplayName = "صديق"),
	Honored			UMETA(DisplayName = "موقر")
};

// ============================================
// بيانات السمعة
// ============================================
USTRUCT(BlueprintType)
struct FFactionReputation
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadWrite, Category = "Reputation")
	EFaction Faction = EFaction::Nomads;

	UPROPERTY(BlueprintReadWrite, Category = "Reputation")
	int32 ReputationPoints = 0;

	UPROPERTY(BlueprintReadWrite, Category = "Reputation")
	EReputationLevel Level = EReputationLevel::Neutral;

	UPROPERTY(BlueprintReadWrite, Category = "Reputation")
	float TraderDiscount = 0.0f;

	UPROPERTY(BlueprintReadWrite, Category = "Reputation")
	bool bCanTrade = true;

	UPROPERTY(BlueprintReadWrite, Category = "Reputation")
	bool bCanAcceptQuests = true;

	UPROPERTY(BlueprintReadWrite, Category = "Reputation")
	int32 UnlockedQuestCount = 0;

	UPROPERTY(BlueprintReadWrite, Category = "Reputation")
	bool bHasBetrayed = false;

	UPROPERTY(BlueprintReadWrite, Category = "Reputation")
	float BetrayalTime = 0.0f;
};

// ============================================
// نظام السمعة
// ============================================
/**
 * UNAR_ReputationSystem — نظام السمعة المتقدم
 * يدير: السمعة + الفصائل + المكافآت + الخصومات
 */
UCLASS(ClassGroup=(NAR), meta=(BlueprintSpawnableComponent))
class NARISREALMS_API UNAR_ReputationSystem : public UActorComponent
{
	GENERATED_BODY()

public:
	UNAR_ReputationSystem();

	virtual void BeginPlay() override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

	// ============================================
	// إدارة السمعة
	// ============================================
	UFUNCTION(BlueprintCallable, Category = "NAR|Reputation")
	bool ModifyReputation(EFaction Faction, int32 PointsAmount);

	UFUNCTION(BlueprintCallable, Category = "NAR|Reputation")
	FFactionReputation GetFactionReputation(EFaction Faction);

	UFUNCTION(BlueprintPure, Category = "NAR|Reputation")
	EReputationLevel GetReputationLevel(EFaction Faction);

	UFUNCTION(BlueprintPure, Category = "NAR|Reputation")
	int32 GetReputationPoints(EFaction Faction);

	UFUNCTION(BlueprintPure, Category = "NAR|Reputation")
	TArray<FFactionReputation> GetAllReputations() const;

	// ============================================
	// الخصومات والامتيازات
	// ============================================
	UFUNCTION(BlueprintCallable, Category = "NAR|Reputation|Benefits")
	float GetTraderDiscount(EFaction Faction);

	UFUNCTION(BlueprintCallable, Category = "NAR|Reputation|Benefits")
	bool CanTradeFaction(EFaction Faction);

	UFUNCTION(BlueprintCallable, Category = "NAR|Reputation|Benefits")
	bool CanAcceptFactionQuest(EFaction Faction);

	UFUNCTION(BlueprintCallable, Category = "NAR|Reputation|Benefits")
	TArray<FString> GetUnlockedBenefits(EFaction Faction);

	UFUNCTION(BlueprintCallable, Category = "NAR|Reputation|Benefits")
	int32 GetAlignmentBonus(EFaction Faction);

	// ============================================
	// الخيانة والعداوة
	// ============================================
	UFUNCTION(BlueprintCallable, Category = "NAR|Reputation|Betrayal")
	bool BetrayFaction(EFaction Faction);

	UFUNCTION(BlueprintCallable, Category = "NAR|Reputation|Betrayal")
	bool HasBetrayed(EFaction Faction);

	UFUNCTION(BlueprintCallable, Category = "NAR|Reputation|Betrayal")
	float GetBetrayalTime(EFaction Faction);

	// ============================================
	// الاستعلامات
	// ============================================
	UFUNCTION(BlueprintCallable, Category = "NAR|Reputation|Query")
	TArray<FFactionReputation> GetFactionsByLevel(EReputationLevel Level);

	UFUNCTION(BlueprintCallable, Category = "NAR|Reputation|Query")
	EFaction GetHighestReputation() const;

	UFUNCTION(BlueprintCallable, Category = "NAR|Reputation|Query")
	EFaction GetLowestReputation() const;

	UFUNCTION(BlueprintCallable, Category = "NAR|Reputation|Query")
	int32 GetTotalFactionCount() const { return FactionReputations.Num(); }

	// ============================================
	// الحفظ والتحميل
	// ============================================
	UFUNCTION(BlueprintCallable, Category = "NAR|Reputation|Save")
	void SaveReputationData();

	UFUNCTION(BlueprintCallable, Category = "NAR|Reputation|Save")
	void LoadReputationData();

	UFUNCTION(BlueprintCallable, Category = "NAR|Reputation|Save")
	void ResetAllReputations();

	// ============================================
	// الأحداث
	// ============================================
	DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnReputationChanged, EFaction, Faction, int32, NewPoints);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Reputation|Events")
	FOnReputationChanged OnReputationChanged;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnReputationLevelUp, EFaction, Faction, EReputationLevel, NewLevel);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Reputation|Events")
	FOnReputationLevelUp OnReputationLevelUp;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnReputationLevelDown, EFaction, Faction, EReputationLevel, NewLevel);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Reputation|Events")
	FOnReputationLevelDown OnReputationLevelDown;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnFactionBetray, EFaction, Faction);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Reputation|Events")
	FOnFactionBetray OnFactionBetray;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnDiscount, EFaction, Faction, float, DiscountAmount);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Reputation|Events")
	FOnDiscount OnDiscount;

protected:
	// ============================================
	// بيانات السمعة
	// ============================================
	UPROPERTY(BlueprintReadOnly, Category = "NAR|Reputation|Data")
	TArray<FFactionReputation> FactionReputations;

	// ============================================
	// الإعدادات
	// ============================================
	UPROPERTY(EditDefaultsOnly, Category = "NAR|Reputation|Settings")
	int32 PointsForLevelUp = 100;

	UPROPERTY(EditDefaultsOnly, Category = "NAR|Reputation|Settings")
	int32 MaxFactions = 10;

	UPROPERTY(EditDefaultsOnly, Category = "NAR|Reputation|Settings")
	bool bEnemyFactionsPenalty = true;

private:
	FFactionReputation* FindFactionReputation(EFaction Faction);
	void UpdateReputationLevel(EFaction Faction);
	void CheckLevelUpDown(EFaction Faction, int32 OldPoints);
	EReputationLevel GetLevelFromPoints(int32 Points) const;
};
