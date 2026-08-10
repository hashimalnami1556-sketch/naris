#include "BoneBeastBoss.h"
#include "BoneBeastDataAsset.h"

ABoneBeastBoss::ABoneBeastBoss()
{
    PrimaryActorTick.bCanEverTick = false;
}

void ABoneBeastBoss::StartEncounter()
{
    if (!BossData)
    {
        return;
    }

    CurrentHealth = BossData->MaxHealth;
    CurrentPhase = ENarisBossPhase::Phase1;
    EmitBossEvent(TEXT("EncounterStarted"));
}

void ABoneBeastBoss::ApplyDamageToEncounter(float Damage)
{
    if (CurrentPhase == ENarisBossPhase::Dead || Damage <= 0.f)
    {
        return;
    }

    CurrentHealth = FMath::Max(0.f, CurrentHealth - Damage);
    EmitBossEvent(TEXT("DamageTaken"));
    EvaluatePhase();

    if (CurrentHealth <= 0.f)
    {
        CurrentPhase = ENarisBossPhase::Dead;
        EmitBossEvent(TEXT("Death"));
    }
}

void ABoneBeastBoss::CompleteEncounter()
{
    if (CurrentPhase != ENarisBossPhase::Dead)
    {
        return;
    }

    EmitBossEvent(TEXT("EncounterComplete"));
}

void ABoneBeastBoss::EvaluatePhase()
{
    if (!BossData || BossData->Phases.Num() == 0 || CurrentPhase == ENarisBossPhase::Dead)
    {
        return;
    }

    const float MaxHP = FMath::Max(BossData->MaxHealth, 1.f);
    const float HealthRatio = CurrentHealth / MaxHP;

    // Phase thresholds remain data-driven and tuneable.
    int32 NewPhaseIndex = 0;
    for (int32 Index = 0; Index < BossData->Phases.Num(); ++Index)
    {
        if (HealthRatio <= BossData->Phases[Index].HealthThreshold)
        {
            NewPhaseIndex = Index;
        }
    }

    const ENarisBossPhase NewPhase = static_cast<ENarisBossPhase>(FMath::Clamp(NewPhaseIndex, 0, 2));
    if (NewPhase != CurrentPhase)
    {
        CurrentPhase = NewPhase;
        EmitBossEvent(TEXT("PhaseTransition"));
    }
}

void ABoneBeastBoss::EmitBossEvent(FName EventName)
{
    OnBossEvent.Broadcast(EventName);
}
