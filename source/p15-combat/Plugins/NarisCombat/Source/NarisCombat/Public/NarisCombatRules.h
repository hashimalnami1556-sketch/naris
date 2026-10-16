#pragma once

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <vector>

// نفس القواعد تستخدمها إضافة Unreal والاختبارات المحلية، دون محاكاة واجهات المحرك.
namespace NarisP15
{
enum class Action { Idle, LightAttack, Dodge, Parry };
enum class DamageOutcome { Ignored, Applied, Evaded, Parried, Killed };

struct Config
{
    float MaxHealth = 100.f, MaxStamina = 100.f;
    float AttackCost = 20.f, DodgeCost = 30.f, ParryCost = 15.f;
    float RegenPerSecond = 18.f, RegenDelay = .75f;
    float AttackDuration = .65f, DodgeDuration = .6f, ParryDuration = .25f;
    float DodgeInvulnerabilityStart = .1f, DodgeInvulnerabilityEnd = .35f;

    bool IsValid() const
    {
        const float Values[] = {MaxHealth, MaxStamina, AttackCost, DodgeCost,
            ParryCost, RegenPerSecond, RegenDelay, AttackDuration, DodgeDuration,
            ParryDuration, DodgeInvulnerabilityStart, DodgeInvulnerabilityEnd};
        for (float Value : Values)
            if (!std::isfinite(Value) || Value < 0.f) return false;
        return MaxHealth > 0.f && MaxStamina > 0.f && AttackDuration > 0.f
            && DodgeDuration > 0.f && ParryDuration > 0.f
            && DodgeInvulnerabilityStart < DodgeInvulnerabilityEnd
            && DodgeInvulnerabilityEnd <= DodgeDuration;
    }
};

class Rules
{
public:
    bool Initialize(const Config& InConfig)
    {
        Ready = false;
        if (!InConfig.IsValid()) return false;
        Settings = InConfig;
        Health = Settings.MaxHealth;
        Stamina = Settings.MaxStamina;
        Time = StartedAt = BusyUntil = RegenStartsAt = 0.;
        Current = Action::Idle;
        AttackWindow = ParryConsumed = false;
        HitActors.clear();
        Ready = true;
        return true;
    }

    bool TryStart(Action Requested)
    {
        if (!Ready || Health <= 0.f || GetAction() != Action::Idle) return false;
        float Cost = 0.f, Duration = 0.f;
        switch (Requested)
        {
        case Action::LightAttack: Cost = Settings.AttackCost; Duration = Settings.AttackDuration; break;
        case Action::Dodge: Cost = Settings.DodgeCost; Duration = Settings.DodgeDuration; break;
        case Action::Parry: Cost = Settings.ParryCost; Duration = Settings.ParryDuration; break;
        default: return false;
        }
        if (Stamina < Cost) return false;
        Stamina -= Cost;
        StartedAt = Time;
        BusyUntil = Time + Duration;
        RegenStartsAt = Time + Settings.RegenDelay;
        Current = Requested;
        AttackWindow = ParryConsumed = false;
        HitActors.clear();
        return true;
    }

    void Tick(float DeltaSeconds)
    {
        if (!Ready || !std::isfinite(DeltaSeconds) || DeltaSeconds <= 0.f) return;
        const double Previous = Time;
        Time += DeltaSeconds;
        if (GetAction() == Action::Idle) AttackWindow = false;
        // نعوّض الجزء الواقع بعد نهاية التأخير فقط، حتى مع إطار طويل.
        if (Health > 0.f)
        {
            const double Eligible = std::max(0., Time - std::max(Previous, RegenStartsAt));
            Stamina = static_cast<float>(std::min<double>(Settings.MaxStamina,
                static_cast<double>(Stamina) + Eligible * Settings.RegenPerSecond));
        }
    }

    DamageOutcome Damage(float Amount)
    {
        if (!Ready || Health <= 0.f || !std::isfinite(Amount) || Amount <= 0.f)
            return DamageOutcome::Ignored;
        const double Elapsed = Time - StartedAt;
        if (GetAction() == Action::Dodge && Elapsed >= Settings.DodgeInvulnerabilityStart
            && Elapsed < Settings.DodgeInvulnerabilityEnd) return DamageOutcome::Evaded;
        if (GetAction() == Action::Parry && !ParryConsumed)
        {
            ParryConsumed = true;
            return DamageOutcome::Parried;
        }
        Health = std::max(0.f, Health - Amount);
        if (Health > 0.f) return DamageOutcome::Applied;
        BusyUntil = Time;
        AttackWindow = false;
        return DamageOutcome::Killed;
    }

    void SetAttackWindow(bool Open)
    {
        AttackWindow = Open && GetAction() == Action::LightAttack;
    }

    bool RegisterHit(std::uint32_t ActorId)
    {
        if (!IsAttackWindowOpen() || ActorId == 0
            || std::find(HitActors.begin(), HitActors.end(), ActorId) != HitActors.end()) return false;
        HitActors.push_back(ActorId);
        return true;
    }

    Action GetAction() const { return Ready && Health > 0.f && Time < BusyUntil ? Current : Action::Idle; }
    bool IsAttackWindowOpen() const { return AttackWindow && GetAction() == Action::LightAttack; }
    float GetHealth() const { return Health; }
    float GetStamina() const { return Stamina; }

private:
    Config Settings;
    bool Ready = false, AttackWindow = false, ParryConsumed = false;
    Action Current = Action::Idle;
    float Health = 0.f, Stamina = 0.f;
    double Time = 0., StartedAt = 0., BusyUntil = 0., RegenStartsAt = 0.;
    std::vector<std::uint32_t> HitActors;
};
}
