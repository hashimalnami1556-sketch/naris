// NAR_CheckpointSystem.h — نظام نقاط الحفظ المتقدم
// محرك اللعبة — Naris Realms

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NAR_CheckpointSystem.generated.h"

// ============================================
// أنواع نقاط الحفظ
// ============================================
UENUM(BlueprintType)
enum class ECheckpointType : uint8
{
	Waystone			UMETA(DisplayName = "حجر الطريق"),
	Shrine				UMETA(DisplayName = "معبد"),
	CampFire			UMETA(DisplayName = "نار المخيم"),
	Portal				UMETA(DisplayName = "بوابة"),
	Teleporter			UMETA(DisplayName = "جهاز نقل")
};

// ============================================
// بيانات نقطة الحفظ
// ============================================
USTRUCT(BlueprintType)
struct FCheckpointData
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadWrite, Category = "Checkpoint")
	FString CheckpointID = FString();

	UPROPERTY(BlueprintReadWrite, Category = "Checkpoint")
	FString CheckpointName = TEXT("");

	UPROPERTY(BlueprintReadWrite, Category = "Checkpoint")
	FString Region = TEXT("");

	UPROPERTY(BlueprintReadWrite, Category = "Checkpoint")
	ECheckpointType CheckpointType = ECheckpointType::Waystone;

	UPROPERTY(BlueprintReadWrite, Category = "Checkpoint")
	FVector Location = FVector::ZeroVector;

	UPROPERTY(BlueprintReadWrite, Category = "Checkpoint")
	bool bIsUnlocked = false;

	UPROPERTY(BlueprintReadWrite, Category = "Checkpoint")
	bool bIsActive = false;

	UPROPERTY(BlueprintReadWrite, Category = "Checkpoint")
	int32 ActivationCost = 0;

	UPROPERTY(BlueprintReadWrite, Category = "Checkpoint")
	float ActivationRadius = 500.0f;

	UPROPERTY(BlueprintReadWrite, Category = "Checkpoint")
	int32 TimesUsed = 0;

	UPROPERTY(BlueprintReadWrite, Category = "Checkpoint")
	float LastUsedTime = 0.0f;

	UPROPERTY(BlueprintReadWrite, Category = "Checkpoint")
	AActor* CheckpointActor = nullptr;

	UPROPERTY(BlueprintReadWrite, Category = "Checkpoint")
	TArray<FString> ConnectedCheckpoints;
};

// ============================================
// نظام نقاط الحفظ
// ============================================
/**
 * UNAR_CheckpointSystem — نظام نقاط الحفظ المتقدم
 * يدير: نقاط الحفظ + الشبكة + الاتصالات
 */
UCLASS(ClassGroup=(NAR), meta=(BlueprintSpawnableComponent))
class NARISREALMS_API UNAR_CheckpointSystem : public UActorComponent
{
	GENERATED_BODY()

public:
	UNAR_CheckpointSystem();

	virtual void BeginPlay() override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

	// ============================================
	// إدارة نقاط الحفظ
	// ============================================
	UFUNCTION(BlueprintCallable, Category = "NAR|Checkpoint")
	bool RegisterCheckpoint(const FCheckpointData& CheckpointData);

	UFUNCTION(BlueprintCallable, Category = "NAR|Checkpoint")
	bool UnregisterCheckpoint(const FString& CheckpointID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Checkpoint")
	FCheckpointData GetCheckpoint(const FString& CheckpointID);

	UFUNCTION(BlueprintPure, Category = "NAR|Checkpoint")
	TArray<FCheckpointData> GetAllCheckpoints() const;

	UFUNCTION(BlueprintPure, Category = "NAR|Checkpoint")
	TArray<FCheckpointData> GetUnlockedCheckpoints() const;

	UFUNCTION(BlueprintPure, Category = "NAR|Checkpoint")
	TArray<FCheckpointData> GetCheckpointsByRegion(const FString& RegionName);

	UFUNCTION(BlueprintPure, Category = "NAR|Checkpoint")
	TArray<FCheckpointData> GetCheckpointsByType(ECheckpointType Type);

	UFUNCTION(BlueprintPure, Category = "NAR|Checkpoint")
	int32 GetCheckpointCount() const { return CheckpointDatabase.Num(); }

	// ============================================
	// تنشيط وفتح
	// ============================================
	UFUNCTION(BlueprintCallable, Category = "NAR|Checkpoint|Activation")
	bool ActivateCheckpoint(const FString& CheckpointID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Checkpoint|Activation")
	bool DeactivateCheckpoint(const FString& CheckpointID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Checkpoint|Activation")
	bool UnlockCheckpoint(const FString& CheckpointID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Checkpoint|Activation")
	bool IsCheckpointUnlocked(const FString& CheckpointID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Checkpoint|Activation")
	bool CanActivateCheckpoint(const FString& CheckpointID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Checkpoint|Activation")
	int32 GetActivationCost(const FString& CheckpointID);

	// ============================================
	// النقل والتلويب
	// ============================================
	UFUNCTION(BlueprintCallable, Category = "NAR|Checkpoint|Teleport")
	bool TeleportToCheckpoint(const FString& CheckpointID, AActor* PlayerActor);

	UFUNCTION(BlueprintCallable, Category = "NAR|Checkpoint|Teleport")
	bool TeleportBetweenCheckpoints(const FString& SourceID, const FString& DestinationID, AActor* PlayerActor);

	UFUNCTION(BlueprintCallable, Category = "NAR|Checkpoint|Teleport")
	bool CanTeleportTo(const FString& CheckpointID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Checkpoint|Teleport")
	bool CanTeleportBetween(const FString& SourceID, const FString& DestID);

	UFUNCTION(BlueprintPure, Category = "NAR|Checkpoint|Teleport")
	float GetTeleportCooldown() const { return TeleportCooldown; }

	// ============================================
	// الشبكة والاتصالات
	// ============================================
	UFUNCTION(BlueprintCallable, Category = "NAR|Checkpoint|Network")
	bool ConnectCheckpoints(const FString& CheckpointID1, const FString& CheckpointID2);

	UFUNCTION(BlueprintCallable, Category = "NAR|Checkpoint|Network")
	bool DisconnectCheckpoints(const FString& CheckpointID1, const FString& CheckpointID2);

	UFUNCTION(BlueprintCallable, Category = "NAR|Checkpoint|Network")
	TArray<FCheckpointData> GetConnectedCheckpoints(const FString& CheckpointID);

	UFUNCTION(BlueprintCallable, Category = "NAR|Checkpoint|Network")
	bool AreCheckpointsConnected(const FString& CheckpointID1, const FString& CheckpointID2);

	UFUNCTION(BlueprintPure, Category = "NAR|Checkpoint|Network")
	int32 GetNetworkSize() const;

	// ============================================
	// البحث والقرب
	// ============================================
	UFUNCTION(BlueprintCallable, Category = "NAR|Checkpoint|Search")
	FCheckpointData FindNearestCheckpoint(FVector Location);

	UFUNCTION(BlueprintCallable, Category = "NAR|Checkpoint|Search")
	TArray<FCheckpointData> FindCheckpointsInRadius(FVector Location, float Radius);

	UFUNCTION(BlueprintCallable, Category = "NAR|Checkpoint|Search")
	bool IsCheckpointInRange(const FString& CheckpointID, FVector Location);

	// ============================================
	// الإحصائيات
	// ============================================
	UFUNCTION(BlueprintPure, Category = "NAR|Checkpoint|Stats")
	int32 GetTotalCheckpoints() const { return CheckpointDatabase.Num(); }

	UFUNCTION(BlueprintPure, Category = "NAR|Checkpoint|Stats")
	int32 GetUnlockedCheckpointCount() const;

	UFUNCTION(BlueprintPure, Category = "NAR|Checkpoint|Stats")
	int32 GetActiveCheckpointCount() const;

	UFUNCTION(BlueprintPure, Category = "NAR|Checkpoint|Stats")
	float GetNetworkCoverage() const;

	UFUNCTION(BlueprintPure, Category = "NAR|Checkpoint|Stats")
	int32 GetTotalTeleportUses() const { return TotalTeleportUses; }

	// ============================================
	// الحفظ والتحميل
	// ============================================
	UFUNCTION(BlueprintCallable, Category = "NAR|Checkpoint|Save")
	void SaveCheckpointData();

	UFUNCTION(BlueprintCallable, Category = "NAR|Checkpoint|Save")
	void LoadCheckpointData();

	UFUNCTION(BlueprintCallable, Category = "NAR|Checkpoint|Save")
	void ResetAllCheckpoints();

	// ============================================
	// الأحداث
	// ============================================
	DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnCheckpointUnlocked, FCheckpointData, Checkpoint);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Checkpoint|Events")
	FOnCheckpointUnlocked OnCheckpointUnlocked;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnCheckpointActivated, FString, CheckpointID, bool, bActivated);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Checkpoint|Events")
	FOnCheckpointActivated OnCheckpointActivated;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnTeleport, FString, SourceID, FString, DestinationID);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Checkpoint|Events")
	FOnTeleport OnTeleport;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnCheckpointUsed, FString, CheckpointID);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Checkpoint|Events")
	FOnCheckpointUsed OnCheckpointUsed;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnNetworkExpanded, FString, CheckpointID, int32, NetworkSize);
	UPROPERTY(BlueprintAssignable, Category = "NAR|Checkpoint|Events")
	FOnNetworkExpanded OnNetworkExpanded;

protected:
	// ============================================
	// بيانات نقاط الحفظ
	// ============================================
	UPROPERTY(BlueprintReadOnly, Category = "NAR|Checkpoint|Data")
	TMap<FString, FCheckpointData> CheckpointDatabase;

	// ============================================
	// الإحصائيات
	// ============================================
	UPROPERTY(BlueprintReadOnly, Category = "NAR|Checkpoint|Data")
	int32 TotalTeleportUses = 0;

	UPROPERTY(BlueprintReadOnly, Category = "NAR|Checkpoint|Data")
	int32 UnlockedCount = 0;

	// ============================================
	// الإعدادات
	// ============================================
	UPROPERTY(EditDefaultsOnly, Category = "NAR|Checkpoint|Settings")
	float TeleportCooldown = 5.0f;

	UPROPERTY(EditDefaultsOnly, Category = "NAR|Checkpoint|Settings")
	float DefaultActivationRadius = 500.0f;

	UPROPERTY(EditDefaultsOnly, Category = "NAR|Checkpoint|Settings")
	bool bRequireLineOfSight = false;

	UPROPERTY(EditDefaultsOnly, Category = "NAR|Checkpoint|Settings")
	int32 MaxConnectionsPerCheckpoint = 10;

private:
	float LastTeleportTime = 0.0f;
};
