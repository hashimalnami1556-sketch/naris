#include "NarisFieryDemonBoss.h"

#include "Animation/AnimSequence.h"
#include "Components/SkeletalMeshComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/World.h"
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

void ANarisFieryDemonBoss::BeginPlay()
{
    Super::BeginPlay();
    OnBossEvent.AddDynamic(this, &ANarisFieryDemonBoss::OnDemonBossEvent);
    RestoreIdleAnimation();
}

void ANarisFieryDemonBoss::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    if (!GetWorld() || IsEncounterComplete()) { return; }

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
    if (!IsEncounterActive() || IsEncounterComplete())
    {
        CancelAttack();
        return;
    }
    APawn* PlayerPawn = UGameplayStatics::GetPlayerPawn(this, 0);
    if (IsValid(PlayerPawn) && FVector::DistSquared(GetActorLocation(), PlayerPawn->GetActorLocation())
        <= FMath::Square(FMath::Max(AttackRange, 1.f)))
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

void ANarisFieryDemonBoss::OnDemonBossEvent(FName EventName)
{
    if (EventName == TEXT("Death") || EventName == TEXT("EncounterComplete"))
    {
        GetWorldTimerManager().ClearTimer(ImpactTimer);
        GetWorldTimerManager().ClearTimer(IdleTimer);
        bStrikeQueued = false;
        CancelAttack();
        return;
    }
    if (EventName == TEXT("PhaseTransition") && EnrageAnimation)
    {
        if (USkeletalMeshComponent* Skel = GetMesh())
        {
            Skel->PlayAnimation(EnrageAnimation, false);
            GetWorldTimerManager().SetTimer(
                IdleTimer, this, &ANarisFieryDemonBoss::RestoreIdleAnimation,
                1.2f, false);
        }
    }
}
