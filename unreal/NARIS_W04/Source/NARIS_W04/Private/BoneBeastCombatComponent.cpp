#include "BoneBeastCombatComponent.h"

void UBoneBeastCombatComponent::StartAttack(FName AttackId)
{
    if (!AttackId.IsNone())
    {
        CurrentAttackId = AttackId;
        OnCombatEvent.Broadcast(FName(TEXT("AttackStart")));
    }
}

void UBoneBeastCombatComponent::ResolveImpact(float Damage)
{
    if (Damage > 0.f)
    {
        OnCombatEvent.Broadcast(FName(TEXT("Impact")));
        CurrentAttackId = NAME_None;
    }
}

void UBoneBeastCombatComponent::TriggerStagger()
{
    OnCombatEvent.Broadcast(FName(TEXT("Stagger")));
}
