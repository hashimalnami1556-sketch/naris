#include "NarisRuntimeSubsystem.h"

#include "Kismet/GameplayStatics.h"
#include "NarisSaveGame.h"

void UNarisRuntimeSubsystem::BeginNewGame()
{
    State = FNarisSaveState();
}

bool UNarisRuntimeSubsystem::SaveState(const FString& SlotName)
{
    if (SlotName.IsEmpty())
    {
        return false;
    }

    UNarisSaveGame* Save = Cast<UNarisSaveGame>(
        UGameplayStatics::CreateSaveGameObject(UNarisSaveGame::StaticClass())
    );
    if (!Save)
    {
        return false;
    }

    Save->State = State;
    return UGameplayStatics::SaveGameToSlot(Save, SlotName, 0);
}

bool UNarisRuntimeSubsystem::LoadState(const FString& SlotName)
{
    if (SlotName.IsEmpty() || !UGameplayStatics::DoesSaveGameExist(SlotName, 0))
    {
        return false;
    }

    UNarisSaveGame* Save =
        Cast<UNarisSaveGame>(UGameplayStatics::LoadGameFromSlot(SlotName, 0));
    if (!Save)
    {
        return false;
    }

    State = Save->State;
    return true;
}

bool UNarisRuntimeSubsystem::ActivateWaystone(
    const FString& WaystoneId,
    const FString& CheckpointId,
    const FString& MapId
)
{
    if (WaystoneId.IsEmpty() || CheckpointId.IsEmpty())
    {
        return false;
    }

    State.CheckpointId = CheckpointId;
    if (!MapId.IsEmpty())
    {
        State.MapId = MapId;
    }

    State.UnlockedWaystones.AddUnique(WaystoneId);
    return true;
}

bool UNarisRuntimeSubsystem::UnlockLore(const FString& LoreId)
{
    if (LoreId.IsEmpty())
    {
        return false;
    }

    State.UnlockedLore.AddUnique(LoreId);
    return true;
}

bool UNarisRuntimeSubsystem::TriggerNarrative(const FString& NarrativeId)
{
    if (NarrativeId.IsEmpty())
    {
        return false;
    }

    State.TriggeredNarratives.AddUnique(NarrativeId);
    return true;
}

bool UNarisRuntimeSubsystem::HasNarrativeTriggered(const FString& NarrativeId) const
{
    return !NarrativeId.IsEmpty() && State.TriggeredNarratives.Contains(NarrativeId);
}

bool UNarisRuntimeSubsystem::UnlockGate(const FString& GateId)
{
    if (GateId.IsEmpty())
    {
        return false;
    }

    State.UnlockedGates.AddUnique(GateId);
    return true;
}

bool UNarisRuntimeSubsystem::IsGateUnlocked(const FString& GateId) const
{
    return !GateId.IsEmpty() && State.UnlockedGates.Contains(GateId);
}

bool UNarisRuntimeSubsystem::UnlockCompanion(const FString& CompanionId)
{
    if (CompanionId.IsEmpty())
    {
        return false;
    }

    State.UnlockedCompanions.AddUnique(CompanionId);
    return true;
}

bool UNarisRuntimeSubsystem::IsCompanionUnlocked(const FString& CompanionId) const
{
    return !CompanionId.IsEmpty() && State.UnlockedCompanions.Contains(CompanionId);
}

bool UNarisRuntimeSubsystem::MarkBossDefeated(const FString& BossId)
{
    if (BossId.IsEmpty())
    {
        return false;
    }

    State.DefeatedBosses.AddUnique(BossId);
    return true;
}

bool UNarisRuntimeSubsystem::IsBossDefeated(const FString& BossId) const
{
    return !BossId.IsEmpty() && State.DefeatedBosses.Contains(BossId);
}

bool UNarisRuntimeSubsystem::CompleteDemo()
{
    State.bDemoCompleted = true;
    return true;
}
