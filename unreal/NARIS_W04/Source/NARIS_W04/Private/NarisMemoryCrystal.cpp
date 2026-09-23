#include "NarisMemoryCrystal.h"

#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "NarisRuntimeSubsystem.h"

ANarisMemoryCrystal::ANarisMemoryCrystal()
{
    PrimaryActorTick.bCanEverTick = false;

    SceneRoot = CreateDefaultSubobject<USceneComponent>(TEXT("SceneRoot"));
    SetRootComponent(SceneRoot);

    Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
    Mesh->SetupAttachment(SceneRoot);
    Mesh->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
}

bool ANarisMemoryCrystal::Interact_Implementation(AActor* InstigatorActor)
{
    return ActivateMemory(InstigatorActor);
}

FText ANarisMemoryCrystal::GetInteractionPrompt_Implementation() const
{
    return NSLOCTEXT("NARIS", "MemoryCrystalInteractPrompt", "Read Memory");
}

bool ANarisMemoryCrystal::ActivateMemory(AActor* InstigatorActor)
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

    if (bOneShot && Runtime->HasNarrativeTriggered(NarrativeId))
    {
        return false;
    }

    if (!Runtime->UnlockLore(LoreId))
    {
        return false;
    }

    if (!Runtime->TriggerNarrative(NarrativeId))
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
