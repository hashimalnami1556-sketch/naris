// NAR_ReputationSystem.cpp — تنفيذ نظام السمعة
#include "NAR_ReputationSystem.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/World.h"

UNAR_ReputationSystem::UNAR_ReputationSystem()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.TickInterval = 0.1f;

	// تهيئة الفصائل
	for (int32 i = 0; i < MaxFactions; i++)
	{
		FFactionReputation FactionRep;
		FactionRep.Faction = (EFaction)i;
		FactionRep.ReputationPoints = 0;
		FactionRep.Level = EReputationLevel::Neutral;
		FactionRep.TraderDiscount = 0.0f;
		FactionRep.bCanTrade = true;
		FactionRep.bCanAcceptQuests = true;
		FactionReputations.Add(FactionRep);
	}
}

void UNAR_ReputationSystem::BeginPlay()
{
	Super::BeginPlay();
	LoadReputationData();
	UE_LOG(LogTemp, Log, TEXT("[NAR_Reputation] نظام السمعة جاهز"));
}

void UNAR_ReputationSystem::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	// تحديثات دورية
}

// ============================================
// إدارة السمعة
// ============================================
bool UNAR_ReputationSystem::ModifyReputation(EFaction Faction, int32 PointsAmount)
{
	FFactionReputation* FactionRep = FindFactionReputation(Faction);
	if (!FactionRep)
	{
		return false;
	}

	int32 OldPoints = FactionRep->ReputationPoints;
	FactionRep->ReputationPoints += PointsAmount;
	FactionRep->ReputationPoints = FMath::Clamp(FactionRep->ReputationPoints, -500, 500);

	// تحديث الخصم التاجر
	FactionRep->TraderDiscount = FMath::Clamp((float)FactionRep->ReputationPoints / 500.0f * 0.5f, -0.25f, 0.5f);

	OnReputationChanged.Broadcast(Faction, FactionRep->ReputationPoints);
	CheckLevelUpDown(Faction, OldPoints);

	UE_LOG(LogTemp, Log, TEXT("[NAR_Reputation] تعديل السمعة: %d (%d نقاط)"), (int32)Faction, FactionRep->ReputationPoints);

	return true;
}

FFactionReputation UNAR_ReputationSystem::GetFactionReputation(EFaction Faction)
{
	FFactionReputation* FactionRep = FindFactionReputation(Faction);
	if (FactionRep)
	{
		return *FactionRep;
	}

	return FFactionReputation();
}

EReputationLevel UNAR_ReputationSystem::GetReputationLevel(EFaction Faction)
{
	FFactionReputation* FactionRep = FindFactionReputation(Faction);
	if (FactionRep)
	{
		return FactionRep->Level;
	}

	return EReputationLevel::Neutral;
}

int32 UNAR_ReputationSystem::GetReputationPoints(EFaction Faction)
{
	FFactionReputation* FactionRep = FindFactionReputation(Faction);
	if (FactionRep)
	{
		return FactionRep->ReputationPoints;
	}

	return 0;
}

TArray<FFactionReputation> UNAR_ReputationSystem::GetAllReputations() const
{
	return FactionReputations;
}

// ============================================
// الخصومات والامتيازات
// ============================================
float UNAR_ReputationSystem::GetTraderDiscount(EFaction Faction)
{
	FFactionReputation* FactionRep = FindFactionReputation(Faction);
	if (FactionRep)
	{
		return FactionRep->TraderDiscount;
	}

	return 0.0f;
}

bool UNAR_ReputationSystem::CanTradeFaction(EFaction Faction)
{
	FFactionReputation* FactionRep = FindFactionReputation(Faction);
	if (FactionRep)
	{
		return FactionRep->bCanTrade && FactionRep->Level != EReputationLevel::Enemy;
	}

	return false;
}

bool UNAR_ReputationSystem::CanAcceptFactionQuest(EFaction Faction)
{
	FFactionReputation* FactionRep = FindFactionReputation(Faction);
	if (FactionRep)
	{
		return FactionRep->bCanAcceptQuests && FactionRep->Level != EReputationLevel::Enemy;
	}

	return false;
}

TArray<FString> UNAR_ReputationSystem::GetUnlockedBenefits(EFaction Faction)
{
	TArray<FString> Benefits;

	FFactionReputation* FactionRep = FindFactionReputation(Faction);
	if (FactionRep)
	{
		switch (FactionRep->Level)
		{
		case EReputationLevel::Friendly:
			Benefits.Add(TEXT("خصم تجاري 10%"));
			Benefits.Add(TEXT("مهام إضافية"));
			break;
		case EReputationLevel::Honored:
			Benefits.Add(TEXT("خصم تجاري 30%"));
			Benefits.Add(TEXT("مهام فريدة"));
			Benefits.Add(TEXT("عناصر حصرية"));
			break;
		default:
			break;
		}
	}

	return Benefits;
}

int32 UNAR_ReputationSystem::GetAlignmentBonus(EFaction Faction)
{
	FFactionReputation* FactionRep = FindFactionReputation(Faction);
	if (FactionRep && FactionRep->Level == EReputationLevel::Honored)
	{
		return 50;
	}

	return 0;
}

// ============================================
// الخيانة والعداوة
// ============================================
bool UNAR_ReputationSystem::BetrayFaction(EFaction Faction)
{
	FFactionReputation* FactionRep = FindFactionReputation(Faction);
	if (!FactionRep)
	{
		return false;
	}

	FactionRep->bHasBetrayed = true;
	FactionRep->BetrayalTime = GetWorld()->GetTimeSeconds();
	FactionRep->ReputationPoints -= 200;

	OnFactionBetray.Broadcast(Faction);
	UE_LOG(LogTemp, Warning, TEXT("[NAR_Reputation] خيانة الفصيلة: %d"), (int32)Faction);

	return true;
}

bool UNAR_ReputationSystem::HasBetrayed(EFaction Faction)
{
	FFactionReputation* FactionRep = FindFactionReputation(Faction);
	if (FactionRep)
	{
		return FactionRep->bHasBetrayed;
	}

	return false;
}

float UNAR_ReputationSystem::GetBetrayalTime(EFaction Faction)
{
	FFactionReputation* FactionRep = FindFactionReputation(Faction);
	if (FactionRep)
	{
		return FactionRep->BetrayalTime;
	}

	return 0.0f;
}

// ============================================
// الاستعلامات
// ============================================
TArray<FFactionReputation> UNAR_ReputationSystem::GetFactionsByLevel(EReputationLevel Level)
{
	TArray<FFactionReputation> FilteredFactions;

	for (const FFactionReputation& Faction : FactionReputations)
	{
		if (Faction.Level == Level)
		{
			FilteredFactions.Add(Faction);
		}
	}

	return FilteredFactions;
}

EFaction UNAR_ReputationSystem::GetHighestReputation() const
{
	int32 MaxPoints = -500;
	EFaction HighestFaction = EFaction::Nomads;

	for (const FFactionReputation& Faction : FactionReputations)
	{
		if (Faction.ReputationPoints > MaxPoints)
		{
			MaxPoints = Faction.ReputationPoints;
			HighestFaction = Faction.Faction;
		}
	}

	return HighestFaction;
}

EFaction UNAR_ReputationSystem::GetLowestReputation() const
{
	int32 MinPoints = 500;
	EFaction LowestFaction = EFaction::Nomads;

	for (const FFactionReputation& Faction : FactionReputations)
	{
		if (Faction.ReputationPoints < MinPoints)
		{
			MinPoints = Faction.ReputationPoints;
			LowestFaction = Faction.Faction;
		}
	}

	return LowestFaction;
}

// ============================================
// الحفظ والتحميل
// ============================================
void UNAR_ReputationSystem::SaveReputationData()
{
	UE_LOG(LogTemp, Log, TEXT("[NAR_Reputation] حفظ بيانات السمعة"));
}

void UNAR_ReputationSystem::LoadReputationData()
{
	UE_LOG(LogTemp, Log, TEXT("[NAR_Reputation] تحميل بيانات السمعة"));
}

void UNAR_ReputationSystem::ResetAllReputations()
{
	for (FFactionReputation& Faction : FactionReputations)
	{
		Faction.ReputationPoints = 0;
		Faction.Level = EReputationLevel::Neutral;
		Faction.TraderDiscount = 0.0f;
		Faction.bHasBetrayed = false;
	}

	UE_LOG(LogTemp, Warning, TEXT("[NAR_Reputation] إعادة تعيين جميع السمعات"));
}

// ============================================
// وظائف داخلية
// ============================================
FFactionReputation* UNAR_ReputationSystem::FindFactionReputation(EFaction Faction)
{
	for (FFactionReputation& FactionRep : FactionReputations)
	{
		if (FactionRep.Faction == Faction)
		{
			return &FactionRep;
		}
	}

	return nullptr;
}

void UNAR_ReputationSystem::UpdateReputationLevel(EFaction Faction)
{
	FFactionReputation* FactionRep = FindFactionReputation(Faction);
	if (FactionRep)
	{
		FactionRep->Level = GetLevelFromPoints(FactionRep->ReputationPoints);
	}
}

void UNAR_ReputationSystem::CheckLevelUpDown(EFaction Faction, int32 OldPoints)
{
	FFactionReputation* FactionRep = FindFactionReputation(Faction);
	if (!FactionRep)
	{
		return;
	}

	EReputationLevel OldLevel = GetLevelFromPoints(OldPoints);
	EReputationLevel NewLevel = GetLevelFromPoints(FactionRep->ReputationPoints);

	if (NewLevel != OldLevel)
	{
		FactionRep->Level = NewLevel;

		if (NewLevel > OldLevel)
		{
			OnReputationLevelUp.Broadcast(Faction, NewLevel);
			UE_LOG(LogTemp, Warning, TEXT("[NAR_Reputation] ارتقاء مستوى السمعة: %d -> %d"), (int32)Faction, (int32)NewLevel);
		}
		else
		{
			OnReputationLevelDown.Broadcast(Faction, NewLevel);
		}
	}
}

EReputationLevel UNAR_ReputationSystem::GetLevelFromPoints(int32 Points) const
{
	if (Points < -200)
		return EReputationLevel::Enemy;
	if (Points < -50)
		return EReputationLevel::Hostile;
	if (Points < 100)
		return EReputationLevel::Neutral;
	if (Points < 250)
		return EReputationLevel::Friendly;
	return EReputationLevel::Honored;
}
