#include "BoneBeastPhaseComponent.h"

void UBoneBeastPhaseComponent::EvaluateHealth(float CurrentHealth, float MaxHealth)
{
    if (MaxHealth <= 0.f)
    {
        return;
    }

    const float Ratio = CurrentHealth / MaxHealth;
    int32 PhaseIndex = 0;

    // Generic three-phase scaffold. Final thresholds belong in BossData/playtest.
    if (Ratio <= 0.66f)
    {
        PhaseIndex = 1;
    }
    if (Ratio <= 0.33f)
    {
        PhaseIndex = 2;
    }

    if (PhaseIndex != LastPhaseIndex)
    {
        LastPhaseIndex = PhaseIndex;
        OnPhaseTransition.Broadcast(FName(*FString::Printf(TEXT("Phase%d"), PhaseIndex + 1)));
    }
}
