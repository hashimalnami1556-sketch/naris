#include "CelestialWolf.h"

#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "NarisRuntimeSubsystem.h"

ACelestialWolf::ACelestialWolf()
{
    PrimaryActorTick.bCanEverTick = true;
    GetCharacterMovement()->MaxWalkSpeed = FollowSpeed;
}

void ACelestialWolf::BeginPlay()
{
    Super::BeginPlay();

    if (!GetWorld())
    {
        return;
    }

    UGameInstance* GameInstance = GetWorld()->GetGameInstance();
    UNarisRuntimeSubsystem* Runtime =
        GameInstance ? GameInstance->GetSubsystem<UNarisRuntimeSubsystem>() : nullptr;

    bBonded = Runtime && Runtime->IsCompanionUnlocked(CompanionId);
    Mode = bBonded ? ENarisWolfMode::Follow : ENarisWolfMode::Guard;
}

void ACelestialWolf::SetMode(ENarisWolfMode NewMode)
{
    if (!bBonded)
    {
        Mode = ENarisWolfMode::Guard;
        return;
    }

    Mode = NewMode;
}

void ACelestialWolf::EchoLink()
{
    if (bBonded)
    {
        Mode = ENarisWolfMode::EchoLink;
    }
}

bool ACelestialWolf::Interact_Implementation(AActor* InstigatorActor)
{
    return BondWithPlayer(InstigatorActor);
}

FText ACelestialWolf::GetInteractionPrompt_Implementation() const
{
    return bBonded
        ? NSLOCTEXT("NARIS", "CelestialWolfBondedPrompt", "Celestial Wolf")
        : NSLOCTEXT("NARIS", "CelestialWolfBondPrompt", "Bond with Celestial Wolf");
}

bool ACelestialWolf::BondWithPlayer(AActor* InstigatorActor)
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

    if (Runtime->IsCompanionUnlocked(CompanionId))
    {
        bBonded = true;
        Mode = ENarisWolfMode::Follow;
        return true;
    }

    if (!Runtime->IsGateUnlocked(RequiredGateId))
    {
        return false;
    }

    if (!Runtime->UnlockCompanion(CompanionId))
    {
        return false;
    }

    if (bAutoSave && !Runtime->SaveState(AutoSaveSlot))
    {
        return false;
    }

    bBonded = true;
    Mode = ENarisWolfMode::Follow;
    OnBonded.Broadcast();
    return true;
}

void ACelestialWolf::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);

    if (!bBonded || Mode != ENarisWolfMode::Follow)
    {
        return;
    }

    APawn* PlayerPawn = UGameplayStatics::GetPlayerPawn(this, 0);
    if (!PlayerPawn)
    {
        return;
    }

    const FVector ToPlayer = PlayerPawn->GetActorLocation() - GetActorLocation();
    const float Distance = ToPlayer.Size();

    if (Distance > FollowDistance)
    {
        AddMovementInput(
            ToPlayer.GetSafeNormal(),
            FMath::Clamp(Distance / 500.f, 0.15f, 1.f)
        );
    }
}
