// NAR_SkillSystem.h — نظام المهارات المتقدم
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NAR_SkillSystem.generated.h"

UENUM(BlueprintType)
enum class ESkillCategory : uint8
{
	Combat			UMETA(DisplayName = "القتال"),
	Magic			UMETA(DisplayName = "السحر"),
	Stealth			UMETA(DisplayName = "الخفاء"),
	Survival		UMETA(DisplayName = "البقاء"),
	Crafting		UMETA(DisplayName = "الصناعة"),
	Social			UMETA(DisplayName = "التفاعل الاجتماعي")
};

UENUM(BlueprintType)
enum class ESkillRarity : uint8
{
	Common			UMETA(DisplayName = "عام"),
	Uncommon		UMETA(DisplayName = "نادر"),
	Rare			UMETA(DisplayName = "نادر جداً"),
	Legendary		UMETA(DisplayName = "أسطوري")
};

USTRUCT(BlueprintType)
struct FSkillRequirement
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadWrite, Category = "Skill")
	int32 RequiredLevel = 1;

	UPROPERTY(BlueprintReadWrite, Category = "Skill")
	TArray<FString> PrerequisiteSkills;

	UPROPERTY(BlueprintReadWrite, Category = "Skill")
	int32 SkillPointsCost = 1;
};

USTRUCT(BlueprintType)
struct FSkill
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadWrite, Category = "Skill")
	FString SkillID = FString();

	UPROPERTY(BlueprintReadWrite, Category = "Skill")
	FString SkillName = TEXT("");

	UPROPERTY(BlueprintReadWrite, Category = "Skill")
	FString SkillDescription = TEXT("");

	UPROPERTY(BlueprintReadWrite, Category = "Skill")
	ESkillCategory Category = ESkillCategory::Combat;

	UPROPERTY(BlueprintReadWrite, Category = "Skill")
	ESkillRarity Rarity = ESkillRarity::Common;

	UPROPERTY(BlueprintReadWrite, Category = "Skill")
	int32 Level = 0;

	UPROPERTY(BlueprintReadWrite, Category = "Skill")
	int32 MaxLevel = 5;

	UPROPERTY(BlueprintReadWrite, Category = "Skill")
	FSkillRequirement Requirement;

	UPROPERTY(BlueprintReadWrite, Category = "Skill")
	bool bIsLearned = false;

	UPROPERTY(BlueprintReadWrite, Category = "Skill")
	int32 BonusAmount = 0;
};

USTRUCT(BlueprintType)
struct FSkillTree
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadWrite, Category = "Skill")
	ESkillCategory Category = ESkillCategory::Combat;

	UPROPERTY(BlueprintReadWrite, Category = "Skill")
	TArray<FSkill> Skills;
};

UCLASS(ClassGroup=(NAR), meta=(BlueprintSpawnableComponent))
class NARISREALMS_API UNAR_SkillSystem : public UActorComponent
{
	GENERATED_BODY()

public:
	UNAR_SkillSystem();

	virtual void BeginPlay() override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

	UFUNCTION(BlueprintCallable, Category = "NAR|Skill")
	bool LearnSkill(const FString& SkillID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Skill")
	bool UnlearnSkill(const FString& SkillID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Skill")
	bool LevelUpSkill(const FString& SkillID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Skill")
	bool CanLearnSkill(const FString& SkillID, int32 PlayerLevel);

	UFUNCTION(BlueprintCallable, Category = "NAR|Skill")
	FSkill GetSkill(const FString& SkillID);

	UFUNCTION(BlueprintPure, Category = "NAR|Skill")
	TArray<FSkill> GetLearnedSkills() const;

	UFUNCTION(BlueprintPure, Category = "NAR|Skill")
	TArray<FSkill> GetSkillsByCategory(ESkillCategory Category);

	UFUNCTION(BlueprintCallable, Category = "NAR|Skill")
	int32 GetSkillBonus(const FString& SkillID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Skill")
	bool ResetSkills();

	UFUNCTION(BlueprintCallable, Category = "NAR|Skill")
	void SaveSkillData();

	UFUNCTION(BlueprintCallable, Category = "NAR|Skill")
	void LoadSkillData();

	DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnSkillLearned, FSkill, Skill);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Skill|Events")
	FOnSkillLearned OnSkillLearned;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnSkillLevelUp, FSkill, Skill);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Skill|Events")
	FOnSkillLevelUp OnSkillLevelUp;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnSkillUnlearned, FSkill, Skill);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Skill|Events")
	FOnSkillUnlearned OnSkillUnlearned;

protected:
	UPROPERTY(BlueprintReadOnly, Category = "NAR|Skill|Data")
	TMap<FString, FSkill> SkillDatabase;

	UPROPERTY(BlueprintReadOnly, Category = "NAR|Skill|Data")
	int32 TotalSkillsLearned = 0;

	UPROPERTY(EditDefaultsOnly, Category = "NAR|Skill|Settings")
	int32 MaxSkillsPerCategory = 10;

private:
	FSkill* FindSkill(const FString& SkillID);
};
