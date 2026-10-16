// NAR_SkillSystem.cpp — تنفيذ نظام المهارات
#include "NAR_SkillSystem.h"
#include "Engine/World.h"

UNAR_SkillSystem::UNAR_SkillSystem()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.TickInterval = 0.1f;
}

void UNAR_SkillSystem::BeginPlay()
{
	Super::BeginPlay();
	LoadSkillData();
	UE_LOG(LogTemp, Log, TEXT("[NAR_Skill] نظام المهارات جاهز"));
}

void UNAR_SkillSystem::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
}

bool UNAR_SkillSystem::LearnSkill(const FString& SkillID)
{
	FSkill* Skill = FindSkill(SkillID);
	if (!Skill || Skill->bIsLearned)
	{
		return false;
	}

	Skill->bIsLearned = true;
	Skill->Level = 1;
	TotalSkillsLearned++;

	OnSkillLearned.Broadcast(*Skill);
	UE_LOG(LogTemp, Log, TEXT("[NAR_Skill] تعلم مهارة: %s"), *Skill->SkillName);

	return true;
}

bool UNAR_SkillSystem::UnlearnSkill(const FString& SkillID)
{
	FSkill* Skill = FindSkill(SkillID);
	if (!Skill || !Skill->bIsLearned)
	{
		return false;
	}

	Skill->bIsLearned = false;
	Skill->Level = 0;
	TotalSkillsLearned--;

	OnSkillUnlearned.Broadcast(*Skill);
	return true;
}

bool UNAR_SkillSystem::LevelUpSkill(const FString& SkillID)
{
	FSkill* Skill = FindSkill(SkillID);
	if (!Skill || !Skill->bIsLearned || Skill->Level >= Skill->MaxLevel)
	{
		return false;
	}

	Skill->Level++;
	Skill->BonusAmount = Skill->Level * 10;

	OnSkillLevelUp.Broadcast(*Skill);
	UE_LOG(LogTemp, Warning, TEXT("[NAR_Skill] ترقية مهارة: %s -> المستوى %d"), *Skill->SkillName, Skill->Level);

	return true;
}

bool UNAR_SkillSystem::CanLearnSkill(const FString& SkillID, int32 PlayerLevel)
{
	FSkill* Skill = FindSkill(SkillID);
	if (!Skill || Skill->bIsLearned)
	{
		return false;
	}

	if (PlayerLevel < Skill->Requirement.RequiredLevel)
	{
		return false;
	}

	for (const FString& PrereqID : Skill->Requirement.PrerequisiteSkills)
	{
		FSkill* PrereqSkill = FindSkill(PrereqID);
		if (!PrereqSkill || !PrereqSkill->bIsLearned)
		{
			return false;
		}
	}

	return true;
}

FSkill UNAR_SkillSystem::GetSkill(const FString& SkillID)
{
	FSkill* Skill = FindSkill(SkillID);
	if (Skill)
	{
		return *Skill;
	}

	return FSkill();
}

TArray<FSkill> UNAR_SkillSystem::GetLearnedSkills() const
{
	TArray<FSkill> LearnedSkills;

	for (const auto& Pair : SkillDatabase)
	{
		if (Pair.Value.bIsLearned)
		{
			LearnedSkills.Add(Pair.Value);
		}
	}

	return LearnedSkills;
}

TArray<FSkill> UNAR_SkillSystem::GetSkillsByCategory(ESkillCategory Category)
{
	TArray<FSkill> CategorySkills;

	for (const auto& Pair : SkillDatabase)
	{
		if (Pair.Value.Category == Category && Pair.Value.bIsLearned)
		{
			CategorySkills.Add(Pair.Value);
		}
	}

	return CategorySkills;
}

int32 UNAR_SkillSystem::GetSkillBonus(const FString& SkillID)
{
	FSkill* Skill = FindSkill(SkillID);
	if (Skill && Skill->bIsLearned)
	{
		return Skill->BonusAmount;
	}

	return 0;
}

bool UNAR_SkillSystem::ResetSkills()
{
	for (auto& Pair : SkillDatabase)
	{
		Pair.Value.bIsLearned = false;
		Pair.Value.Level = 0;
		Pair.Value.BonusAmount = 0;
	}

	TotalSkillsLearned = 0;
	UE_LOG(LogTemp, Warning, TEXT("[NAR_Skill] إعادة تعيين جميع المهارات"));

	return true;
}

void UNAR_SkillSystem::SaveSkillData()
{
	UE_LOG(LogTemp, Log, TEXT("[NAR_Skill] حفظ بيانات المهارات"));
}

void UNAR_SkillSystem::LoadSkillData()
{
	UE_LOG(LogTemp, Log, TEXT("[NAR_Skill] تحميل بيانات المهارات"));
}

FSkill* UNAR_SkillSystem::FindSkill(const FString& SkillID)
{
	if (SkillDatabase.Contains(SkillID))
	{
		return &SkillDatabase[SkillID];
	}

	return nullptr;
}
