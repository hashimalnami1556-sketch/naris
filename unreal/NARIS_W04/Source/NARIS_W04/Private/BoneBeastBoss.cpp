#include "BoneBeastBoss.h"
#include "BoneBeastDataAsset.h"

ABoneBeastBoss::ABoneBeastBoss()
{
    PrimaryActorTick.bCanEverTick = false;
}

void ABoneBeastBoss::StartEncounter()
{
    if (!BossData || BossData->MaxHealth <= 0.f || bEncounterActive)
    {
        return;
    }

    CurrentHealth = BossData->MaxHealth;
    CurrentPhase = ENarisBossPhase::Phase1;
    bEncounterActive = true;
    bEncounterComplete = false;
    EmitBossEvent(TEXT("EncounterStarted"));
}

void ABoneBeastBoss::ResetEncounter()
{
    if (!BossData)
    {
        return;
    }

    CurrentHealth = BossData->MaxHealth;
    CurrentPhase = ENarisBossPhase::Phase1;
    bEncounterActive = false;
    bEncounterComplete = false;
    EmitBossEvent(TEXT("EncounterReset"));
}

void ABoneBeastBoss::ApplyDamageToEncounter(float Damage)
{
    if (!bEncounterActive || bEncounterComplete || CurrentPhase == ENarisBossPhase::Dead || Damage <= 0.f)
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
        EmitBossEvent(TEXT("Death"));
        return;
    }

    EvaluatePhase();
}

void ABoneBeastBoss::CompleteEncounter()
{
    if (bEncounterComplete || CurrentPhase != ENarisBossPhase::Dead)
    {
        return;
    }

    bEncounterComplete = true;
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
    int32 NewPhaseIndex = 0;

    for (int32 Index = 0; Index < BossData->Phases.Num(); ++Index)
    {
        if (HealthRatio <= BossData->Phases[Index].HealthThreshold)
        {
            NewPhaseIndex = Index;
        }
    }

    const int32 MaxSupportedPhaseIndex = FMath::Min(BossData->Phases.Num() - 1, 2);
    NewPhaseIndex = FMath::Clamp(NewPhaseIndex, 0, MaxSupportedPhaseIndex);
    const ENarisBossPhase NewPhase = static_cast<ENarisBossPhase>(NewPhaseIndex);

    if (NewPhase != CurrentPhase)
    {
        CurrentPhase = NewPhase;
        EmitBossEvent(FName(*FString::Printf(TEXT("Phase%d"), NewPhaseIndex + 1)));
        EmitBossEvent(TEXT("PhaseTransition"));
    }
}

void ABoneBeastBoss::EmitBossEvent(FName EventName)
{
    OnBossEvent.Broadcast(EventName);
}
