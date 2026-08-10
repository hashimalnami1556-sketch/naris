#include "BoneBeastBossController.h"

ABoneBeastBossController::ABoneBeastBossController()
{
    PrimaryActorTick.bCanEverTick = false;
}

void ABoneBeastBossController::StartEncounter()
{
    CurrentHealth = MaxHealth;
    CurrentPhase = ENarisBossPhase::Phase1;
    EmitBossEvent(TEXT("EncounterStart"));
}

void ABoneBeastBossController::ApplyEncounterDamage(float Damage)
{
    if (CurrentPhase == ENarisBossPhase::Dead || Damage <= 0.0f)
    {
        return;
    }

    CurrentHealth = FMath::Max(0.0f, CurrentHealth - Damage);
    EvaluatePhase();

    if (CurrentHealth <= 0.0f)
    {
        CurrentPhase = ENarisBossPhase::Dead;
        EmitBossEvent(TEXT("Death"));
    }
}

void ABoneBeastBossController::CompleteEncounter()
{
    EmitBossEvent(TEXT("EncounterComplete"));
}

void ABoneBeastBossController::EvaluatePhase()
{
    // Threshold values remain TUNE until playtest.
    // Phase evaluation should eventually read from UBoneBeastDataAsset.
}

void ABoneBeastBossController::EmitBossEvent(FName EventName)
{
    OnBossEvent(EventName);
}
