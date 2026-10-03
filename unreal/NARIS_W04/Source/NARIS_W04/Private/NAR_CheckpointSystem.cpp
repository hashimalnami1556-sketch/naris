// NAR_CheckpointSystem.cpp — تنفيذ نظام نقاط الحفظ
#include "NAR_CheckpointSystem.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/World.h"

UNAR_CheckpointSystem::UNAR_CheckpointSystem()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.TickInterval = 0.1f;
}

void UNAR_CheckpointSystem::BeginPlay()
{
	Super::BeginPlay();
	LoadCheckpointData();
	UE_LOG(LogTemp, Log, TEXT("[NAR_Checkpoint] نظام نقاط الحفظ جاهز"));
}

void UNAR_CheckpointSystem::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	// تحديثات دورية
}

// ============================================
// إدارة نقاط الحفظ
// ============================================
bool UNAR_CheckpointSystem::RegisterCheckpoint(const FCheckpointData& CheckpointData)
{
	if (CheckpointDatabase.Contains(CheckpointData.CheckpointID))
	{
		UE_LOG(LogTemp, Warning, TEXT("[NAR_Checkpoint] نقطة حفظ موجودة بالفعل: %s"), *CheckpointData.CheckpointID);
		return false;
	}

	CheckpointDatabase.Add(CheckpointData.CheckpointID, CheckpointData);
	UE_LOG(LogTemp, Log, TEXT("[NAR_Checkpoint] تسجيل نقطة حفظ: %s في %s"),
		*CheckpointData.CheckpointName, *CheckpointData.Region);

	return true;
}

bool UNAR_CheckpointSystem::UnregisterCheckpoint(const FString& CheckpointID)
{
	if (!CheckpointDatabase.Contains(CheckpointID))
	{
		return false;
	}

	CheckpointDatabase.Remove(CheckpointID);
	UE_LOG(LogTemp, Log, TEXT("[NAR_Checkpoint] إزالة نقطة حفظ: %s"), *CheckpointID);

	return true;
}

FCheckpointData UNAR_CheckpointSystem::GetCheckpoint(const FString& CheckpointID)
{
	if (CheckpointDatabase.Contains(CheckpointID))
	{
		return CheckpointDatabase[CheckpointID];
	}

	return FCheckpointData();
}

TArray<FCheckpointData> UNAR_CheckpointSystem::GetAllCheckpoints() const
{
	TArray<FCheckpointData> AllCheckpoints;
	CheckpointDatabase.GenerateValueArray(AllCheckpoints);
	return AllCheckpoints;
}

TArray<FCheckpointData> UNAR_CheckpointSystem::GetUnlockedCheckpoints() const
{
	TArray<FCheckpointData> UnlockedCheckpoints;

	for (const auto& Pair : CheckpointDatabase)
	{
		if (Pair.Value.bIsUnlocked)
		{
			UnlockedCheckpoints.Add(Pair.Value);
		}
	}

	return UnlockedCheckpoints;
}

TArray<FCheckpointData> UNAR_CheckpointSystem::GetCheckpointsByRegion(const FString& RegionName)
{
	TArray<FCheckpointData> RegionCheckpoints;

	for (const auto& Pair : CheckpointDatabase)
	{
		if (Pair.Value.Region == RegionName)
		{
			RegionCheckpoints.Add(Pair.Value);
		}
	}

	return RegionCheckpoints;
}

TArray<FCheckpointData> UNAR_CheckpointSystem::GetCheckpointsByType(ECheckpointType Type)
{
	TArray<FCheckpointData> TypeCheckpoints;

	for (const auto& Pair : CheckpointDatabase)
	{
		if (Pair.Value.CheckpointType == Type)
		{
			TypeCheckpoints.Add(Pair.Value);
		}
	}

	return TypeCheckpoints;
}

// ============================================
// تنشيط وفتح
// ============================================
bool UNAR_CheckpointSystem::ActivateCheckpoint(const FString& CheckpointID)
{
	if (!CheckpointDatabase.Contains(CheckpointID))
	{
		return false;
	}

	FCheckpointData& Checkpoint = CheckpointDatabase[CheckpointID];
	Checkpoint.bIsActive = true;
	Checkpoint.LastUsedTime = GetWorld()->GetTimeSeconds();
	Checkpoint.TimesUsed++;

	OnCheckpointActivated.Broadcast(CheckpointID, true);
	OnCheckpointUsed.Broadcast(CheckpointID);

	UE_LOG(LogTemp, Log, TEXT("[NAR_Checkpoint] تنشيط نقطة حفظ: %s"), *CheckpointID);

	return true;
}

bool UNAR_CheckpointSystem::DeactivateCheckpoint(const FString& CheckpointID)
{
	if (!CheckpointDatabase.Contains(CheckpointID))
	{
		return false;
	}

	FCheckpointData& Checkpoint = CheckpointDatabase[CheckpointID];
	Checkpoint.bIsActive = false;

	OnCheckpointActivated.Broadcast(CheckpointID, false);

	UE_LOG(LogTemp, Log, TEXT("[NAR_Checkpoint] إيقاف تنشيط نقطة حفظ: %s"), *CheckpointID);

	return true;
}

bool UNAR_CheckpointSystem::UnlockCheckpoint(const FString& CheckpointID)
{
	if (!CheckpointDatabase.Contains(CheckpointID))
	{
		return false;
	}

	FCheckpointData& Checkpoint = CheckpointDatabase[CheckpointID];
	if (Checkpoint.bIsUnlocked)
	{
		return false;
	}

	Checkpoint.bIsUnlocked = true;
	UnlockedCount++;

	OnCheckpointUnlocked.Broadcast(Checkpoint);
	UE_LOG(LogTemp, Warning, TEXT("[NAR_Checkpoint] فتح نقطة حفظ: %s"), *CheckpointData.CheckpointName);

	return true;
}

bool UNAR_CheckpointSystem::IsCheckpointUnlocked(const FString& CheckpointID)
{
	if (CheckpointDatabase.Contains(CheckpointID))
	{
		return CheckpointDatabase[CheckpointID].bIsUnlocked;
	}

	return false;
}

bool UNAR_CheckpointSystem::CanActivateCheckpoint(const FString& CheckpointID)
{
	if (!CheckpointDatabase.Contains(CheckpointID))
	{
		return false;
	}

	return CheckpointDatabase[CheckpointID].bIsUnlocked;
}

int32 UNAR_CheckpointSystem::GetActivationCost(const FString& CheckpointID)
{
	if (CheckpointDatabase.Contains(CheckpointID))
	{
		return CheckpointDatabase[CheckpointID].ActivationCost;
	}

	return 0;
}

// ============================================
// النقل والتلويب
// ============================================
bool UNAR_CheckpointSystem::TeleportToCheckpoint(const FString& CheckpointID, AActor* PlayerActor)
{
	if (!CheckpointDatabase.Contains(CheckpointID) || !PlayerActor)
	{
		return false;
	}

	FCheckpointData& Checkpoint = CheckpointDatabase[CheckpointID];

	if (!Checkpoint.bIsUnlocked)
	{
		UE_LOG(LogTemp, Warning, TEXT("[NAR_Checkpoint] نقطة الحفظ لم تفتح بعد: %s"), *CheckpointID);
		return false;
	}

	// فحص cooldown
	float TimeSinceTeleport = GetWorld()->GetTimeSeconds() - LastTeleportTime;
	if (TimeSinceTeleport < TeleportCooldown)
	{
		UE_LOG(LogTemp, Warning, TEXT("[NAR_Checkpoint] النقل على الكول داون (%.1f/%.1f)"),
			TimeSinceTeleport, TeleportCooldown);
		return false;
	}

	PlayerActor->SetActorLocation(Checkpoint.Location);
	LastTeleportTime = GetWorld()->GetTimeSeconds();
	TotalTeleportUses++;
	Checkpoint.TimesUsed++;

	OnCheckpointUsed.Broadcast(CheckpointID);
	UE_LOG(LogTemp, Warning, TEXT("[NAR_Checkpoint] نقل اللاعب إلى: %s"), *Checkpoint.CheckpointName);

	return true;
}

bool UNAR_CheckpointSystem::TeleportBetweenCheckpoints(const FString& SourceID, const FString& DestinationID, AActor* PlayerActor)
{
	if (!CanTeleportBetween(SourceID, DestinationID) || !PlayerActor)
	{
		return false;
	}

	if (!TeleportToCheckpoint(DestinationID, PlayerActor))
	{
		return false;
	}

	OnTeleport.Broadcast(SourceID, DestinationID);
	UE_LOG(LogTemp, Warning, TEXT("[NAR_Checkpoint] نقل بين نقطتي حفظ: %s -> %s"), *SourceID, *DestinationID);

	return true;
}

bool UNAR_CheckpointSystem::CanTeleportTo(const FString& CheckpointID)
{
	return IsCheckpointUnlocked(CheckpointID);
}

bool UNAR_CheckpointSystem::CanTeleportBetween(const FString& SourceID, const FString& DestID)
{
	if (!CanTeleportTo(SourceID) || !CanTeleportTo(DestID))
	{
		return false;
	}

	return AreCheckpointsConnected(SourceID, DestID);
}

// ============================================
// الشبكة والاتصالات
// ============================================
bool UNAR_CheckpointSystem::ConnectCheckpoints(const FString& CheckpointID1, const FString& CheckpointID2)
{
	if (!CheckpointDatabase.Contains(CheckpointID1) || !CheckpointDatabase.Contains(CheckpointID2))
	{
		return false;
	}

	FCheckpointData& Checkpoint1 = CheckpointDatabase[CheckpointID1];
	FCheckpointData& Checkpoint2 = CheckpointDatabase[CheckpointID2];

	if (Checkpoint1.ConnectedCheckpoints.Num() >= MaxConnectionsPerCheckpoint ||
		Checkpoint2.ConnectedCheckpoints.Num() >= MaxConnectionsPerCheckpoint)
	{
		return false;
	}

	Checkpoint1.ConnectedCheckpoints.AddUnique(CheckpointID2);
	Checkpoint2.ConnectedCheckpoints.AddUnique(CheckpointID1);

	OnNetworkExpanded.Broadcast(CheckpointID1, GetNetworkSize());
	UE_LOG(LogTemp, Log, TEXT("[NAR_Checkpoint] ربط نقطتي حفظ: %s <-> %s"), *CheckpointID1, *CheckpointID2);

	return true;
}

bool UNAR_CheckpointSystem::DisconnectCheckpoints(const FString& CheckpointID1, const FString& CheckpointID2)
{
	if (!CheckpointDatabase.Contains(CheckpointID1) || !CheckpointDatabase.Contains(CheckpointID2))
	{
		return false;
	}

	CheckpointDatabase[CheckpointID1].ConnectedCheckpoints.Remove(CheckpointID2);
	CheckpointDatabase[CheckpointID2].ConnectedCheckpoints.Remove(CheckpointID1);

	UE_LOG(LogTemp, Log, TEXT("[NAR_Checkpoint] فك الربط بين نقطتي حفظ: %s <-> %s"), *CheckpointID1, *CheckpointID2);

	return true;
}

TArray<FCheckpointData> UNAR_CheckpointSystem::GetConnectedCheckpoints(const FString& CheckpointID)
{
	TArray<FCheckpointData> ConnectedList;

	if (!CheckpointDatabase.Contains(CheckpointID))
	{
		return ConnectedList;
	}

	const FCheckpointData& Checkpoint = CheckpointDatabase[CheckpointID];

	for (const FString& ConnectedID : Checkpoint.ConnectedCheckpoints)
	{
		if (CheckpointDatabase.Contains(ConnectedID))
		{
			ConnectedList.Add(CheckpointDatabase[ConnectedID]);
		}
	}

	return ConnectedList;
}

bool UNAR_CheckpointSystem::AreCheckpointsConnected(const FString& CheckpointID1, const FString& CheckpointID2)
{
	if (!CheckpointDatabase.Contains(CheckpointID1))
	{
		return false;
	}

	return CheckpointDatabase[CheckpointID1].ConnectedCheckpoints.Contains(CheckpointID2);
}

int32 UNAR_CheckpointSystem::GetNetworkSize() const
{
	int32 NetworkSize = 0;

	for (const auto& Pair : CheckpointDatabase)
	{
		if (Pair.Value.bIsUnlocked)
		{
			NetworkSize++;
		}
	}

	return NetworkSize;
}

// ============================================
// البحث والقرب
// ============================================
FCheckpointData UNAR_CheckpointSystem::FindNearestCheckpoint(FVector Location)
{
	FCheckpointData NearestCheckpoint;
	float NearestDistance = FLT_MAX;

	for (const auto& Pair : CheckpointDatabase)
	{
		if (Pair.Value.bIsUnlocked)
		{
			float Distance = FVector::Dist(Location, Pair.Value.Location);

			if (Distance < NearestDistance)
			{
				NearestDistance = Distance;
				NearestCheckpoint = Pair.Value;
			}
		}
	}

	return NearestCheckpoint;
}

TArray<FCheckpointData> UNAR_CheckpointSystem::FindCheckpointsInRadius(FVector Location, float Radius)
{
	TArray<FCheckpointData> NearbyCheckpoints;

	for (const auto& Pair : CheckpointDatabase)
	{
		float Distance = FVector::Dist(Location, Pair.Value.Location);

		if (Distance <= Radius && Pair.Value.bIsUnlocked)
		{
			NearbyCheckpoints.Add(Pair.Value);
		}
	}

	return NearbyCheckpoints;
}

bool UNAR_CheckpointSystem::IsCheckpointInRange(const FString& CheckpointID, FVector Location)
{
	if (!CheckpointDatabase.Contains(CheckpointID))
	{
		return false;
	}

	const FCheckpointData& Checkpoint = CheckpointDatabase[CheckpointID];
	float Distance = FVector::Dist(Location, Checkpoint.Location);

	return Distance <= Checkpoint.ActivationRadius;
}

// ============================================
// الإحصائيات
// ============================================
int32 UNAR_CheckpointSystem::GetUnlockedCheckpointCount() const
{
	return UnlockedCount;
}

int32 UNAR_CheckpointSystem::GetActiveCheckpointCount() const
{
	int32 ActiveCount = 0;

	for (const auto& Pair : CheckpointDatabase)
	{
		if (Pair.Value.bIsActive)
		{
			ActiveCount++;
		}
	}

	return ActiveCount;
}

float UNAR_CheckpointSystem::GetNetworkCoverage() const
{
	if (CheckpointDatabase.Num() == 0)
	{
		return 0.0f;
	}

	return (float)GetNetworkSize() / CheckpointDatabase.Num() * 100.0f;
}

// ============================================
// الحفظ والتحميل
// ============================================
void UNAR_CheckpointSystem::SaveCheckpointData()
{
	UE_LOG(LogTemp, Log, TEXT("[NAR_Checkpoint] حفظ بيانات نقاط الحفظ"));
}

void UNAR_CheckpointSystem::LoadCheckpointData()
{
	UE_LOG(LogTemp, Log, TEXT("[NAR_Checkpoint] تحميل بيانات نقاط الحفظ"));
}

void UNAR_CheckpointSystem::ResetAllCheckpoints()
{
	for (auto& Pair : CheckpointDatabase)
	{
		Pair.Value.bIsUnlocked = false;
		Pair.Value.bIsActive = false;
		Pair.Value.TimesUsed = 0;
		Pair.Value.LastUsedTime = 0.0f;
	}

	UnlockedCount = 0;
	TotalTeleportUses = 0;

	UE_LOG(LogTemp, Warning, TEXT("[NAR_Checkpoint] إعادة تعيين جميع نقاط الحفظ"));
}
