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
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Runtime")
    FString DefaultAutoSaveSlot = TEXT("NARIS_Auto");

    UFUNCTION(BlueprintCallable, Category="NARIS|Runtime")
    void BeginNewGame();

    UFUNCTION(BlueprintCallable, Category="NARIS|Runtime|FrontEnd")
    void RequestFrontEndBypassOnce();

    UFUNCTION(BlueprintCallable, Category="NARIS|Runtime|FrontEnd")
    bool ConsumeFrontEndBypassOnce();

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

    UFUNCTION(BlueprintCallable, Category="NARIS|Runtime")
    bool SetCheckpointLocation(FVector WorldLocation);

    UFUNCTION(BlueprintCallable, Category="NARIS|Runtime")
    bool UnlockLore(const FString& LoreId);

    UFUNCTION(BlueprintCallable, Category="NARIS|Runtime")
    bool TriggerNarrative(const FString& NarrativeId);

    UFUNCTION(BlueprintPure, Category="NARIS|Runtime")
    bool HasNarrativeTriggered(const FString& NarrativeId) const;

    UFUNCTION(BlueprintCallable, Category="NARIS|Runtime")
    bool UnlockGate(const FString& GateId);

    UFUNCTION(BlueprintPure, Category="NARIS|Runtime")
    bool IsGateUnlocked(const FString& GateId) const;

    UFUNCTION(BlueprintCallable, Category="NARIS|Runtime")
    bool UnlockCompanion(const FString& CompanionId);

    UFUNCTION(BlueprintPure, Category="NARIS|Runtime")
    bool IsCompanionUnlocked(const FString& CompanionId) const;

    UFUNCTION(BlueprintCallable, Category="NARIS|Runtime")
    bool StartQuest(const FString& QuestId, int32 InitialStep);

    UFUNCTION(BlueprintCallable, Category="NARIS|Runtime")
    bool SetQuestStep(const FString& QuestId, int32 Step);

    UFUNCTION(BlueprintPure, Category="NARIS|Runtime")
    bool IsQuestActive(const FString& QuestId) const;

    UFUNCTION(BlueprintPure, Category="NARIS|Runtime")
    int32 GetQuestStep(const FString& QuestId) const;

    UFUNCTION(BlueprintCallable, Category="NARIS|Runtime")
    bool CompleteQuest(const FString& QuestId);

    UFUNCTION(BlueprintPure, Category="NARIS|Runtime")
    bool IsQuestCompleted(const FString& QuestId) const;

    UFUNCTION(BlueprintCallable, Category="NARIS|Runtime")
    bool MarkBossDefeated(const FString& BossId);

    UFUNCTION(BlueprintPure, Category="NARIS|Runtime")
    bool IsBossDefeated(const FString& BossId) const;

    UFUNCTION(BlueprintCallable, Category="NARIS|Runtime")
    bool CompleteDemo();

    UFUNCTION(BlueprintPure, Category="NARIS|Runtime")
    bool IsDemoCompleted() const { return State.bDemoCompleted; }

    UFUNCTION(BlueprintPure, Category="NARIS|Runtime")
    FNarisSaveState GetState() const { return State; }

private:
    FNarisSaveState State;
    bool bFrontEndBypassOnce = false;
};
