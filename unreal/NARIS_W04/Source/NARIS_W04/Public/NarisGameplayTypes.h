#pragma once

#include "CoreMinimal.h"
#include "NarisGameplayTypes.generated.h"

UENUM(BlueprintType)
enum class ENarisEssence : uint8
{
    NarisFlame,
    Ash,
    Aether,
    Void,
    Radiant
};

USTRUCT(BlueprintType)
struct FNarisCombatResult
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly)
    float Damage = 0.f;

    UPROPERTY(BlueprintReadOnly)
    float PoiseDamage = 0.f;

    UPROPERTY(BlueprintReadOnly)
    bool bCritical = false;

    UPROPERTY(BlueprintReadOnly)
    bool bParried = false;

    UPROPERTY(BlueprintReadOnly)
    bool bStaggered = false;

    UPROPERTY(BlueprintReadOnly)
    bool bExecutionWindow = false;
};

USTRUCT(BlueprintType)
struct FNarisSaveState
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadWrite)
    FString MapId = TEXT("W04_AshenForest");

    UPROPERTY(BlueprintReadWrite)
    FString CheckpointId = TEXT("WakeArea");

    UPROPERTY(BlueprintReadWrite)
    TArray<FString> UnlockedLore;

    UPROPERTY(BlueprintReadWrite)
    TArray<FString> CompletedQuests;

    UPROPERTY(BlueprintReadWrite)
    TArray<FString> UnlockedWaystones;

    UPROPERTY(BlueprintReadWrite)
    TArray<FString> TriggeredNarratives;

    UPROPERTY(BlueprintReadWrite)
    TArray<FString> UnlockedGates;

    UPROPERTY(BlueprintReadWrite)
    TArray<FString> UnlockedCompanions;

    UPROPERTY(BlueprintReadWrite)
    TArray<FString> DefeatedBosses;

    UPROPERTY(BlueprintReadWrite)
    bool bDemoCompleted = false;

    UPROPERTY(BlueprintReadWrite)
    int32 ResonanceLevel = 0;
};
