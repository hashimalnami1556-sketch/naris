#include "NarisWaystone.h"

#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "NarisRuntimeSubsystem.h"

ANarisWaystone::ANarisWaystone()
{
    PrimaryActorTick.bCanEverTick = false;

    SceneRoot = CreateDefaultSubobject<USceneComponent>(TEXT("SceneRoot"));
    SetRootComponent(SceneRoot);

    Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
    Mesh->SetupAttachment(SceneRoot);
    Mesh->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
}

bool ANarisWaystone::Interact_Implementation(AActor* InstigatorActor)
{
    return ActivateWaystone(InstigatorActor);
}

FText ANarisWaystone::GetInteractionPrompt_Implementation() const
{
    return NSLOCTEXT("NARIS", "WaystoneInteractPrompt", "Attune Waystone");
}

bool ANarisWaystone::ActivateWaystone(AActor* InstigatorActor)
{
    if (!GetWorld())
    {
        return false;
    }

    UGameInstance* GameInstance = GetWorld()->GetGameInstance();
    UNarisRuntimeSubsystem* Runtime =
        GameInstance ? GameInstance->GetSubsystem<UNarisRuntimeSubsystem>() : nullptr;

    if (!Runtime)
    {
        return false;
    }

    if (!Runtime->ActivateWaystone(WaystoneId, CheckpointId, MapId))
    {
        return false;
    }

    if (!Runtime->SetCheckpointLocation(GetActorLocation()))
    {
        return false;
    }

    if (bAutoSave && !Runtime->SaveState(AutoSaveSlot))
    {
        return false;
    }

    OnActivated.Broadcast();
    return true;
}
