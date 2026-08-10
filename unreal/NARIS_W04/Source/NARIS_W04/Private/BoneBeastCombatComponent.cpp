#include "BoneBeastCombatComponent.h"

void UBoneBeastCombatComponent::StartAttack(FName AttackId)
{
    if (!AttackId.IsNone())
    {
        OnCombatEvent.Broadcast(FName(TEXT("AttackStart")));
    }
}

void UBoneBeastCombatComponent::ResolveImpact(float Damage)
{
    if (Damage > 0.f)
    {
        OnCombatEvent.Broadcast(FName(TEXT("Impact")));
    }
}

void UBoneBeastCombatComponent::TriggerStagger()
{
    OnCombatEvent.Broadcast(FName(TEXT("Stagger")));
}
