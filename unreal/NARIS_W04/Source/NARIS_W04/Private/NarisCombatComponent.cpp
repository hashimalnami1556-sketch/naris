#include "NarisCombatComponent.h"

#include "Engine/World.h"

UNarisCombatComponent::UNarisCombatComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

FNarisCombatResult UNarisCombatComponent::ResolveHit(
    float BaseDamage,
    float PoiseDamage,
    bool bParried,
    bool bCritical
)
{
    FNarisCombatResult Result;
    Result.bParried = bParried;
    Result.bCritical = bCritical;

    if (bParried)
    {
        AddResonance(15.f);
        Result.bCritical = false;
    }
    else
    {
        Result.Damage = bCritical ? BaseDamage * 1.5f : BaseDamage;
        Result.PoiseDamage = PoiseDamage;

        Health = FMath::Clamp(Health - Result.Damage, 0.f, MaxHealth);
        Poise = FMath::Clamp(Poise - PoiseDamage, 0.f, MaxPoise);

        Result.bStaggered = Poise <= 0.f;
        Result.bExecutionWindow = Result.bStaggered && Health > 0.f;

        if (Result.bStaggered)
        {
            ResetPoise();
        }
    }

    OnCombatResolved.Broadcast(Result);
    return Result;
}

FNarisCombatResult UNarisCombatComponent::ResolveIncomingHit(
    float BaseDamage,
    float PoiseDamage,
    bool bCritical
)
{
    if (IsInvulnerable())
    {
        FNarisCombatResult Result;
        Result.bEvaded = true;
        OnCombatResolved.Broadcast(Result);
        return Result;
    }

    const bool bParry = IsParryWindowActive();
    if (bParry)
    {
        ParryWindowEndTime = -1.f;
    }

    return ResolveHit(BaseDamage, PoiseDamage, bParry, bCritical);
}

void UNarisCombatComponent::OpenParryWindow(float DurationSeconds)
{
    if (DurationSeconds <= 0.f || !GetWorld())
    {
        return;
    }

    ParryWindowEndTime = GetWorld()->GetTimeSeconds() + DurationSeconds;
}

void UNarisCombatComponent::OpenInvulnerabilityWindow(float DurationSeconds)
{
    if (DurationSeconds <= 0.f || !GetWorld())
    {
        return;
    }

    InvulnerabilityEndTime = GetWorld()->GetTimeSeconds() + DurationSeconds;
}

void UNarisCombatComponent::ClearDefenseWindows()
{
    ParryWindowEndTime = -1.f;
    InvulnerabilityEndTime = -1.f;
}

bool UNarisCombatComponent::IsParryWindowActive() const
{
    return GetWorld()
        && ParryWindowEndTime >= 0.f
        && GetWorld()->GetTimeSeconds() <= ParryWindowEndTime;
}

bool UNarisCombatComponent::IsInvulnerable() const
{
    return GetWorld()
        && InvulnerabilityEndTime >= 0.f
        && GetWorld()->GetTimeSeconds() <= InvulnerabilityEndTime;
}

void UNarisCombatComponent::AddResonance(float Amount)
{
    Resonance = FMath::Clamp(Resonance + Amount, 0.f, MaxResonance);
}

void UNarisCombatComponent::ResetPoise()
{
    Poise = MaxPoise;
}
