// NAR_AllySystem.h — نظام الحلفاء
// محرك اللعبة — Naris Realms

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NAR_AllySystem.generated.h"

// ============================================
// أنواع الحلفاء
// ============================================
UENUM(BlueprintType)
enum class EAllyType : uint8
{
	Melee			UMETA(DisplayName = "قتالي"),
	Ranged			UMETA(DisplayName = "أسلحة بعيدة"),
	Support			UMETA(DisplayName = "دعم"),
	Tank			UMETA(DisplayName = "دفاع"),
	Hybrid			UMETA(DisplayName = "مختلط")
};

// ============================================
// حالة الحليف
// ============================================
UENUM(BlueprintType)
enum class EAllyState : uint8
{
	Idle			UMETA(DisplayName = "خامل"),
	Following		UMETA(DisplayName = "متابعة"),
	Attacking		UMETA(DisplayName = "هجوم"),
	Defending		UMETA(DisplayName = "دفاع"),
	Dying			UMETA(DisplayName = "احتضار"),
	Dead			UMETA(DisplayName = "ميت")
};

// ============================================
// بيانات الحليف
// ============================================
USTRUCT(BlueprintType)
struct FAllyData
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadWrite, Category = "Ally")
	FString AllyID = FString();

	UPROPERTY(BlueprintReadWrite, Category = "Ally")
	FString AllyName = TEXT("");

	UPROPERTY(BlueprintReadWrite, Category = "Ally")
	EAllyType AllyType = EAllyType::Melee;

	UPROPERTY(BlueprintReadWrite, Category = "Ally")
	EAllyState AllyState = EAllyState::Idle;

	UPROPERTY(BlueprintReadWrite, Category = "Ally")
	int32 Level = 1;

	UPROPERTY(BlueprintReadWrite, Category = "Ally")
	int32 Health = 100;

	UPROPERTY(BlueprintReadWrite, Category = "Ally")
	int32 MaxHealth = 100;

	UPROPERTY(BlueprintReadWrite, Category = "Ally")
	float Damage = 10.0f;

	UPROPERTY(BlueprintReadWrite, Category = "Ally")
	float AttackSpeed = 1.0f;

	UPROPERTY(BlueprintReadWrite, Category = "Ally")
	float MovementSpeed = 5.0f;

	UPROPERTY(BlueprintReadWrite, Category = "Ally")
	int32 Armor = 5;

	UPROPERTY(BlueprintReadWrite, Category = "Ally")
	bool bIsActive = false;

	UPROPERTY(BlueprintReadWrite, Category = "Ally")
	float Experience = 0.0f;

	UPROPERTY(BlueprintReadWrite, Category = "Ally")
	FVector LastKnownPosition = FVector::ZeroVector;

	UPROPERTY(BlueprintReadWrite, Category = "Ally")
	AActor* TargetEnemy = nullptr;

	UPROPERTY(BlueprintReadWrite, Category = "Ally")
	AActor* AllyActor = nullptr;
};

// ============================================
// نظام الحلفاء
// ============================================
/**
 * UNAR_AllySystem — نظام الحلفاء
 * يدير: الحلفاء + المجموعة + المساعدة
 */
UCLASS(ClassGroup=(NAR), meta=(BlueprintSpawnableComponent))
class NARISREALMS_API UNAR_AllySystem : public UActorComponent
{
	GENERATED_BODY()

public:
	UNAR_AllySystem();

	virtual void BeginPlay() override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

	// ============================================
	// تجنيد الحلفاء
	// ============================================
	UFUNCTION(BlueprintCallable, Category = "NAR|Allies")
	bool RecruitAlly(const FAllyData& AllyData);

	UFUNCTION(BlueprintCallable, Category = "NAR|Allies")
	bool DismissAlly(const FString& AllyID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Allies")
	bool ReleaseAlly(const FString& AllyID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Allies")
	FAllyData GetAlly(const FString& AllyID);

	UFUNCTION(BlueprintPure, Category = "NAR|Allies")
	TArray<FAllyData> GetAllAllies() const;

	UFUNCTION(BlueprintPure, Category = "NAR|Allies")
	TArray<FAllyData> GetActiveAllies() const;

	UFUNCTION(BlueprintPure, Category = "NAR|Allies")
	int32 GetAllyCount() const { return AlliedCharacters.Num(); }

	UFUNCTION(BlueprintPure, Category = "NAR|Allies")
	int32 GetMaxAllies() const { return MaxAllyCount; }

	// ============================================
	// إدارة الحالة
	// ============================================
	UFUNCTION(BlueprintCallable, Category = "NAR|Allies|State")
	void SetAllyState(const FString& AllyID, EAllyState NewState);

	UFUNCTION(BlueprintCallable, Category = "NAR|Allies|State")
	EAllyState GetAllyState(const FString& AllyID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Allies|State")
	void ActivateAlly(const FString& AllyID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Allies|State")
	void DeactivateAlly(const FString& AllyID);

	// ============================================
	// القتال المجموعي
	// ============================================
	UFUNCTION(BlueprintCallable, Category = "NAR|Allies|Combat")
	void CommandAttack(const FString& AllyID, AActor* Target);

	UFUNCTION(BlueprintCallable, Category = "NAR|Allies|Combat")
	void CommandAllAttack(AActor* Target);

	UFUNCTION(BlueprintCallable, Category = "NAR|Allies|Combat")
	void CommandHold(const FString& AllyID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Allies|Combat")
	void CommandAllHold();

	UFUNCTION(BlueprintCallable, Category = "NAR|Allies|Combat")
	void CommandFollow(const FString& AllyID, AActor* FollowTarget);

	UFUNCTION(BlueprintCallable, Category = "NAR|Allies|Combat")
	void CommandAllFollow(AActor* FollowTarget);

	// ============================================
	// المساعدة والدعم
	// ============================================
	UFUNCTION(BlueprintCallable, Category = "NAR|Allies|Support")
	void HealAlly(const FString& AllyID, int32 Amount);

	UFUNCTION(BlueprintCallable, Category = "NAR|Allies|Support")
	void DamageAlly(const FString& AllyID, int32 Amount);

	UFUNCTION(BlueprintCallable, Category = "NAR|Allies|Support")
	void ReviveAlly(const FString& AllyID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Allies|Support")
	bool IsAllyAlive(const FString& AllyID);

	// ============================================
	// الإحصائيات
	// ============================================
	UFUNCTION(BlueprintPure, Category = "NAR|Allies|Stats")
	int32 GetTotalAllyHealth() const;

	UFUNCTION(BlueprintPure, Category = "NAR|Allies|Stats")
	int32 GetTotalAllyDamage() const;

	UFUNCTION(BlueprintPure, Category = "NAR|Allies|Stats")
	float GetAverageAllyLevel() const;

	UFUNCTION(BlueprintPure, Category = "NAR|Allies|Stats")
	int32 GetAliveAllyCount() const;

	UFUNCTION(BlueprintPure, Category = "NAR|Allies|Stats")
	int32 GetDeadAllyCount() const;

	// ============================================
	// التطور والترقية
	// ============================================
	UFUNCTION(BlueprintCallable, Category = "NAR|Allies|Progression")
	void GiveExperienceToAlly(const FString& AllyID, float Amount);

	UFUNCTION(BlueprintCallable, Category = "NAR|Allies|Progression")
	void LevelUpAlly(const FString& AllyID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Allies|Progression")
	bool CanLevelUp(const FString& AllyID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Allies|Progression")
	void BoostAllyStats(const FString& AllyID, float DamageBoost, float HealthBoost, float SpeedBoost);

	// ============================================
	// الأحداث
	// ============================================
	DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnAllyRecruited, FAllyData, Ally);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Allies|Events")
	FOnAllyRecruited OnAllyRecruited;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnAllyDismissed, FString, AllyID);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Allies|Events")
	FOnAllyDismissed OnAllyDismissed;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnAllyStateChanged, FString, AllyID, EAllyState, NewState);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Allies|Events")
	FOnAllyStateChanged OnAllyStateChanged;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnAllyDamaged, FString, AllyID, int32, Damage);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Allies|Events")
	FOnAllyDamaged OnAllyDamaged;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnAllyHealed, FString, AllyID, int32, HealAmount);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Allies|Events")
	FOnAllyHealed OnAllyHealed;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnAllyDied, FString, AllyID);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Allies|Events")
	FOnAllyDied OnAllyDied;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnAllyLeveledUp, FString, AllyID);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Allies|Events")
	FOnAllyLeveledUp OnAllyLeveledUp;

protected:
	// ============================================
	// بيانات الحلفاء
	// ============================================
	UPROPERTY(BlueprintReadOnly, Category = "NAR|Allies|Data")
	TMap<FString, FAllyData> AlliedCharacters;

	UPROPERTY(EditDefaultsOnly, Category = "NAR|Allies|Settings")
	int32 MaxAllyCount = 3;

	UPROPERTY(EditDefaultsOnly, Category = "NAR|Allies|Settings")
	float ExperiencePerLevel = 100.0f;

private:
	void UpdateAllyPositions();
};
