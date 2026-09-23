#include "CelestialWolf.h"

#include "BoneBeastBoss.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "NarisPresentationComponent.h"
#include "NarisRuntimeSubsystem.h"

namespace
{
    FName WolfModeCue(ENarisWolfMode Mode)
    {
        switch (Mode)
        {
            case ENarisWolfMode::Follow:
                return TEXT("Wolf.Mode.Follow");
            case ENarisWolfMode::Guard:
                return TEXT("Wolf.Mode.Guard");
            case ENarisWolfMode::Attack:
                return TEXT("Wolf.Mode.Attack");
            case ENarisWolfMode::Track:
                return TEXT("Wolf.Mode.Track");
            case ENarisWolfMode::EchoLink:
                return TEXT("Wolf.Mode.EchoLink");
            default:
                return TEXT("Wolf.Mode.Unknown");
        }
    }
}

ACelestialWolf::ACelestialWolf()
{
    PrimaryActorTick.bCanEverTick = true;

    Presentation =
        CreateDefaultSubobject<UNarisPresentationComponent>(TEXT("Presentation"));

    GetCharacterMovement()->MaxWalkSpeed = FollowSpeed;
}

void ACelestialWolf::BeginPlay()
{
    Super::BeginPlay();

    GuardAnchor = GetActorLocation();
    GetCharacterMovement()->MaxWalkSpeed = FollowSpeed;

    if (!GetWorld())
    {
        return;
    }

    UGameInstance* GameInstance = GetWorld()->GetGameInstance();
    UNarisRuntimeSubsystem* Runtime =
        GameInstance ? GameInstance->GetSubsystem<UNarisRuntimeSubsystem>() : nullptr;

    bBonded = Runtime && Runtime->IsCompanionUnlocked(CompanionId);
    Mode = bBonded ? ENarisWolfMode::Follow : ENarisWolfMode::Guard;

    if (Presentation)
    {
        Presentation->TriggerCue(WolfModeCue(Mode));
    }
}

void ACelestialWolf::SetMode(ENarisWolfMode NewMode)
{
    if (!bBonded)
    {
        NewMode = ENarisWolfMode::Guard;
    }

    if (Mode == NewMode)
    {
        return;
    }

    Mode = NewMode;

    if (Mode == ENarisWolfMode::Guard)
    {
        GuardAnchor = GetActorLocation();
    }

    OnModeChanged.Broadcast(Mode);

    if (Presentation)
    {
        Presentation->TriggerCue(WolfModeCue(Mode));
    }
}

void ACelestialWolf::EchoLink()
{
    SetMode(ENarisWolfMode::EchoLink);
}

void ACelestialWolf::CycleMode()
{
    if (!bBonded)
    {
        return;
    }

    switch (Mode)
    {
        case ENarisWolfMode::Follow:
            SetMode(ENarisWolfMode::Guard);
            break;
        case ENarisWolfMode::Guard:
            SetMode(ENarisWolfMode::Attack);
            break;
        case ENarisWolfMode::Attack:
            SetMode(ENarisWolfMode::Track);
            break;
        case ENarisWolfMode::Track:
            SetMode(ENarisWolfMode::EchoLink);
            break;
        case ENarisWolfMode::EchoLink:
        default:
            SetMode(ENarisWolfMode::Follow);
            break;
    }
}

FText ACelestialWolf::GetModeDisplayName() const
{
    switch (Mode)
    {
        case ENarisWolfMode::Follow:
            return NSLOCTEXT("NARIS", "WolfModeFollow", "Follow");
        case ENarisWolfMode::Guard:
            return NSLOCTEXT("NARIS", "WolfModeGuard", "Guard");
        case ENarisWolfMode::Attack:
            return NSLOCTEXT("NARIS", "WolfModeAttack", "Attack");
        case ENarisWolfMode::Track:
            return NSLOCTEXT("NARIS", "WolfModeTrack", "Track");
        case ENarisWolfMode::EchoLink:
            return NSLOCTEXT("NARIS", "WolfModeEchoLink", "Echo Link");
        default:
            return NSLOCTEXT("NARIS", "WolfModeUnknown", "Unknown");
    }
}

void ACelestialWolf::SetTrackTarget(AActor* NewTarget)
{
    TrackTarget = NewTarget;

    if (TrackTarget && bBonded)
    {
        SetMode(ENarisWolfMode::Track);
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
        SetMode(ENarisWolfMode::Follow);
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
    SetMode(ENarisWolfMode::Follow);
    OnBonded.Broadcast();

    if (Presentation)
    {
        Presentation->TriggerCue(TEXT("Wolf.Bonded"));
    }

    return true;
}

void ACelestialWolf::MoveTowards(
    const FVector& Destination,
    float AcceptanceRadius
)
{
    const FVector ToDestination = Destination - GetActorLocation();
    const float Distance = ToDestination.Size();

    if (Distance > AcceptanceRadius)
    {
        AddMovementInput(
            ToDestination.GetSafeNormal(),
            FMath::Clamp(Distance / 500.f, 0.15f, 1.f)
        );
    }
}

ABoneBeastBoss* ACelestialWolf::FindAttackTarget() const
{
    if (!GetWorld())
    {
        return nullptr;
    }

    ABoneBeastBoss* Best = nullptr;
    float BestDistanceSq = FMath::Square(AttackAcquireRadius);

    for (TActorIterator<ABoneBeastBoss> It(GetWorld()); It; ++It)
    {
        ABoneBeastBoss* Candidate = *It;
        if (!Candidate
            || !Candidate->IsEncounterActive()
            || Candidate->IsEncounterComplete())
        {
            continue;
        }

        const float DistanceSq =
            FVector::DistSquared(GetActorLocation(), Candidate->GetActorLocation());

        if (DistanceSq < BestDistanceSq)
        {
            BestDistanceSq = DistanceSq;
            Best = Candidate;
        }
    }

    return Best;
}

void ACelestialWolf::TickFollow()
{
    APawn* PlayerPawn = UGameplayStatics::GetPlayerPawn(this, 0);
    if (PlayerPawn)
    {
        MoveTowards(PlayerPawn->GetActorLocation(), FollowDistance);
    }
}

void ACelestialWolf::TickGuard()
{
    MoveTowards(GuardAnchor, FollowDistance * 0.5f);
}

void ACelestialWolf::TickAttack()
{
    ABoneBeastBoss* Target = FindAttackTarget();
    if (!Target)
    {
        TickFollow();
        return;
    }

    const float Distance =
        FVector::Distance(GetActorLocation(), Target->GetActorLocation());

    if (Distance > AttackRange)
    {
        MoveTowards(Target->GetActorLocation(), AttackRange * 0.8f);
        return;
    }

    const float Now = GetWorld()->GetTimeSeconds();
    if (Now - LastAttackTime < AttackCooldownSeconds)
    {
        return;
    }

    LastAttackTime = Now;
    RequestAttack(Target);
}

bool ACelestialWolf::RequestAttack(ABoneBeastBoss* Target)
{
    if (!bBonded
        || !IsValid(Target)
        || !Target->IsEncounterActive()
        || Target->IsEncounterComplete())
    {
        return false;
    }

    PendingAttackTarget = Target;

    if (Presentation)
    {
        Presentation->TriggerCue(TEXT("Wolf.Attack"));
    }

    OnAttackRequested();

    if (bImmediateSmokeAttackImpact)
    {
        return CommitAttackImpact();
    }

    return true;
}

bool ACelestialWolf::CommitAttackImpact()
{
    ABoneBeastBoss* Target = PendingAttackTarget;
    if (!IsValid(Target)
        || !Target->IsEncounterActive()
        || Target->IsEncounterComplete())
    {
        CancelAttack();
        return false;
    }

    if (FVector::DistSquared(GetActorLocation(), Target->GetActorLocation())
        > FMath::Square(FMath::Max(AttackRange * 1.5f, 1.f)))
    {
        CancelAttack();
        return false;
    }

    Target->ApplyDamageToEncounter(AttackDamage);

    if (Presentation)
    {
        Presentation->TriggerCueAtLocation(
            TEXT("Wolf.AttackImpact"),
            Target->GetActorLocation()
        );
    }

    CancelAttack();
    return true;
}

void ACelestialWolf::CancelAttack()
{
    PendingAttackTarget = nullptr;
}

void ACelestialWolf::TickTrack()
{
    if (!IsValid(TrackTarget))
    {
        SetMode(ENarisWolfMode::Follow);
        return;
    }

    MoveTowards(TrackTarget->GetActorLocation(), TrackAcceptanceRadius);
}

void ACelestialWolf::TickEchoLink()
{
    APawn* PlayerPawn = UGameplayStatics::GetPlayerPawn(this, 0);
    if (PlayerPawn)
    {
        MoveTowards(PlayerPawn->GetActorLocation(), EchoLinkDistance);
    }

    const float Now = GetWorld()->GetTimeSeconds();
    if (Now - LastEchoPulseTime >= EchoLinkPulseSeconds)
    {
        LastEchoPulseTime = Now;

        if (Presentation)
        {
            Presentation->TriggerCue(TEXT("Wolf.EchoLink.Pulse"));
        }
    }
}

void ACelestialWolf::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);

    if (!bBonded)
    {
        return;
    }

    switch (Mode)
    {
        case ENarisWolfMode::Follow:
            TickFollow();
            break;
        case ENarisWolfMode::Guard:
            TickGuard();
            break;
        case ENarisWolfMode::Attack:
            TickAttack();
            break;
        case ENarisWolfMode::Track:
            TickTrack();
            break;
        case ENarisWolfMode::EchoLink:
            TickEchoLink();
            break;
        default:
            break;
    }
}
