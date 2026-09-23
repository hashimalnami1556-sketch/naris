#include "BoneBeastBoss.h"

#include "BoneBeastCombatComponent.h"
#include "BoneBeastDataAsset.h"
#include "BoneBeastPhaseComponent.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "GameFramework/DamageType.h"
#include "Kismet/GameplayStatics.h"
#include "NarisPresentationComponent.h"
#include "NarisRuntimeSubsystem.h"

ABoneBeastBoss::ABoneBeastBoss()
{
    PrimaryActorTick.bCanEverTick = true;

    CombatPresentation =
        CreateDefaultSubobject<UBoneBeastCombatComponent>(TEXT("CombatPresentation"));
    PhasePresentation =
        CreateDefaultSubobject<UBoneBeastPhaseComponent>(TEXT("PhasePresentation"));
    Presentation =
        CreateDefaultSubobject<UNarisPresentationComponent>(TEXT("Presentation"));
}

void ABoneBeastBoss::BeginPlay()
{
    Super::BeginPlay();

    if (!GetWorld())
    {
        return;
    }

    UGameInstance* GameInstance = GetWorld()->GetGameInstance();
    UNarisRuntimeSubsystem* Runtime =
        GameInstance ? GameInstance->GetSubsystem<UNarisRuntimeSubsystem>() : nullptr;

    if (Runtime && Runtime->IsBossDefeated(BossProgressId))
    {
        CurrentHealth = 0.f;
        CurrentPhase = ENarisBossPhase::Dead;
        bEncounterActive = false;
        bEncounterComplete = true;

        if (PhasePresentation)
        {
            PhasePresentation->SetAuthoritativePhase(CurrentPhase);
        }

        EmitBossEvent(TEXT("EncounterRestoredComplete"));

        if (Runtime->IsDemoCompleted())
        {
            EmitBossEvent(TEXT("DemoEnd"));
        }
    }
}

void ABoneBeastBoss::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);

    if (!bAutoAttack
        || !bEncounterActive
        || bEncounterComplete
        || !PendingAttackId.IsNone()
        || !GetWorld())
    {
        return;
    }

    APawn* PlayerPawn = UGameplayStatics::GetPlayerPawn(this, 0);
    if (!IsValid(PlayerPawn))
    {
        return;
    }

    const float DistanceSq = FVector::DistSquared(
        GetActorLocation(),
        PlayerPawn->GetActorLocation()
    );
    if (DistanceSq > FMath::Square(FMath::Max(AttackRange, 1.f)))
    {
        return;
    }

    const float Now = GetWorld()->GetTimeSeconds();
    if (Now - LastAttackRequestTime < FMath::Max(AttackIntervalSeconds, 0.1f))
    {
        return;
    }

    if (!RequestPhaseAttack())
    {
        return;
    }

    LastAttackRequestTime = Now;

    if (bImmediateSmokeAttackImpact)
    {
        CommitAttackImpact(PlayerPawn);
    }
}

float ABoneBeastBoss::GetConfiguredMaxHealth() const
{
    if (BossData && BossData->MaxHealth > 0.f)
    {
        return BossData->MaxHealth;
    }

    return FMath::Max(FallbackMaxHealth, 1.f);
}

bool ABoneBeastBoss::Interact_Implementation(AActor* InstigatorActor)
{
    return TryStartEncounter(InstigatorActor);
}

FText ABoneBeastBoss::GetInteractionPrompt_Implementation() const
{
    return bEncounterComplete
        ? NSLOCTEXT("NARIS", "BoneBeastDefeatedPrompt", "Bone Beast Defeated")
        : NSLOCTEXT("NARIS", "BoneBeastStartPrompt", "Enter Bone Beast Arena");
}

bool ABoneBeastBoss::TryStartEncounter(AActor* InstigatorActor)
{
    if (bEncounterComplete)
    {
        return false;
    }

    StartEncounter();
    return bEncounterActive;
}

void ABoneBeastBoss::StartEncounter()
{
    const float MaxHealth = GetConfiguredMaxHealth();
    if (MaxHealth <= 0.f || bEncounterActive || bEncounterComplete)
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

    if (!Runtime || !Runtime->IsCompanionUnlocked(RequiredCompanionId))
    {
        EmitBossEvent(TEXT("EncounterLocked"));
        return;
    }

    if (Runtime->IsBossDefeated(BossProgressId))
    {
        CurrentHealth = 0.f;
        CurrentPhase = ENarisBossPhase::Dead;
        bEncounterComplete = true;
        EmitBossEvent(TEXT("EncounterRestoredComplete"));
        return;
    }

    CurrentHealth = MaxHealth;
    CurrentPhase = ENarisBossPhase::Phase1;
    bEncounterActive = true;
    bEncounterComplete = false;
    PendingAttackId = NAME_None;
    PendingAttackDamage = 0.f;
    LastAttackRequestTime = -1000.f;

    if (PhasePresentation)
    {
        PhasePresentation->SetAuthoritativePhase(CurrentPhase);
    }

    EmitBossEvent(TEXT("EncounterStarted"));
}

void ABoneBeastBoss::ResetEncounter()
{
    if (bEncounterComplete)
    {
        return;
    }

    CurrentHealth = GetConfiguredMaxHealth();
    CurrentPhase = ENarisBossPhase::Phase1;
    bEncounterActive = false;
    CancelAttack();

    if (PhasePresentation)
    {
        PhasePresentation->SetAuthoritativePhase(CurrentPhase);
    }

    EmitBossEvent(TEXT("EncounterReset"));
}

void ABoneBeastBoss::ApplyDamageToEncounter(float Damage)
{
    if (!bEncounterActive
        || bEncounterComplete
        || CurrentPhase == ENarisBossPhase::Dead
        || Damage <= 0.f)
    {
        return;
    }

    CurrentHealth = FMath::Max(0.f, CurrentHealth - Damage);
    EmitBossEvent(TEXT("DamageTaken"));

    if (CurrentHealth <= 0.f)
    {
        CurrentHealth = 0.f;
        CurrentPhase = ENarisBossPhase::Dead;
        bEncounterActive = false;
        CancelAttack();

        if (PhasePresentation)
        {
            PhasePresentation->SetAuthoritativePhase(CurrentPhase);
        }

        EmitBossEvent(TEXT("Death"));
        CompleteEncounter();
        return;
    }

    EvaluatePhase();
}

void ABoneBeastBoss::CompleteEncounter()
{
    if (bEncounterComplete
        || CurrentPhase != ENarisBossPhase::Dead
        || !GetWorld())
    {
        return;
    }

    UGameInstance* GameInstance = GetWorld()->GetGameInstance();
    UNarisRuntimeSubsystem* Runtime =
        GameInstance ? GameInstance->GetSubsystem<UNarisRuntimeSubsystem>() : nullptr;

    if (!Runtime || !Runtime->MarkBossDefeated(BossProgressId))
    {
        EmitBossEvent(TEXT("CompletionStateFailed"));
        return;
    }

    FName QuestCompletionId = FallbackQuestCompletionId;
    if (BossData && !BossData->QuestCompletionId.IsNone())
    {
        QuestCompletionId = BossData->QuestCompletionId;
    }

    if (!QuestCompletionId.IsNone())
    {
        Runtime->SetQuestStep(QuestCompletionId.ToString(), 4);
        Runtime->CompleteQuest(QuestCompletionId.ToString());
    }

    if (bCompleteDemoOnDefeat)
    {
        Runtime->CompleteDemo();
    }

    bEncounterComplete = true;
    EmitBossEvent(TEXT("EncounterComplete"));

    if (bCompleteDemoOnDefeat)
    {
        EmitBossEvent(TEXT("DemoEnd"));
    }

    if (bAutoSave && !Runtime->SaveState(AutoSaveSlot))
    {
        EmitBossEvent(TEXT("AutoSaveFailed"));
    }
}

bool ABoneBeastBoss::RequestPhaseAttack()
{
    switch (CurrentPhase)
    {
        case ENarisBossPhase::Phase1:
            return RequestAttack(TEXT("ClawSweep"), Phase1AttackDamage);
        case ENarisBossPhase::Phase2:
            return RequestAttack(TEXT("BoneCharge"), Phase2AttackDamage);
        case ENarisBossPhase::Phase3:
            return RequestAttack(TEXT("AshRupture"), Phase3AttackDamage);
        default:
            return false;
    }
}

bool ABoneBeastBoss::RequestAttack(FName AttackId, float Damage)
{
    if (!bEncounterActive
        || bEncounterComplete
        || CurrentPhase == ENarisBossPhase::Dead
        || AttackId.IsNone()
        || Damage <= 0.f)
    {
        return false;
    }

    PendingAttackId = AttackId;
    PendingAttackDamage = Damage;

    if (CombatPresentation)
    {
        CombatPresentation->StartAttack(AttackId);
    }

    if (Presentation)
    {
        Presentation->TriggerCue(
            FName(*FString::Printf(
                TEXT("Boss.Attack.%s"),
                *AttackId.ToString()
            ))
        );
    }

    return true;
}

bool ABoneBeastBoss::CommitAttackImpact(AActor* TargetActor)
{
    if (!bEncounterActive
        || bEncounterComplete
        || PendingAttackId.IsNone()
        || PendingAttackDamage <= 0.f
        || !IsValid(TargetActor))
    {
        return false;
    }

    const float AppliedDamage = UGameplayStatics::ApplyDamage(
        TargetActor,
        PendingAttackDamage,
        GetController(),
        this,
        UDamageType::StaticClass()
    );

    if (CombatPresentation)
    {
        CombatPresentation->ResolveImpact(PendingAttackDamage);
    }

    if (Presentation)
    {
        Presentation->TriggerCueAtLocation(
            TEXT("Boss.AttackImpact"),
            TargetActor->GetActorLocation()
        );
    }

    PendingAttackId = NAME_None;
    PendingAttackDamage = 0.f;
    return AppliedDamage > 0.f;
}

void ABoneBeastBoss::CancelAttack()
{
    PendingAttackId = NAME_None;
    PendingAttackDamage = 0.f;
}

void ABoneBeastBoss::EvaluatePhase()
{
    if (CurrentPhase == ENarisBossPhase::Dead)
    {
        return;
    }

    const float MaxHP = FMath::Max(GetConfiguredMaxHealth(), 1.f);
    const float HealthRatio = CurrentHealth / MaxHP;
    ENarisBossPhase NewPhase = ENarisBossPhase::Phase1;
    int32 PhaseNumber = 1;

    if (BossData && BossData->Phases.Num() > 0)
    {
        int32 NewPhaseIndex = 0;
        for (int32 Index = 0; Index < BossData->Phases.Num(); ++Index)
        {
            if (HealthRatio <= BossData->Phases[Index].HealthThreshold)
            {
                NewPhaseIndex = Index;
            }
        }

        const int32 MaxSupportedPhaseIndex =
            FMath::Min(BossData->Phases.Num() - 1, 2);
        NewPhaseIndex =
            FMath::Clamp(NewPhaseIndex, 0, MaxSupportedPhaseIndex);
        NewPhase = static_cast<ENarisBossPhase>(NewPhaseIndex);
        PhaseNumber = NewPhaseIndex + 1;
    }
    else if (HealthRatio <= FallbackPhase3HealthPercent)
    {
        NewPhase = ENarisBossPhase::Phase3;
        PhaseNumber = 3;
    }
    else if (HealthRatio <= FallbackPhase2HealthPercent)
    {
        NewPhase = ENarisBossPhase::Phase2;
        PhaseNumber = 2;
    }

    if (NewPhase != CurrentPhase)
    {
        CurrentPhase = NewPhase;

        if (PhasePresentation)
        {
            PhasePresentation->SetAuthoritativePhase(CurrentPhase);
        }

        EmitBossEvent(
            FName(*FString::Printf(TEXT("Phase%d"), PhaseNumber))
        );
        EmitBossEvent(TEXT("PhaseTransition"));
    }
}

void ABoneBeastBoss::EmitBossEvent(FName EventName)
{
    OnBossEvent.Broadcast(EventName);

    if (Presentation && !EventName.IsNone())
    {
        Presentation->TriggerCue(
            FName(*FString::Printf(
                TEXT("Boss.%s"),
                *EventName.ToString()
            ))
        );
    }
}
