#include "NarisCombatRules.h"
#include <cstdlib>
#include <iostream>
#include <limits>
#include <map>
#include <stdexcept>
#include <string>

using namespace NarisP15;
static void Check(bool Value) { if (!Value) throw std::runtime_error("behavior assertion failed"); }
static void Near(float Actual, float Expected) { Check(std::abs(Actual - Expected) < .002f); }
static Rules Fresh(const Config& C = Config()) { Rules R; Check(R.Initialize(C)); return R; }

int main(int Argc, char** Argv)
{
    const std::map<std::string, void(*)()> Cases = {
        {"initial_vitals", [] { auto R=Fresh(); Near(R.GetHealth(),100); Near(R.GetStamina(),100); }},
        {"spam_rejected", [] { auto R=Fresh(); Check(R.TryStart(Action::LightAttack));
            for(int I=0;I<100;++I) { Check(!R.TryStart(Action::LightAttack)); }
            Near(R.GetStamina(),80); }},
        {"cooldown_expires", [] { auto R=Fresh(); Check(R.TryStart(Action::LightAttack));
            R.Tick(.65f); Check(R.TryStart(Action::Dodge)); Near(R.GetStamina(),50); }},
        {"insufficient_stamina", [] { Config C; C.MaxStamina=19; auto R=Fresh(C);
            Check(!R.TryStart(Action::LightAttack)); Near(R.GetStamina(),19); }},
        {"no_actions_before_initialize", [] { Rules R; Check(!R.TryStart(Action::Dodge));
            Check(R.Damage(1)==DamageOutcome::Ignored); }},
        {"invalid_configuration", [] {
            float Config::* Fields[] = {&Config::MaxHealth,&Config::MaxStamina,&Config::AttackCost,
                &Config::DodgeCost,&Config::ParryCost,&Config::RegenPerSecond,&Config::RegenDelay,
                &Config::AttackDuration,&Config::DodgeDuration,&Config::ParryDuration,
                &Config::DodgeInvulnerabilityStart,&Config::DodgeInvulnerabilityEnd};
            for (auto Field:Fields) for(float Value:{-1.f,std::numeric_limits<float>::infinity(),
                std::numeric_limits<float>::quiet_NaN()}) {
                Config C; C.*Field=Value; Rules R; Check(!R.Initialize(C));
            }
        }},
        {"invalid_window", [] { Config C; C.DodgeInvulnerabilityEnd=2; Check(!C.IsValid());
            C=Config(); C.AttackDuration=0; Check(!C.IsValid()); }},
        {"invalid_action", [] { auto R=Fresh(); Check(!R.TryStart(static_cast<Action>(255)));
            Check(!R.TryStart(Action::Idle)); Near(R.GetStamina(),100); }},
        {"invalid_damage", [] { auto R=Fresh();
            for(float V:{0.f,-2.f,std::numeric_limits<float>::infinity(),std::numeric_limits<float>::quiet_NaN()})
                { Check(R.Damage(V)==DamageOutcome::Ignored); }
            Near(R.GetHealth(),100); }},
        {"lethal_damage", [] { auto R=Fresh(); Check(R.TryStart(Action::LightAttack)); R.SetAttackWindow(true);
            Check(R.Damage(200)==DamageOutcome::Killed); Near(R.GetHealth(),0);
            Check(!R.RegisterHit(1)); Check(!R.TryStart(Action::Dodge));
            R.Tick(10); Near(R.GetStamina(),80); }},
        {"dodge_startup_vulnerable", [] { auto R=Fresh(); Check(R.TryStart(Action::Dodge));
            Check(R.Damage(10)==DamageOutcome::Applied); Near(R.GetHealth(),90); }},
        {"dodge_window", [] { auto R=Fresh(); Check(R.TryStart(Action::Dodge)); R.Tick(.1f);
            Check(R.Damage(10)==DamageOutcome::Evaded); Near(R.GetHealth(),100); }},
        {"dodge_recovery_vulnerable", [] { auto R=Fresh(); Check(R.TryStart(Action::Dodge)); R.Tick(.35f);
            Check(R.Damage(10)==DamageOutcome::Applied); }},
        {"parry_single_use", [] { auto R=Fresh(); Check(R.TryStart(Action::Parry));
            Check(R.Damage(10)==DamageOutcome::Parried); Check(R.Damage(10)==DamageOutcome::Applied);
            Near(R.GetHealth(),90); }},
        {"parry_expires", [] { auto R=Fresh(); Check(R.TryStart(Action::Parry)); R.Tick(.25f);
            Check(R.Damage(10)==DamageOutcome::Applied); }},
        {"regen_delay", [] { auto R=Fresh(); Check(R.TryStart(Action::LightAttack));
            R.Tick(.75f); Near(R.GetStamina(),80); R.Tick(.25f); Near(R.GetStamina(),84.5f); }},
        {"regen_crossing_frame", [] { auto R=Fresh(); Check(R.TryStart(Action::LightAttack));
            R.Tick(.5f); R.Tick(.5f); Near(R.GetStamina(),84.5f); }},
        {"regen_frame_independent", [] { auto A=Fresh(),B=Fresh();
            Check(A.TryStart(Action::LightAttack)); Check(B.TryStart(Action::LightAttack));
            A.Tick(1); for(int I=0;I<100;++I) B.Tick(.01f); Near(A.GetStamina(),B.GetStamina()); }},
        {"regen_capped", [] { auto R=Fresh(); Check(R.TryStart(Action::Dodge));
            R.Tick(std::numeric_limits<float>::max()); Near(R.GetStamina(),100); }},
        {"invalid_delta", [] { auto R=Fresh(); Check(R.TryStart(Action::LightAttack));
            for(float V:{-1.f,0.f,std::numeric_limits<float>::infinity(),std::numeric_limits<float>::quiet_NaN()}) R.Tick(V);
            Near(R.GetStamina(),80); Check(R.GetAction()==Action::LightAttack); }},
        {"hit_window_required", [] { auto R=Fresh(); R.SetAttackWindow(true); Check(!R.RegisterHit(1));
            Check(R.TryStart(Action::LightAttack)); Check(!R.RegisterHit(1));
            R.SetAttackWindow(true); Check(R.RegisterHit(1)); }},
        {"once_per_swing", [] { auto R=Fresh(); Check(R.TryStart(Action::LightAttack)); R.SetAttackWindow(true);
            Check(!R.RegisterHit(0)); Check(R.RegisterHit(1)); Check(!R.RegisterHit(1)); Check(R.RegisterHit(2));
            R.SetAttackWindow(false); R.SetAttackWindow(true); Check(!R.RegisterHit(1)); }},
        {"hit_window_expires", [] { auto R=Fresh(); Check(R.TryStart(Action::LightAttack)); R.SetAttackWindow(true);
            R.Tick(.65f); Check(!R.RegisterHit(1)); Check(!R.IsAttackWindowOpen()); }},
        {"next_swing_resets_hits", [] { auto R=Fresh(); Check(R.TryStart(Action::LightAttack)); R.SetAttackWindow(true);
            Check(R.RegisterHit(1)); R.Tick(.65f); Check(R.TryStart(Action::LightAttack));
            R.SetAttackWindow(true); Check(R.RegisterHit(1)); }},
        {"zero_cost_still_locked", [] { Config C; C.AttackCost=0; auto R=Fresh(C);
            Check(R.TryStart(Action::LightAttack)); Check(!R.TryStart(Action::Dodge)); Near(R.GetStamina(),100); }}
    };
    if (Argc!=2 || Cases.count(Argv[1])==0) return 2;
    try { Cases.at(Argv[1])(); std::cout << "PASS " << Argv[1] << '\n'; }
    catch(const std::exception& E) { std::cerr << "FAIL " << Argv[1] << ": " << E.what() << '\n'; return 1; }
    return 0;
}
