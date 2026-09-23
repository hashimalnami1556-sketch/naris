#include "NarisAshGate.h"

#include "Components/BoxComponent.h"
#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "NarisRuntimeSubsystem.h"

ANarisAshGate::ANarisAshGate()
{
    PrimaryActorTick.bCanEverTick = false;

    SceneRoot = CreateDefaultSubobject<USceneComponent>(TEXT("SceneRoot"));
    SetRootComponent(SceneRoot);

    GateMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("GateMesh"));
    GateMesh->SetupAttachment(SceneRoot);
    GateMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);

    Blocker = CreateDefaultSubobject<UBoxComponent>(TEXT("Blocker"));
    Blocker->SetupAttachment(SceneRoot);
    Blocker->SetBoxExtent(FVector(120.f, 40.f, 220.f));
    Blocker->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
    Blocker->SetCollisionResponseToAllChannels(ECR_Block);
}

void ANarisAshGate::BeginPlay()
{
    Super::BeginPlay();

    if (!GetWorld())
    {
        return;
    }

    UGameInstance* GameInstance = GetWorld()->GetGameInstance();
    UNarisRuntimeSubsystem* Runtime =
        GameInstance ? GameInstance->GetSubsystem<UNarisRuntimeSubsystem>() : nullptr;

    if (Runtime && Runtime->IsGateUnlocked(GateId))
    {
        ApplyUnlockedState();
    }
}

bool ANarisAshGate::Interact_Implementation(AActor* InstigatorActor)
{
    return TryUnlockGate(InstigatorActor);
}

FText ANarisAshGate::GetInteractionPrompt_Implementation() const
{
    return NSLOCTEXT("NARIS", "AshGateInteractPrompt", "Open Ash Gate");
}

bool ANarisAshGate::TryUnlockGate(AActor* InstigatorActor)
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

    if (Runtime->IsGateUnlocked(GateId))
    {
        ApplyUnlockedState();
        return true;
    }

    if (!Runtime->HasNarrativeTriggered(RequiredNarrativeId))
    {
        OnGateLocked.Broadcast();
        return false;
    }

    if (!Runtime->UnlockGate(GateId))
    {
        return false;
    }

    if (bAutoSave && !Runtime->SaveState(AutoSaveSlot))
    {
        return false;
    }

    ApplyUnlockedState();
    OnGateUnlocked.Broadcast();
    return true;
}

void ANarisAshGate::ApplyUnlockedState()
{
    if (Blocker)
    {
        Blocker->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    }
}
