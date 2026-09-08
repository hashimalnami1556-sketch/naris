// NAR_CompanionSystem.cpp — تنفيذ نظام الرفاق
#include "NAR_CompanionSystem.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/World.h"

UNAR_CompanionSystem::UNAR_CompanionSystem()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.TickInterval = 0.1f;
}

void UNAR_CompanionSystem::BeginPlay()
{
	Super::BeginPlay();
	LoadCompanionData();
	UE_LOG(LogTemp, Log, TEXT("[NAR_Companion] نظام الرفاق جاهز"));
}

void UNAR_CompanionSystem::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	UpdateCompanionRelationships(DeltaTime);
}

// ============================================
// إدارة الرفاق
// ============================================
bool UNAR_CompanionSystem::RecruitCompanion(const FCompanionData& CompanionData)
{
	if (CompanionDatabase.Contains(CompanionData.CompanionID))
	{
		return false;
	}

	if (GetRecruitedCount() >= MaxCompanions)
	{
		UE_LOG(LogTemp, Warning, TEXT("[NAR_Companion] تم الوصول للحد الأقصى للرفاق"));
		return false;
	}

	FCompanionData NewCompanion = CompanionData;
	NewCompanion.bIsRecruited = true;
	NewCompanion.JoinedTime = GetWorld()->GetTimeSeconds();

	CompanionDatabase.Add(CompanionData.CompanionID, NewCompanion);
	RecruitedCount++;

	OnCompanionRecruited.Broadcast(NewCompanion);
	UE_LOG(LogTemp, Log, TEXT("[NAR_Companion] تجنيد رفيق: %s"), *NewCompanion.CompanionName);

	return true;
}

bool UNAR_CompanionSystem::RemoveCompanion(const FString& CompanionID)
{
	if (!CompanionDatabase.Contains(CompanionID))
	{
		return false;
	}

	FCompanionData Companion = CompanionDatabase[CompanionID];
	CompanionDatabase.Remove(CompanionID);
	RecruitedCount--;

	OnCompanionRemoved.Broadcast(Companion);
	UE_LOG(LogTemp, Log, TEXT("[NAR_Companion] إزالة رفيق: %s"), *CompanionID);

	return true;
}

FCompanionData UNAR_CompanionSystem::GetCompanion(const FString& CompanionID)
{
	if (CompanionDatabase.Contains(CompanionID))
	{
		return CompanionDatabase[CompanionID];
	}

	return FCompanionData();
}

TArray<FCompanionData> UNAR_CompanionSystem::GetAllCompanions() const
{
	TArray<FCompanionData> AllCompanions;
	CompanionDatabase.GenerateValueArray(AllCompanions);
	return AllCompanions;
}

TArray<FCompanionData> UNAR_CompanionSystem::GetActiveCompanions() const
{
	TArray<FCompanionData> ActiveCompanions;

	for (const auto& Pair : CompanionDatabase)
	{
		if (Pair.Value.bIsActive)
		{
			ActiveCompanions.Add(Pair.Value);
		}
	}

	return ActiveCompanions;
}

// ============================================
// إدارة العلاقات
// ============================================
bool UNAR_CompanionSystem::ModifyRelationship(const FString& CompanionID, int32 LoyaltyChange, int32 TrustChange)
{
	if (!CompanionDatabase.Contains(CompanionID))
	{
		return false;
	}

	FCompanionData& Companion = CompanionDatabase[CompanionID];
	Companion.Relationship.Loyalty = FMath::Clamp(Companion.Relationship.Loyalty + LoyaltyChange, 0, 100);
	Companion.Relationship.Trust = FMath::Clamp(Companion.Relationship.Trust + TrustChange, 0, 100);

	OnRelationshipChanged.Broadcast(CompanionID, Companion.Relationship);
	UE_LOG(LogTemp, Log, TEXT("[NAR_Companion] تعديل العلاقة: %s (الولاء: %d، الثقة: %d)"),
		*CompanionID, Companion.Relationship.Loyalty, Companion.Relationship.Trust);

	return true;
}

int32 UNAR_CompanionSystem::GetLoyalty(const FString& CompanionID)
{
	if (CompanionDatabase.Contains(CompanionID))
	{
		return CompanionDatabase[CompanionID].Relationship.Loyalty;
	}

	return 0;
}

int32 UNAR_CompanionSystem::GetTrust(const FString& CompanionID)
{
	if (CompanionDatabase.Contains(CompanionID))
	{
		return CompanionDatabase[CompanionID].Relationship.Trust;
	}

	return 0;
}

bool UNAR_CompanionSystem::GiftCompanion(const FString& CompanionID, const FString& GiftItemID)
{
	if (!CompanionDatabase.Contains(CompanionID))
	{
		return false;
	}

	FCompanionData& Companion = CompanionDatabase[CompanionID];

	// تحسين الحب والثقة من خلال الهدايا
	int32 AffectionBoost = 10;
	if (Companion.FavoriteGifts.Contains(GiftItemID))
	{
		AffectionBoost = 25;
	}

	Companion.Relationship.Affection += AffectionBoost;
	Companion.Relationship.Trust = FMath::Clamp(Companion.Relationship.Trust + 5, 0, 100);

	OnRelationshipChanged.Broadcast(CompanionID, Companion.Relationship);
	UE_LOG(LogTemp, Log, TEXT("[NAR_Companion] إهداء هدية: %s إلى %s"), *GiftItemID, *CompanionID);

	return true;
}

float UNAR_CompanionSystem::GetBetrayalRisk(const FString& CompanionID)
{
	if (!CompanionDatabase.Contains(CompanionID))
	{
		return 0.0f;
	}

	const FCompanionData& Companion = CompanionDatabase[CompanionID];
	return Companion.Relationship.BetrayalRisk;
}

bool UNAR_CompanionSystem::CheckBetray(const FString& CompanionID)
{
	if (!CompanionDatabase.Contains(CompanionID))
	{
		return false;
	}

	FCompanionData& Companion = CompanionDatabase[CompanionID];

	if (Companion.Relationship.Loyalty < 20 && FMath::Rand() % 100 < Companion.Relationship.BetrayalRisk)
	{
		BetrayalCount++;
		OnCompanionBetray.Broadcast(Companion);
		RemoveCompanion(CompanionID);
		UE_LOG(LogTemp, Warning, TEXT("[NAR_Companion] خيانة من: %s"), *CompanionID);
		return true;
	}

	return false;
}

// ============================================
// إدارة المستويات والخبرة
// ============================================
bool UNAR_CompanionSystem::LevelUpCompanion(const FString& CompanionID)
{
	if (!CompanionDatabase.Contains(CompanionID))
	{
		return false;
	}

	FCompanionData& Companion = CompanionDatabase[CompanionID];
	Companion.Stats.Level++;
	Companion.Stats.Experience = 0;

	// زيادة الإحصائيات عند الترقية
	Companion.Stats.MaxHealth = FMath::RoundToInt(Companion.Stats.MaxHealth * 1.15f);
	Companion.Stats.Health = Companion.Stats.MaxHealth;
	Companion.Stats.Damage = FMath::RoundToInt(Companion.Stats.Damage * 1.1f);
	Companion.Stats.Armor = FMath::RoundToInt(Companion.Stats.Armor * 1.05f);

	OnCompanionLeveledUp.Broadcast(CompanionID, Companion.Stats.Level);
	UE_LOG(LogTemp, Warning, TEXT("[NAR_Companion] ترقية مستوى الرفيق: %s إلى المستوى %d"),
		*CompanionID, Companion.Stats.Level);

	return true;
}

bool UNAR_CompanionSystem::GainExperience(const FString& CompanionID, int32 ExperienceAmount)
{
	if (!CompanionDatabase.Contains(CompanionID))
	{
		return false;
	}

	FCompanionData& Companion = CompanionDatabase[CompanionID];
	Companion.Stats.Experience += ExperienceAmount;

	int32 ExperienceNeeded = GetExperienceThreshold(Companion.Stats.Level);
	while (Companion.Stats.Experience >= ExperienceNeeded)
	{
		Companion.Stats.Experience -= ExperienceNeeded;
		LevelUpCompanion(CompanionID);
		ExperienceNeeded = GetExperienceThreshold(Companion.Stats.Level);
	}

	return true;
}

int32 UNAR_CompanionSystem::GetExperienceNeeded(const FString& CompanionID)
{
	if (!CompanionDatabase.Contains(CompanionID))
	{
		return 0;
	}

	const FCompanionData& Companion = CompanionDatabase[CompanionID];
	int32 Needed = GetExperienceThreshold(Companion.Stats.Level);
	return Needed - Companion.Stats.Experience;
}

bool UNAR_CompanionSystem::BoostCompanionStats(const FString& CompanionID, int32 HealthBoost, int32 DamageBoost, int32 ArmorBoost)
{
	if (!CompanionDatabase.Contains(CompanionID))
	{
		return false;
	}

	FCompanionData& Companion = CompanionDatabase[CompanionID];
	Companion.Stats.MaxHealth += HealthBoost;
	Companion.Stats.Health = FMath::Min(Companion.Stats.Health + HealthBoost, Companion.Stats.MaxHealth);
	Companion.Stats.Damage += DamageBoost;
	Companion.Stats.Armor += ArmorBoost;

	return true;
}

// ============================================
// المهام الفردية
// ============================================
bool UNAR_CompanionSystem::StartPersonalQuest(const FString& CompanionID, const FString& QuestID)
{
	if (!CompanionDatabase.Contains(CompanionID))
	{
		return false;
	}

	FCompanionData& Companion = CompanionDatabase[CompanionID];
	Companion.PersonalQuestID = QuestID;

	OnPersonalQuestStarted.Broadcast(CompanionID, QuestID);
	UE_LOG(LogTemp, Log, TEXT("[NAR_Companion] بدء مهمة فردية: %s -> %s"), *CompanionID, *QuestID);

	return true;
}

bool UNAR_CompanionSystem::CompletePersonalQuest(const FString& CompanionID)
{
	if (!CompanionDatabase.Contains(CompanionID))
	{
		return false;
	}

	FCompanionData& Companion = CompanionDatabase[CompanionID];
	Companion.PersonalQuestID = TEXT("");

	OnPersonalQuestCompleted.Broadcast(CompanionID);
	return true;
}

FString UNAR_CompanionSystem::GetPersonalQuest(const FString& CompanionID)
{
	if (CompanionDatabase.Contains(CompanionID))
	{
		return CompanionDatabase[CompanionID].PersonalQuestID;
	}

	return FString();
}

// ============================================
// المهارات
// ============================================
bool UNAR_CompanionSystem::UnlockSkill(const FString& CompanionID, const FString& SkillID)
{
	if (!CompanionDatabase.Contains(CompanionID))
	{
		return false;
	}

	FCompanionData& Companion = CompanionDatabase[CompanionID];
	if (!Companion.UnlockedSkills.Contains(SkillID))
	{
		Companion.UnlockedSkills.Add(SkillID);
		OnSkillUnlocked.Broadcast(CompanionID, SkillID);
		return true;
	}

	return false;
}

bool UNAR_CompanionSystem::LearnSkill(const FString& CompanionID, const FString& SkillID)
{
	return UnlockSkill(CompanionID, SkillID);
}

TArray<FString> UNAR_CompanionSystem::GetUnlockedSkills(const FString& CompanionID)
{
	TArray<FString> Skills;

	if (CompanionDatabase.Contains(CompanionID))
	{
		Skills = CompanionDatabase[CompanionID].UnlockedSkills;
	}

	return Skills;
}

// ============================================
// الحوار والديناميكية
// ============================================
FString UNAR_CompanionSystem::GetCompanionDialogue(const FString& CompanionID)
{
	if (!CompanionDatabase.Contains(CompanionID))
	{
		return TEXT("");
	}

	const FCompanionData& Companion = CompanionDatabase[CompanionID];

	// حوار ديناميكي حسب الشخصية والعلاقة
	if (Companion.Relationship.Loyalty > 80)
	{
		return TEXT("أنت قائدي الموثوق! سأتبعك أينما تذهب!");
	}
	else if (Companion.Relationship.Loyalty < 30)
	{
		return TEXT("أنا هنا، لكن لا تتوقع مني أن أحبك...");
	}

	return TEXT("دعنا نعمل معاً.");
}

bool UNAR_CompanionSystem::UpdateCompanionMood(const FString& CompanionID, int32 MoodChange)
{
	if (!CompanionDatabase.Contains(CompanionID))
	{
		return false;
	}

	FCompanionData& Companion = CompanionDatabase[CompanionID];
	Companion.Relationship.Affection += MoodChange;

	return true;
}

EPersonality UNAR_CompanionSystem::GetPersonality(const FString& CompanionID)
{
	if (CompanionDatabase.Contains(CompanionID))
	{
		return CompanionDatabase[CompanionID].Personality;
	}

	return EPersonality::Neutral;
}

// ============================================
// الاستعلامات والإحصائيات
// ============================================
TArray<FCompanionData> UNAR_CompanionSystem::GetCompanionsByType(ECompanionType CompanionType)
{
	TArray<FCompanionData> FilteredCompanions;

	for (const auto& Pair : CompanionDatabase)
	{
		if (Pair.Value.CompanionType == CompanionType)
		{
			FilteredCompanions.Add(Pair.Value);
		}
	}

	return FilteredCompanions;
}

int32 UNAR_CompanionSystem::GetRecruitedCount() const
{
	int32 Count = 0;

	for (const auto& Pair : CompanionDatabase)
	{
		if (Pair.Value.bIsRecruited)
		{
			Count++;
		}
	}

	return Count;
}

bool UNAR_CompanionSystem::IsCompanionRecruited(const FString& CompanionID)
{
	if (CompanionDatabase.Contains(CompanionID))
	{
		return CompanionDatabase[CompanionID].bIsRecruited;
	}

	return false;
}

// ============================================
// الحفظ والتحميل
// ============================================
void UNAR_CompanionSystem::SaveCompanionData()
{
	UE_LOG(LogTemp, Log, TEXT("[NAR_Companion] حفظ بيانات الرفاق"));
}

void UNAR_CompanionSystem::LoadCompanionData()
{
	UE_LOG(LogTemp, Log, TEXT("[NAR_Companion] تحميل بيانات الرفاق"));
}

void UNAR_CompanionSystem::ResetAllCompanions()
{
	for (auto& Pair : CompanionDatabase)
	{
		Pair.Value.bIsRecruited = false;
		Pair.Value.bIsActive = false;
		Pair.Value.Stats.Level = 1;
		Pair.Value.Stats.Experience = 0;
		Pair.Value.Relationship.Loyalty = 50;
		Pair.Value.Relationship.Trust = 50;
	}

	RecruitedCount = 0;
	BetrayalCount = 0;

	UE_LOG(LogTemp, Warning, TEXT("[NAR_Companion] إعادة تعيين جميع الرفاق"));
}

// ============================================
// وظائف داخلية
// ============================================
void UNAR_CompanionSystem::UpdateCompanionRelationships(float DeltaTime)
{
	for (auto& Pair : CompanionDatabase)
	{
		FCompanionData& Companion = Pair.Value;

		// تناقص الولاء بمرور الوقت إذا لم يتم التفاعل معهم
		if (Companion.bIsRecruited)
		{
			Companion.Relationship.BetrayalRisk = FMath::Max(0.0f, 100.0f - Companion.Relationship.Loyalty);

			// تحديث خطر الخيانة
			if (Companion.Relationship.Loyalty < 30)
			{
				Companion.Relationship.BetrayalRisk = FMath::Min(100.0f, Companion.Relationship.BetrayalRisk + LoyaltyDecayRate);
			}
		}
	}
}

int32 UNAR_CompanionSystem::GetExperienceThreshold(int32 Level) const
{
	return ExperiencePerLevel * Level;
}
