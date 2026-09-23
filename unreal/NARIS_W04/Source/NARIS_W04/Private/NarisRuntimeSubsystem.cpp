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
