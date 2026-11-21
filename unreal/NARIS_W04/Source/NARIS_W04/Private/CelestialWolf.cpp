#include "CelestialWolf.h"

#include "BoneBeastBoss.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimMontage.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "Engine/NetDriver.h"
#include "EngineUtils.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "NarisPresentationComponent.h"
#include "NarisRuntimeSubsystem.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Net/UnrealNetwork.h"

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

void ACelestialWolf::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);
    DOREPLIFETIME(ACelestialWolf, Mode);
    DOREPLIFETIME(ACelestialWolf, bBonded);
}

void ACelestialWolf::BeginPlay()
{
    Super::BeginPlay();

    GuardAnchor = GetActorLocation();
    GetCharacterMovement()->MaxWalkSpeed = FollowSpeed;

    // Only the authoritative game instance may read campaign/save state.
    // Simulated proxies receive Mode and bBonded via property replication.
    if (!HasAuthority())
    {
        return;
    }

    if (!GetWorld())
    {
        return;
    }

    UGameInstance* GameInstance = GetWorld()->GetGameInstance();
    UNarisRuntimeSubsystem* Runtime =
        GameInstance ? GameInstance->GetSubsystem<UNarisRuntimeSubsystem>() : nullptr;

    bBonded = Runtime && Runtime->IsCompanionUnlocked(CompanionId);
    Mode = bBonded ? ENarisWolfMode::Follow : ENarisWolfMode::Guard;

#if !UE_BUILD_SHIPPING
    // Explicit QA opt-in only: enables a moving, bonded Wolf in a disposable
    // local server session without mutating the player's save/quest state.
    if (FParse::Param(FCommandLine::Get(), TEXT("NarisWolfNetProbeFollow")))
    {
        bBonded = true;
        Mode = ENarisWolfMode::Follow;
        ForceNetUpdate();
    }

    // Only in a disposable DEV test: enter the real Wolf TickAttack path
    // without advancing campaign gates or altering authored assets.
    if (FParse::Param(FCommandLine::Get(), TEXT("NarisWolfNetProbeCombatOnce")))
    {
        bBonded = true;
        Mode = ENarisWolfMode::Attack;
        AttackAcquireRadius = FMath::Max(AttackAcquireRadius, 2500.f);
        bImmediateSmokeAttackImpact = !FParse::Param(FCommandLine::Get(), TEXT("NarisWolfNetProbeMontageOnce"));
        ForceNetUpdate();
    }
#endif

    if (Presentation)
    {
        Presentation->TriggerCue(WolfModeCue(Mode));
    }
}

void ACelestialWolf::SetMode(ENarisWolfMode NewMode)
{
    if (!HasAuthority())
    {
        return;
    }

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
    ForceNetUpdate();

    if (Presentation)
    {
        Presentation->TriggerCue(WolfModeCue(Mode));
    }
}

void ACelestialWolf::OnRep_Mode()
{
    OnModeChanged.Broadcast(Mode);
    if (Presentation)
    {
        Presentation->TriggerCue(WolfModeCue(Mode));
    }
#if !UE_BUILD_SHIPPING
    if (FParse::Param(FCommandLine::Get(), TEXT("NarisWolfNetProbe")))
    {
        UE_LOG(LogTemp, Display, TEXT("NARIS_WOLF_NET_PROBE event=OnRep_Mode mode=%d"), static_cast<int32>(Mode));
    }
#endif
}

void ACelestialWolf::OnRep_Bonded()
{
    if (bBonded)
    {
        OnBonded.Broadcast();
        if (Presentation)
        {
            Presentation->TriggerCue(TEXT("Wolf.Bonded"));
        }
    }
#if !UE_BUILD_SHIPPING
    if (FParse::Param(FCommandLine::Get(), TEXT("NarisWolfNetProbe")))
    {
        UE_LOG(LogTemp, Display, TEXT("NARIS_WOLF_NET_PROBE event=OnRep_Bonded bonded=%d"), bBonded ? 1 : 0);
    }
#endif
}

void ACelestialWolf::EchoLink()
{
    SetMode(ENarisWolfMode::EchoLink);
}

void ACelestialWolf::CycleMode()
{
    if (!HasAuthority())
    {
        return;
    }

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
    if (!HasAuthority())
    {
        return;
    }

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
    if (!HasAuthority())
    {
        return false;
    }

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

    if (!Runtime->SetQuestStep(QuestId, QuestStep))
    {
        return false;
    }

    if (bAutoSave && !Runtime->SaveState(AutoSaveSlot))
    {
        return false;
    }

    bBonded = true;
    SetMode(ENarisWolfMode::Follow);
    ForceNetUpdate();
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
#if !UE_BUILD_SHIPPING
    // Deterministic, non-shipping QA probe only. It moves the real Character
    // via AddMovementInput so a listen server and two clients can verify
    // continuing *authoritative* replication after their initial join.
    // No source assets, quest state, or save games are changed.
    if (GetWorld() && FParse::Param(FCommandLine::Get(), TEXT("NarisWolfNetProbeMarch")))
    {
        const float Seconds = GetWorld()->GetTimeSeconds();
        const FVector ProbeDestination = GuardAnchor
            + FVector(600.f * FMath::Sin(Seconds * 0.45f), 0.f, 0.f);
        MoveTowards(ProbeDestination, 12.f);
        return;
    }
#endif

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
#if !UE_BUILD_SHIPPING
    if (GetWorld() && FParse::Param(FCommandLine::Get(), TEXT("NarisWolfNetProbeCombatOnce")))
    {
        // Deterministic QA only: do not run the real server attack decision
        // before both packaged remote clients have joined and observed HP=100.
        // No gameplay attack delay or network dependency in normal builds.
        const UNetDriver* Driver = GetWorld()->GetNetDriver();
        if (!Driver || Driver->ClientConnections.Num() < 2
            || GetWorld()->GetTimeSeconds() < 12.f)
        {
            return;
        }
    }
#endif

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
    if (!HasAuthority() || !bBonded
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

#if !UE_BUILD_SHIPPING
    if (FParse::Param(FCommandLine::Get(), TEXT("NarisWolfNetProbeMontageOnce")))
    {
        // Read the already-authored, matching-skeleton Bite montage only in
        // isolated QA. NEVER create/overwrite .uasset or synthesize a hit.
        static const TCHAR* BitePath =
            TEXT("/Game/NARIS/W04/Characters/WolfPresentationV9/Combat/AM_Wolf_Bite.AM_Wolf_Bite");
        UAnimMontage* Bite = LoadObject<UAnimMontage>(nullptr, BitePath);
        UAnimInstance* Instance = GetMesh() ? GetMesh()->GetAnimInstance() : nullptr;
        const float Duration = (Bite && Instance) ? Instance->Montage_Play(Bite) : 0.f;
        UE_LOG(LogTemp, Display,
            TEXT("NARIS_WOLF_COMBAT_PROBE event=ServerMontagePlay authority=%d valid_asset=%d valid_anim_instance=%d duration=%.3f"),
            HasAuthority() ? 1 : 0, IsValid(Bite) ? 1 : 0,
            IsValid(Instance) ? 1 : 0, Duration);
        if (Duration <= 0.f)
        {
            CancelAttack();
            SetMode(ENarisWolfMode::Guard);
            return false;
        }
        // The existing NarisWolfAttackImpactNotify on AM_Wolf_Bite is now the
        // ONLY path to CommitAttackImpact. No instant smoke fallback.
        return true;
    }
#endif

    if (bImmediateSmokeAttackImpact)
    {
        return CommitAttackImpact();
    }

    return true;
}

bool ACelestialWolf::CommitAttackImpact()
{
    // Montage notifies may execute on simulated clients. Never let them
    // apply damage locally: only the server owns the authoritative hit.
    if (!HasAuthority())
    {
        return false;
    }

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

#if !UE_BUILD_SHIPPING
    const float BossHPBeforeProbe = Target->GetCurrentHealth();
#endif
    Target->ApplyDamageToEncounter(AttackDamage);

#if !UE_BUILD_SHIPPING
    if (FParse::Param(FCommandLine::Get(), TEXT("NarisWolfNetProbeCombatOnce")))
    {
        UE_LOG(LogTemp, Display,
            TEXT("NARIS_WOLF_COMBAT_PROBE event=ServerWolfAttackImpact authority=%d before=%.2f after=%.2f damage=%.2f"),
            HasAuthority() ? 1 : 0, BossHPBeforeProbe, Target->GetCurrentHealth(), AttackDamage);
        // Stop at a single real RequestAttack->CommitAttackImpact call:
        // no boss death, no quest completion and no autosave.
        SetMode(ENarisWolfMode::Guard);
    }
#endif

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

#if !UE_BUILD_SHIPPING
    if (GetWorld() && FParse::Param(FCommandLine::Get(), TEXT("NarisWolfNetProbe"))
        && GetWorld()->GetTimeSeconds() >= NextNetProbeLogTime)
    {
        NextNetProbeLogTime = GetWorld()->GetTimeSeconds() + 1.f;
        const FVector P = GetActorLocation();
        UE_LOG(LogTemp, Display,
            TEXT("NARIS_WOLF_NET_PROBE event=Tick authority=%d bonded=%d mode=%d x=%.2f y=%.2f z=%.2f speed2d=%.2f"),
            HasAuthority() ? 1 : 0, bBonded ? 1 : 0, static_cast<int32>(Mode),
            P.X, P.Y, P.Z, GetVelocity().Size2D());
    }
#endif

    // CharacterMovement replicates the authoritative wolf movement; clients
    // animate simulated proxies and must not run AI/combat/save-state ticks.
    if (!HasAuthority() || !bBonded)
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
