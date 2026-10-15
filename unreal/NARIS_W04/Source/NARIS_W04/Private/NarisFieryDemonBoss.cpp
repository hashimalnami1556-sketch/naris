#include "NarisFieryDemonBoss.h"

#include "Animation/AnimSequence.h"
#include "Components/SkeletalMeshComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/World.h"
#include "CollisionQueryParams.h"
#include "TimerManager.h"

ANarisFieryDemonBoss::ANarisFieryDemonBoss()
{
    PrimaryActorTick.bCanEverTick = true;
    BossProgressId = TEXT("FieryDemon");
    RequiredCompanionId.Empty();
    FallbackQuestCompletionId = NAME_None;
    FallbackMaxHealth = 6200.f;
    FallbackPhase2HealthPercent = 0.55f;
    FallbackPhase3HealthPercent = 0.f;
    bCompleteDemoOnDefeat = false;
    bAutoSave = true;
    bAutoAttack = true;
    bImmediateSmokeAttackImpact = false;
    AttackIntervalSeconds = 2.6f;
    AttackRange = 540.f;
    Phase1AttackDamage = 28.f;
    Phase2AttackDamage = 46.f;
    Phase3AttackDamage = 46.f;
    AutoPossessAI = EAutoPossessAI::PlacedInWorldOrSpawned;
    if (UCharacterMovementComponent* Movement = GetCharacterMovement())
    {
        Movement->MaxWalkSpeed = 260.f;
        Movement->bOrientRotationToMovement = true;
    }
}

bool ANarisFieryDemonBoss::RequestPhaseAttack()
{
    if (!IsEncounterActive() || IsEncounterComplete() || bEnraging)
    {
        return false;
    }
    // Bone Beast retains ClawSweep/BoneCharge; Fiery Demon uses its own cues.
    if (GetPhase() == ENarisBossPhase::Phase1)
    {
        return RequestAttack(TEXT("GroundSmash"), Phase1AttackDamage);
    }
    if (GetPhase() == ENarisBossPhase::Phase2)
    {
        return RequestAttack(TEXT("EmberNova"), Phase2AttackDamage);
    }
    return false;
}

void ANarisFieryDemonBoss::BeginPlay()
{
    Super::BeginPlay();
    OnBossEvent.AddDynamic(this, &ANarisFieryDemonBoss::OnDemonBossEvent);
    const bool bMeshReady = GetMesh() && GetMesh()->GetSkeletalMeshAsset();
    const bool bClipsReady = IdleAnimation && SmashAnimation && NovaAnimation;
    if (bMeshReady && bClipsReady)
    {
        UE_LOG(LogTemp, Display, TEXT("NARIS_FIERY_DEMON_RUNTIME_READY"));
    }
    else
    {
        UE_LOG(LogTemp, Error,
            TEXT("NARIS_FIERY_DEMON_ASSET_BINDING_FAILED mesh=%d clips=%d"),
            bMeshReady ? 1 : 0, bClipsReady ? 1 : 0);
    }
    RestoreIdleAnimation();
}

void ANarisFieryDemonBoss::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    if (!GetWorld() || IsEncounterComplete() || bEnraging) { return; }

    APawn* PlayerPawn = UGameplayStatics::GetPlayerPawn(this, 0);
    if (!IsValid(PlayerPawn)) { return; }

    const FVector Offset = PlayerPawn->GetActorLocation() - GetActorLocation();
    const float DistanceSq = Offset.SizeSquared();
    if (!IsEncounterActive())
    {
        if (DistanceSq <= FMath::Square(FMath::Max(AggroRadius, 1.f))) { StartEncounter(); }
        return;
    }
    if (bChasePlayer && DistanceSq > FMath::Square(AttackRange * 0.85f)
        && DistanceSq < FMath::Square(AggroRadius * 1.4f))
    {
        AddMovementInput(Offset.GetSafeNormal2D(), 0.65f);
    }
    if (!bStrikeQueued && !GetPendingAttackId().IsNone())
    {
        bStrikeQueued = true;
        if (USkeletalMeshComponent* Skel = GetMesh())
        {
            UAnimSequence* Attack = GetPhase() == ENarisBossPhase::Phase1
                ? SmashAnimation.Get() : NovaAnimation.Get();
            if (Attack) { Skel->PlayAnimation(Attack, false); }
        }
        GetWorldTimerManager().SetTimer(
            ImpactTimer, this, &ANarisFieryDemonBoss::ResolveQueuedImpact,
            FMath::Max(ImpactDelay, 0.1f), false);
    }
}

void ANarisFieryDemonBoss::ResolveQueuedImpact()
{
    bStrikeQueued = false;
    if (!IsEncounterActive() || IsEncounterComplete() || bEnraging)
    {
        CancelAttack();
        return;
    }
    APawn* PlayerPawn = UGameplayStatics::GetPlayerPawn(this, 0);
    const bool bInRange = IsValid(PlayerPawn)
        && FVector::DistSquared(GetActorLocation(), PlayerPawn->GetActorLocation())
            <= FMath::Square(FMath::Max(AttackRange, 1.f));
    bool bClearLineOfSight = false;
    if (bInRange && GetWorld())
    {
        FHitResult Hit;
        FCollisionQueryParams QueryParams;
        QueryParams.AddIgnoredActor(this);
        const FVector Source = GetActorLocation() + FVector(0.f, 0.f, 85.f);
        const FVector Target = PlayerPawn->GetActorLocation() + FVector(0.f, 0.f, 65.f);
        const bool bBlockingHit = GetWorld()->LineTraceSingleByChannel(
            Hit, Source, Target, ECC_Visibility, QueryParams);
        bClearLineOfSight = !bBlockingHit || Hit.GetActor() == PlayerPawn;
    }

    if (bInRange && bClearLineOfSight)
    {
        CommitAttackImpact(PlayerPawn);
    }
    else
    {
        CancelAttack();
    }
    RestoreIdleAnimation();
}

void ANarisFieryDemonBoss::RestoreIdleAnimation()
{
    if (USkeletalMeshComponent* Skel = GetMesh())
    {
        if (IdleAnimation && !IsEncounterComplete())
        {
            Skel->PlayAnimation(IdleAnimation, true);
        }
    }
}

void ANarisFieryDemonBoss::EndEnrage()
{
    bEnraging = false;
    if (IsEncounterActive() && !IsEncounterComplete())
    {
        bAutoAttack = true;
        RestoreIdleAnimation();
    }
}

void ANarisFieryDemonBoss::OnDemonBossEvent(FName EventName)
{
    if (EventName == TEXT("Death") || EventName == TEXT("EncounterComplete")
        || EventName == TEXT("EncounterRestoredComplete"))
    {
        GetWorldTimerManager().ClearTimer(ImpactTimer);
        GetWorldTimerManager().ClearTimer(IdleTimer);
        bEnraging = false;
        bAutoAttack = false;
        bStrikeQueued = false;
        CancelAttack();
        if (EventName == TEXT("Death") && DeathAnimation)
        {
            if (USkeletalMeshComponent* Skel = GetMesh())
            {
                Skel->PlayAnimation(DeathAnimation, false);
            }
        }
        return;
    }
    if (EventName == TEXT("PhaseTransition") && EnrageAnimation)
    {
        GetWorldTimerManager().ClearTimer(ImpactTimer);
        bStrikeQueued = false;
        CancelAttack();
        bEnraging = true;
        bAutoAttack = false;
        if (USkeletalMeshComponent* Skel = GetMesh())
        {
            Skel->PlayAnimation(EnrageAnimation, false);
            GetWorldTimerManager().SetTimer(
                IdleTimer, this, &ANarisFieryDemonBoss::EndEnrage,
                1.2f, false);
        }
        else
        {
            EndEnrage();
        }
    }
}
