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
enum class ControlPhase { Unavailable, Free, Action, Recovery, Hit, Dead };

struct Config
{
    float MaxHealth = 100.f, MaxStamina = 100.f;
    float InputBufferSeconds = .15f;
    float HitRecoverySeconds = .2f;
    float AttackCost = 20.f, DodgeCost = 30.f, ParryCost = 15.f;
    float RegenPerSecond = 18.f, RegenDelay = .75f;
    float AttackDuration = .65f, DodgeDuration = .6f, ParryDuration = .25f;
    float DodgeInvulnerabilityStart = .1f, DodgeInvulnerabilityEnd = .35f;

    bool IsValid() const
    {
        const float Values[] = {InputBufferSeconds, HitRecoverySeconds, MaxHealth, MaxStamina, AttackCost, DodgeCost,
            ParryCost, RegenPerSecond, RegenDelay, AttackDuration, DodgeDuration,
            ParryDuration, DodgeInvulnerabilityStart, DodgeInvulnerabilityEnd};
        for (float Value : Values)
            if (!std::isfinite(Value) || Value < 0.f) return false;
        return InputBufferSeconds <= .3f && HitRecoverySeconds <= 2.f
            && MaxHealth > 0.f && MaxStamina > 0.f && AttackDuration > 0.f
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
        ClearBufferedAction();
        if (!InConfig.IsValid()) return false;
        Settings = InConfig;
        Health = Settings.MaxHealth;
        Stamina = Settings.MaxStamina;
        Time = StartedAt = BusyUntil = RegenStartsAt = 0.;
        HitUntil = 0.;
        Current = Action::Idle;
        AttackWindow = ParryConsumed = ActionCancelled = false;
        PresentationPending = false;
        CancelWindow = false;
        HitActors.clear();
        Ready = true;
        return true;
    }

    bool CanStart(Action Requested) const
    {
        if (!Ready || Health <= 0.f || PresentationPending || Time < BusyUntil) return false;
        float Cost = 0.f, Duration = 0.f;
        return ActionParameters(Requested, Cost, Duration) && Stamina >= Cost;
    }

    // لا نستهلك التحمل ولا نمنح دفاعًا إذا رفض المحرك تشغيل الحركة.
    template<class Presenter>
    bool TryStartPresented(Action Requested, Presenter&& Present)
    {
        if (!CanStart(Requested)) return false;
        bool Accepted = false;
        {
            struct PresentationGuard
            {
                bool& Pending;
                explicit PresentationGuard(bool& InPending) : Pending(InPending) { Pending = true; }
                ~PresentationGuard() { Pending = false; }
            } Guard(PresentationPending);
            Accepted = Present();
        }
        return Accepted && TryStart(Requested);
    }

    bool TryStart(Action Requested)
    {
        if (!CanStart(Requested)) return false;
        float Cost = 0.f, Duration = 0.f;
        if (!ActionParameters(Requested, Cost, Duration)) return false;
        ClearBufferedAction();
        Stamina -= Cost;
        StartedAt = Time;
        BusyUntil = Time + Duration;
        RegenStartsAt = Time + Settings.RegenDelay;
        Current = Requested;
        CancelWindow = false;
        AttackWindow = ParryConsumed = ActionCancelled = false;
        HitActors.clear();
        return true;
    }

    // آخر أمر صالح فقط، دون تمديد المهلة عند تكرار الأمر نفسه.
    bool BufferAction(Action Requested)
    {
        float Cost = 0.f, Duration = 0.f;
        if (!Ready || Health <= 0.f || PresentationPending || Settings.InputBufferSeconds <= 0.f
            || Time >= BusyUntil || BusyUntil - Time > Settings.InputBufferSeconds
            || !ActionParameters(Requested, Cost, Duration) || Stamina < Cost) return false;
        if (Buffered == Requested && Time < BufferExpiresAt) return true;
        Buffered = Requested;
        BufferExpiresAt = Time + Settings.InputBufferSeconds;
        return true;
    }

    bool TakeBufferedAction(Action& Out)
    {
        if (Buffered == Action::Idle) return false;
        if (!Ready || Health <= 0.f || Time > BufferExpiresAt)
        { ClearBufferedAction(); return false; }
        if (Time < BusyUntil || PresentationPending) return false;
        const Action Next = Buffered;
        ClearBufferedAction(); // محاولة واحدة حتى إذا فشل تشغيل الحركة.
        if (!CanStart(Next)) return false;
        Out = Next;
        return true;
    }

    void ClearBufferedAction() { Buffered = Action::Idle; BufferExpiresAt = 0.; }

    void SetCancelWindow(bool Open) { CancelWindow = Open && GetAction() != Action::Idle; }

    bool TryCancelInWindow()
    {
        if (!CancelWindow || PresentationPending || GetAction() == Action::Idle) return false;
        ClearBufferedAction();
        return CancelAction();
    }

    bool CancelAction()
    {
        if (GetAction() == Action::Idle) return false;
        ActionCancelled = true;
        CancelWindow = false;
        AttackWindow = false;
        ParryConsumed = true;
        // نحفظ كلفة الحركة وفترة التعافي؛ الإلغاء ليس استرجاعًا أو تجاوزًا للمهلة.
        return true;
    }

private:
    bool ActionParameters(Action Requested, float& Cost, float& Duration) const
    {
        switch (Requested)
        {
        case Action::LightAttack: Cost = Settings.AttackCost; Duration = Settings.AttackDuration; break;
        case Action::Dodge: Cost = Settings.DodgeCost; Duration = Settings.DodgeDuration; break;
        case Action::Parry: Cost = Settings.ParryCost; Duration = Settings.ParryDuration; break;
        default: return false;
        }
        return true;
    }

public:
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
        if (Health > 0.f)
        {
            if (Settings.HitRecoverySeconds > 0.f)
            {
                HitUntil = Time + Settings.HitRecoverySeconds;
                BusyUntil = std::max(BusyUntil, HitUntil);
                ActionCancelled = true;
                AttackWindow = CancelWindow = false;
                ParryConsumed = true;
                ClearBufferedAction();
            }
            return DamageOutcome::Applied;
        }
        BusyUntil = Time;
        ClearBufferedAction();
        AttackWindow = false;
        CancelWindow = false;
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

    Action GetAction() const { return Ready && Health > 0.f && !ActionCancelled && Time < BusyUntil ? Current : Action::Idle; }
    bool IsAttackWindowOpen() const { return AttackWindow && GetAction() == Action::LightAttack; }
    float GetHealth() const { return Health; }
    float GetStamina() const { return Stamina; }

    ControlPhase GetControlPhase() const
    {
        if (!Ready) return ControlPhase::Unavailable;
        if (Health <= 0.f) return ControlPhase::Dead;
        if (Time < HitUntil) return ControlPhase::Hit;
        if (Time >= BusyUntil) return ControlPhase::Free;
        return ActionCancelled ? ControlPhase::Recovery : ControlPhase::Action;
    }

private:
    Config Settings;
    bool Ready = false, AttackWindow = false, ParryConsumed = false, ActionCancelled = false;
    bool PresentationPending = false;
    bool CancelWindow = false;
    Action Current = Action::Idle, Buffered = Action::Idle;
    double BufferExpiresAt = 0.;
    float Health = 0.f, Stamina = 0.f;
    double Time = 0., StartedAt = 0., BusyUntil = 0., RegenStartsAt = 0.;
    double HitUntil = 0.;
    std::vector<std::uint32_t> HitActors;
};
}
