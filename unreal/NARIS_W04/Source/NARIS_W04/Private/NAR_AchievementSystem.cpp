// NAR_AchievementSystem.cpp — تنفيذ نظام الإنجازات
#include "NAR_AchievementSystem.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/World.h"

UNAR_AchievementSystem::UNAR_AchievementSystem()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.TickInterval = 0.5f;
}

void UNAR_AchievementSystem::BeginPlay()
{
	Super::BeginPlay();
	LoadAchievements();
	UE_LOG(LogTemp, Log, TEXT("[NAR_Achievements] نظام الإنجازات جاهز"));
}

void UNAR_AchievementSystem::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	// منطق الإنجازات الدوري
}

// ============================================
// إدارة الإنجازات
// ============================================
void UNAR_AchievementSystem::RegisterAchievement(const FAchievement& Achievement)
{
	AchievementDatabase.Add(Achievement.AchievementID, Achievement);
	UE_LOG(LogTemp, Log, TEXT("[NAR_Achievements] تسجيل إنجاز: %s"), *Achievement.Title);
}

FAchievement UNAR_AchievementSystem::GetAchievement(const FString& AchievementID)
{
	if (AchievementDatabase.Contains(AchievementID))
	{
		return AchievementDatabase[AchievementID];
	}

	return FAchievement();
}

bool UNAR_AchievementSystem::UnlockAchievement(const FString& AchievementID)
{
	if (!AchievementDatabase.Contains(AchievementID))
	{
		return false;
	}

	FAchievement& Achievement = AchievementDatabase[AchievementID];

	if (Achievement.bIsUnlocked)
	{
		return false; // بالفعل مفتوح
	}

	Achievement.bIsUnlocked = true;
	Achievement.UnlockTime = GetWorld()->GetTimeSeconds();

	UnlockedCount++;
	TotalRewardXP += Achievement.RewardXP;
	TotalRewardShards += Achievement.RewardShards;

	RecentlyUnlocked.Insert(Achievement, 0);
	if (RecentlyUnlocked.Num() > MaxRecentAchievements)
	{
		RecentlyUnlocked.RemoveAt(MaxRecentAchievements);
	}

	OnAchievementUnlocked.Broadcast(Achievement);
	UE_LOG(LogTemp, Warning, TEXT("[NAR_Achievements] فتح إنجاز: %s (+%d XP, +%d Shards)"),
		*Achievement.Title, Achievement.RewardXP, Achievement.RewardShards);

	return true;
}

bool UNAR_AchievementSystem::IsAchievementUnlocked(const FString& AchievementID)
{
	if (AchievementDatabase.Contains(AchievementID))
	{
		return AchievementDatabase[AchievementID].bIsUnlocked;
	}

	return false;
}

TArray<FAchievement> UNAR_AchievementSystem::GetAllAchievements() const
{
	TArray<FAchievement> AllAchievements;
	AchievementDatabase.GenerateValueArray(AllAchievements);
	return AllAchievements;
}

TArray<FAchievement> UNAR_AchievementSystem::GetUnlockedAchievements() const
{
	TArray<FAchievement> UnlockedAchievements;

	for (const auto& Pair : AchievementDatabase)
	{
		if (Pair.Value.bIsUnlocked)
		{
			UnlockedAchievements.Add(Pair.Value);
		}
	}

	return UnlockedAchievements;
}

TArray<FAchievement> UNAR_AchievementSystem::GetAchievementsByType(EAchievementType Type) const
{
	TArray<FAchievement> TypeAchievements;

	for (const auto& Pair : AchievementDatabase)
	{
		if (Pair.Value.Type == Type)
		{
			TypeAchievements.Add(Pair.Value);
		}
	}

	return TypeAchievements;
}

// ============================================
// تحديث التقدم
// ============================================
void UNAR_AchievementSystem::UpdateProgress(const FString& AchievementID, int32 Amount)
{
	if (!AchievementDatabase.Contains(AchievementID))
	{
		return;
	}

	FAchievement& Achievement = AchievementDatabase[AchievementID];

	if (Achievement.bIsUnlocked)
	{
		return; // مفتوح بالفعل
	}

	Achievement.Progress = FMath::Min(Achievement.Progress + Amount, Achievement.ProgressGoal);

	OnProgressUpdated.Broadcast(AchievementID, Achievement.Progress);

	// التحقق من الاكتمال
	CheckForCompletion(AchievementID);

	// إذا كنا قريبين من الاكتمال (90%)
	if (!Achievement.bIsUnlocked)
	{
		float PercentComplete = (float)Achievement.Progress / Achievement.ProgressGoal;
		if (PercentComplete >= 0.9f)
		{
			OnAchievementAlmostComplete.Broadcast(AchievementID, PercentComplete);
		}
	}
}

int32 UNAR_AchievementSystem::GetProgress(const FString& AchievementID)
{
	if (AchievementDatabase.Contains(AchievementID))
	{
		return AchievementDatabase[AchievementID].Progress;
	}

	return 0;
}

float UNAR_AchievementSystem::GetProgressPercentage(const FString& AchievementID)
{
	if (AchievementDatabase.Contains(AchievementID))
	{
		const FAchievement& Achievement = AchievementDatabase[AchievementID];
		return Achievement.ProgressGoal > 0 ? (float)Achievement.Progress / Achievement.ProgressGoal : 0.0f;
	}

	return 0.0f;
}

void UNAR_AchievementSystem::ResetProgress(const FString& AchievementID)
{
	if (AchievementDatabase.Contains(AchievementID))
	{
		AchievementDatabase[AchievementID].Progress = 0;
		UE_LOG(LogTemp, Log, TEXT("[NAR_Achievements] إعادة تعيين تقدم إنجاز: %s"), *AchievementID);
	}
}

// ============================================
// الإحصائيات
// ============================================
int32 UNAR_AchievementSystem::GetTotalAchievements() const
{
	return AchievementDatabase.Num();
}

int32 UNAR_AchievementSystem::GetUnlockedAchievementCount() const
{
	return UnlockedCount;
}

float UNAR_AchievementSystem::GetCompletionPercentage() const
{
	if (AchievementDatabase.Num() == 0)
	{
		return 0.0f;
	}

	return (float)UnlockedCount / AchievementDatabase.Num() * 100.0f;
}

// ============================================
// التصفية والبحث
// ============================================
TArray<FAchievement> UNAR_AchievementSystem::GetRecentAchievements(int32 Count)
{
	TArray<FAchievement> Result;

	for (int32 i = 0; i < FMath::Min(Count, RecentlyUnlocked.Num()); ++i)
	{
		Result.Add(RecentlyUnlocked[i]);
	}

	return Result;
}

TArray<FAchievement> UNAR_AchievementSystem::GetNextAchievements(int32 Count)
{
	TArray<FAchievement> NextAchievements;
	int32 Added = 0;

	for (const auto& Pair : AchievementDatabase)
	{
		if (!Pair.Value.bIsUnlocked && !Pair.Value.bIsHidden)
		{
			NextAchievements.Add(Pair.Value);
			Added++;

			if (Added >= Count)
			{
				break;
			}
		}
	}

	return NextAchievements;
}

TArray<FAchievement> UNAR_AchievementSystem::GetAchievementsByRarity(int32 Rarity)
{
	TArray<FAchievement> RarityAchievements;

	for (const auto& Pair : AchievementDatabase)
	{
		if (Pair.Value.Rarity == Rarity)
		{
			RarityAchievements.Add(Pair.Value);
		}
	}

	return RarityAchievements;
}

// ============================================
// الحفظ والتحميل
// ============================================
void UNAR_AchievementSystem::SaveAchievements()
{
	// سيتم تطبيق الحفظ مع نظام الحفظ الرئيسي
	UE_LOG(LogTemp, Log, TEXT("[NAR_Achievements] حفظ الإنجازات (%d مفتوحة)"), UnlockedCount);
}

void UNAR_AchievementSystem::LoadAchievements()
{
	// سيتم تطبيق التحميل مع نظام الحفظ الرئيسي
	UE_LOG(LogTemp, Log, TEXT("[NAR_Achievements] تحميل الإنجازات"));
}

// ============================================
// وظائف داخلية
// ============================================
void UNAR_AchievementSystem::CheckForCompletion(const FString& AchievementID)
{
	if (!AchievementDatabase.Contains(AchievementID))
	{
		return;
	}

	FAchievement& Achievement = AchievementDatabase[AchievementID];

	if (Achievement.Progress >= Achievement.ProgressGoal && !Achievement.bIsUnlocked)
	{
		UnlockAchievement(AchievementID);
	}
}
