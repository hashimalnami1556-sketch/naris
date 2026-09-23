#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "NarisGameplayTypes.h"
#include "NarisRuntimeSubsystem.generated.h"

UCLASS()
class NARIS_W04_API UNarisRuntimeSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category="NARIS|Runtime")
    void BeginNewGame();

    UFUNCTION(BlueprintCallable, Category="NARIS|Runtime")
    bool SaveState(const FString& SlotName);

    UFUNCTION(BlueprintCallable, Category="NARIS|Runtime")
    bool LoadState(const FString& SlotName);

    UFUNCTION(BlueprintCallable, Category="NARIS|Runtime")
    bool ActivateWaystone(
        const FString& WaystoneId,
        const FString& CheckpointId,
        const FString& MapId
    );

    UFUNCTION(BlueprintPure, Category="NARIS|Runtime")
    FNarisSaveState GetState() const { return State; }

private:
    FNarisSaveState State;
};
