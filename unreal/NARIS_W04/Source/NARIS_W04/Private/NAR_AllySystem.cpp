// NAR_AllySystem.cpp — تنفيذ نظام الحلفاء
#include "NAR_AllySystem.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/World.h"

UNAR_AllySystem::UNAR_AllySystem()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.TickInterval = 0.1f;
}

void UNAR_AllySystem::BeginPlay()
{
	Super::BeginPlay();
	UE_LOG(LogTemp, Log, TEXT("[NAR_Allies] نظام الحلفاء جاهز (الحد الأقصى: %d)"), MaxAllyCount);
}

void UNAR_AllySystem::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

	// تحديث مواقع الحلفاء بشكل دوري
	UpdateAllyPositions();
}

// ============================================
// تجنيد الحلفاء
// ============================================
bool UNAR_AllySystem::RecruitAlly(const FAllyData& AllyData)
{
	if (AlliedCharacters.Num() >= MaxAllyCount)
	{
		UE_LOG(LogTemp, Warning, TEXT("[NAR_Allies] وصلت إلى الحد الأقصى من الحلفاء (%d)"), MaxAllyCount);
		return false;
	}

	if (AlliedCharacters.Contains(AllyData.AllyID))
	{
		UE_LOG(LogTemp, Warning, TEXT("[NAR_Allies] الحليف موجود بالفعل: %s"), *AllyData.AllyID);
		return false;
	}

	FAllyData NewAlly = AllyData;
	NewAlly.bIsActive = true;
	AlliedCharacters.Add(AllyData.AllyID, NewAlly);

	OnAllyRecruited.Broadcast(NewAlly);
	UE_LOG(LogTemp, Warning, TEXT("[NAR_Allies] تجنيد حليف جديد: %s (النوع: %d)"),
		*AllyData.AllyName, (int32)AllyData.AllyType);

	return true;
}

bool UNAR_AllySystem::DismissAlly(const FString& AllyID)
{
	if (!AlliedCharacters.Contains(AllyID))
	{
		return false;
	}

	AlliedCharacters.Remove(AllyID);
	OnAllyDismissed.Broadcast(AllyID);

	UE_LOG(LogTemp, Log, TEXT("[NAR_Allies] صرف حليف: %s"), *AllyID);
	return true;
}

bool UNAR_AllySystem::ReleaseAlly(const FString& AllyID)
{
	return DismissAlly(AllyID);
}

FAllyData UNAR_AllySystem::GetAlly(const FString& AllyID)
{
	if (AlliedCharacters.Contains(AllyID))
	{
		return AlliedCharacters[AllyID];
	}

	return FAllyData();
}

TArray<FAllyData> UNAR_AllySystem::GetAllAllies() const
{
	TArray<FAllyData> AllAllies;
	AlliedCharacters.GenerateValueArray(AllAllies);
	return AllAllies;
}

TArray<FAllyData> UNAR_AllySystem::GetActiveAllies() const
{
	TArray<FAllyData> ActiveAllies;

	for (const auto& Pair : AlliedCharacters)
	{
		if (Pair.Value.bIsActive && Pair.Value.AllyState != EAllyState::Dead)
		{
			ActiveAllies.Add(Pair.Value);
		}
	}

	return ActiveAllies;
}

// ============================================
// إدارة الحالة
// ============================================
void UNAR_AllySystem::SetAllyState(const FString& AllyID, EAllyState NewState)
{
	if (!AlliedCharacters.Contains(AllyID))
	{
		return;
	}

	FAllyData& Ally = AlliedCharacters[AllyID];
	EAllyState OldState = Ally.AllyState;
	Ally.AllyState = NewState;

	OnAllyStateChanged.Broadcast(AllyID, NewState);

	UE_LOG(LogTemp, Log, TEXT("[NAR_Allies] تغيير حالة %s من %d إلى %d"),
		*AllyID, (int32)OldState, (int32)NewState);
}

EAllyState UNAR_AllySystem::GetAllyState(const FString& AllyID)
{
	if (AlliedCharacters.Contains(AllyID))
	{
		return AlliedCharacters[AllyID].AllyState;
	}

	return EAllyState::Idle;
}

void UNAR_AllySystem::ActivateAlly(const FString& AllyID)
{
	if (AlliedCharacters.Contains(AllyID))
	{
		AlliedCharacters[AllyID].bIsActive = true;
		SetAllyState(AllyID, EAllyState::Following);
	}
}

void UNAR_AllySystem::DeactivateAlly(const FString& AllyID)
{
	if (AlliedCharacters.Contains(AllyID))
	{
		AlliedCharacters[AllyID].bIsActive = false;
		SetAllyState(AllyID, EAllyState::Idle);
	}
}

// ============================================
// القتال المجموعي
// ============================================
void UNAR_AllySystem::CommandAttack(const FString& AllyID, AActor* Target)
{
	if (!AlliedCharacters.Contains(AllyID) || !Target)
	{
		return;
	}

	FAllyData& Ally = AlliedCharacters[AllyID];
	Ally.TargetEnemy = Target;
	SetAllyState(AllyID, EAllyState::Attacking);

	UE_LOG(LogTemp, Log, TEXT("[NAR_Allies] أمر %s بمهاجمة %s"), *AllyID, *Target->GetName());
}

void UNAR_AllySystem::CommandAllAttack(AActor* Target)
{
	if (!Target)
	{
		return;
	}

	for (auto& Pair : AlliedCharacters)
	{
		CommandAttack(Pair.Key, Target);
	}

	UE_LOG(LogTemp, Warning, TEXT("[NAR_Allies] أمر الجميع بمهاجمة: %s"), *Target->GetName());
}

void UNAR_AllySystem::CommandHold(const FString& AllyID)
{
	if (AlliedCharacters.Contains(AllyID))
	{
		AlliedCharacters[AllyID].TargetEnemy = nullptr;
		SetAllyState(AllyID, EAllyState::Defending);
	}
}

void UNAR_AllySystem::CommandAllHold()
{
	for (auto& Pair : AlliedCharacters)
	{
		CommandHold(Pair.Key);
	}

	UE_LOG(LogTemp, Log, TEXT("[NAR_Allies] أمر الجميع بالوقوف الدفاعي"));
}

void UNAR_AllySystem::CommandFollow(const FString& AllyID, AActor* FollowTarget)
{
	if (!AlliedCharacters.Contains(AllyID) || !FollowTarget)
	{
		return;
	}

	AlliedCharacters[AllyID].TargetEnemy = nullptr;
	SetAllyState(AllyID, EAllyState::Following);
}

void UNAR_AllySystem::CommandAllFollow(AActor* FollowTarget)
{
	if (!FollowTarget)
	{
		return;
	}

	for (auto& Pair : AlliedCharacters)
	{
		CommandFollow(Pair.Key, FollowTarget);
	}

	UE_LOG(LogTemp, Log, TEXT("[NAR_Allies] أمر الجميع بمتابعة: %s"), *FollowTarget->GetName());
}

// ============================================
// المساعدة والدعم
// ============================================
void UNAR_AllySystem::HealAlly(const FString& AllyID, int32 Amount)
{
	if (!AlliedCharacters.Contains(AllyID))
	{
		return;
	}

	FAllyData& Ally = AlliedCharacters[AllyID];
	int32 OldHealth = Ally.Health;
	Ally.Health = FMath::Min(Ally.Health + Amount, Ally.MaxHealth);
	int32 ActualHeal = Ally.Health - OldHealth;

	OnAllyHealed.Broadcast(AllyID, ActualHeal);
	UE_LOG(LogTemp, Log, TEXT("[NAR_Allies] شفاء %s: +%d (الصحة: %d/%d)"),
		*AllyID, ActualHeal, Ally.Health, Ally.MaxHealth);
}

void UNAR_AllySystem::DamageAlly(const FString& AllyID, int32 Amount)
{
	if (!AlliedCharacters.Contains(AllyID))
	{
		return;
	}

	FAllyData& Ally = AlliedCharacters[AllyID];
	int32 ActualDamage = FMath::Min(Amount, Ally.Health);
	Ally.Health -= ActualDamage;

	OnAllyDamaged.Broadcast(AllyID, ActualDamage);

	if (Ally.Health <= 0)
	{
		SetAllyState(AllyID, EAllyState::Dead);
		OnAllyDied.Broadcast(AllyID);
		UE_LOG(LogTemp, Warning, TEXT("[NAR_Allies] مات الحليف: %s"), *AllyID);
	}
	else
	{
		UE_LOG(LogTemp, Log, TEXT("[NAR_Allies] إصابة %s: -%d (الصحة: %d/%d)"),
			*AllyID, ActualDamage, Ally.Health, Ally.MaxHealth);
	}
}

void UNAR_AllySystem::ReviveAlly(const FString& AllyID)
{
	if (!AlliedCharacters.Contains(AllyID))
	{
		return;
	}

	FAllyData& Ally = AlliedCharacters[AllyID];
	Ally.Health = Ally.MaxHealth;
	SetAllyState(AllyID, EAllyState::Idle);

	UE_LOG(LogTemp, Warning, TEXT("[NAR_Allies] إحياء الحليف: %s"), *AllyID);
}

bool UNAR_AllySystem::IsAllyAlive(const FString& AllyID)
{
	if (AlliedCharacters.Contains(AllyID))
	{
		return AlliedCharacters[AllyID].Health > 0;
	}

	return false;
}

// ============================================
// الإحصائيات
// ============================================
int32 UNAR_AllySystem::GetTotalAllyHealth() const
{
	int32 TotalHealth = 0;

	for (const auto& Pair : AlliedCharacters)
	{
		if (Pair.Value.AllyState != EAllyState::Dead)
		{
			TotalHealth += Pair.Value.Health;
		}
	}

	return TotalHealth;
}

int32 UNAR_AllySystem::GetTotalAllyDamage() const
{
	int32 TotalDamage = 0;

	for (const auto& Pair : AlliedCharacters)
	{
		TotalDamage += (int32)Pair.Value.Damage;
	}

	return TotalDamage;
}

float UNAR_AllySystem::GetAverageAllyLevel() const
{
	if (AlliedCharacters.Num() == 0)
	{
		return 0.0f;
	}

	float TotalLevel = 0.0f;

	for (const auto& Pair : AlliedCharacters)
	{
		TotalLevel += Pair.Value.Level;
	}

	return TotalLevel / AlliedCharacters.Num();
}

int32 UNAR_AllySystem::GetAliveAllyCount() const
{
	int32 AliveCount = 0;

	for (const auto& Pair : AlliedCharacters)
	{
		if (Pair.Value.AllyState != EAllyState::Dead && Pair.Value.Health > 0)
		{
			AliveCount++;
		}
	}

	return AliveCount;
}

int32 UNAR_AllySystem::GetDeadAllyCount() const
{
	int32 DeadCount = 0;

	for (const auto& Pair : AlliedCharacters)
	{
		if (Pair.Value.AllyState == EAllyState::Dead || Pair.Value.Health <= 0)
		{
			DeadCount++;
		}
	}

	return DeadCount;
}

// ============================================
// التطور والترقية
// ============================================
void UNAR_AllySystem::GiveExperienceToAlly(const FString& AllyID, float Amount)
{
	if (!AlliedCharacters.Contains(AllyID))
	{
		return;
	}

	FAllyData& Ally = AlliedCharacters[AllyID];
	Ally.Experience += Amount;

	while (CanLevelUp(AllyID))
	{
		LevelUpAlly(AllyID);
	}
}

void UNAR_AllySystem::LevelUpAlly(const FString& AllyID)
{
	if (!AlliedCharacters.Contains(AllyID) || !CanLevelUp(AllyID))
	{
		return;
	}

	FAllyData& Ally = AlliedCharacters[AllyID];
	Ally.Level++;
	Ally.Experience = 0.0f;

	// تحسين الإحصائيات
	Ally.MaxHealth = (int32)(Ally.MaxHealth * 1.15f);
	Ally.Health = Ally.MaxHealth;
	Ally.Damage *= 1.1f;
	Ally.Armor = (int32)(Ally.Armor * 1.05f);

	OnAllyLeveledUp.Broadcast(AllyID);
	UE_LOG(LogTemp, Warning, TEXT("[NAR_Allies] ترقية %s إلى المستوى %d"), *AllyID, Ally.Level);
}

bool UNAR_AllySystem::CanLevelUp(const FString& AllyID)
{
	if (!AlliedCharacters.Contains(AllyID))
	{
		return false;
	}

	return AlliedCharacters[AllyID].Experience >= ExperiencePerLevel;
}

void UNAR_AllySystem::BoostAllyStats(const FString& AllyID, float DamageBoost, float HealthBoost, float SpeedBoost)
{
	if (!AlliedCharacters.Contains(AllyID))
	{
		return;
	}

	FAllyData& Ally = AlliedCharacters[AllyID];
	Ally.Damage += DamageBoost;
	Ally.MaxHealth += (int32)HealthBoost;
	Ally.Health = FMath::Min(Ally.Health + (int32)HealthBoost, Ally.MaxHealth);
	Ally.MovementSpeed += SpeedBoost;

	UE_LOG(LogTemp, Log, TEXT("[NAR_Allies] تعزيز إحصائيات %s: الضرر +%.1f، الصحة +%.0f، السرعة +%.1f"),
		*AllyID, DamageBoost, HealthBoost, SpeedBoost);
}

// ============================================
// وظائف داخلية
// ============================================
void UNAR_AllySystem::UpdateAllyPositions()
{
	for (auto& Pair : AlliedCharacters)
	{
		if (Pair.Value.AllyActor && !Pair.Value.AllyActor->IsHidden())
		{
			Pair.Value.LastKnownPosition = Pair.Value.AllyActor->GetActorLocation();
		}
	}
}
