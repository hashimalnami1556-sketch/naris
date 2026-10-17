#include "NarisCombatRules.h"
#include "NarisMoveInput.h"
#include "NarisControlMotion.h"
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
        {"cancel_window_required", [] { auto R=Fresh(); R.TryStart(Action::LightAttack);
            Check(!R.TryCancelInWindow()); Check(R.GetAction()==Action::LightAttack); }},
        {"cancel_window_closes_and_preserves_lock", [] { auto R=Fresh(); R.TryStart(Action::LightAttack);
            R.SetCancelWindow(true); Check(R.TryCancelInWindow()); Near(R.GetStamina(),80);
            Check(R.GetControlPhase()==ControlPhase::Recovery); Check(!R.CanStart(Action::Dodge));
            R.SetCancelWindow(true); Check(!R.TryCancelInWindow()); R.Tick(.65f);
            Check(R.GetControlPhase()==ControlPhase::Free); Check(R.CanStart(Action::Dodge)); }},
        {"cancel_window_not_inherited_by_next_action", [] { auto R=Fresh(); R.TryStart(Action::Parry);
            R.SetCancelWindow(true); R.Tick(.25f); R.TryStart(Action::LightAttack);
            Check(!R.TryCancelInWindow()); }},
        {"closed_cancel_window_rejects_request", [] { auto R=Fresh(); R.TryStart(Action::Dodge);
            R.SetCancelWindow(true); R.SetCancelWindow(false); Check(!R.TryCancelInWindow()); }},
        {"hit_interrupts_defense_and_preserves_old_recovery", [] { auto R=Fresh();
            R.TryStart(Action::Dodge); Check(R.Damage(10)==DamageOutcome::Applied);
            Check(R.GetControlPhase()==ControlPhase::Hit); R.Tick(.15f);
            Check(R.Damage(10)==DamageOutcome::Applied); Near(R.GetStamina(),70);
            R.Tick(.21f); Check(R.GetControlPhase()==ControlPhase::Recovery);
            Check(!R.CanStart(Action::Parry)); R.Tick(.25f); Check(R.CanStart(Action::Parry)); }},
        {"hit_recovery_from_idle", [] { auto R=Fresh(); R.Damage(1);
            Check(R.GetControlPhase()==ControlPhase::Hit); Check(!R.CanStart(Action::Dodge));
            R.Tick(.21f); Check(R.GetControlPhase()==ControlPhase::Free); }},
        {"hit_recovery_can_be_disabled", [] { Config C; C.HitRecoverySeconds=0; auto R=Fresh(C);
            R.Damage(1); Check(R.GetControlPhase()==ControlPhase::Free); }},
        {"evade_and_parry_do_not_start_hit_recovery", [] { auto R=Fresh(); R.TryStart(Action::Dodge);
            R.Tick(.15f); Check(R.Damage(1)==DamageOutcome::Evaded);
            Check(R.GetControlPhase()==ControlPhase::Action); R.Tick(.5f); R.TryStart(Action::Parry);
            Check(R.Damage(1)==DamageOutcome::Parried); Check(R.GetControlPhase()==ControlPhase::Action); }},
        {"death_overrides_hit_and_cancel", [] { auto R=Fresh(); R.TryStart(Action::LightAttack);
            R.SetCancelWindow(true); R.Damage(100); Check(R.GetControlPhase()==ControlPhase::Dead);
            Check(!R.TryCancelInWindow()); }},
        {"failed_presentation_leaves_control_free", [] { auto R=Fresh();
            Check(!R.TryStartPresented(Action::Dodge,[]{return false;}));
            Check(R.GetControlPhase()==ControlPhase::Free); }},
        {"yaw_shortest_path_and_rate_cap", [] { YawDriver Y; double Angle=179;
            Angle=Y.Step(Angle,-179,1./60.,450,1800); Check(Angle>179 && Angle<=181);
            Check(std::abs(ShortestYawDelta(179,Angle))<=450./60.+1e-8); }},
        {"yaw_acceleration_cap", [] { YawDriver Y; Y.Step(0,90,.01,450,1800);
            Check(Y.GetVelocity()<=18.+1e-8); }},
        {"yaw_braking_after_target_change_is_bounded", [] { YawDriver Y; double Angle=0;
            for(int I=0;I<24;++I) Angle=Y.Step(Angle,170,1./120.,450,1800);
            const double Before=Y.GetVelocity(); Y.Step(Angle,Angle+.1,1./120.,450,1800);
            Check(std::abs(Y.GetVelocity()-Before)<=15.+1e-7); }},
        {"yaw_frame_rates_agree", [] { double Results[3]; int Index=0;
            for(int FPS:{30,60,120}) { YawDriver Y; double Angle=0;
                for(int I=0;I<FPS;++I) Angle=Y.Step(Angle,170,1./FPS,450,1800);
                Results[Index++]=Angle; } Near(Results[0],Results[1]); Near(Results[1],Results[2]); }},
        {"yaw_no_overshoot", [] { YawDriver Y; double Angle=0;
            for(int I=0;I<240;++I) { Angle=Y.Step(Angle,15,1./120.,450,1800); Check(Angle<=15.+1e-8); }
            Near(Angle,15); Near(Y.GetVelocity(),0); }},
        {"yaw_hitch_is_bounded", [] { YawDriver Y; double Angle=Y.Step(0,180,20,450,1800);
            Check(std::abs(Angle)<=45.); }},
        {"yaw_bad_values_are_safe", [] { YawDriver Y; Near(Y.Step(10,90,-1,450,1800),10);
            Near(Y.Step(10,std::numeric_limits<double>::infinity(),.1,450,1800),10); }},
        {"signals_idle_start_stop", [] { LocomotionSignals S;
            auto V=S.Step(0,0,0,0,false,.016); Check(!V.Starting && !V.Stopping);
            V=S.Step(40,0,100,0,false,.016); Check(V.Starting);
            V=S.Step(40,0,0,0,false,.016); Check(V.Stopping && !V.Starting); }},
        {"signals_pivot_requires_speed_and_opposite_input", [] { LocomotionSignals S;
            auto V=S.Step(200,0,-100,0,false,.016); Check(V.Pivoting);
            S.Reset(); V=S.Step(20,0,-100,0,false,.016); Check(!V.Pivoting); }},
        {"signals_direction_is_body_relative", [] { LocomotionSignals S;
            auto V=S.Step(0,200,0,100,false,.016); Near(V.DirectionDegrees,90); Near(V.Speed,200); }},
        {"signals_airborne_resets_start_and_pivot", [] { LocomotionSignals S;
            auto V=S.Step(200,0,-100,0,true,.016); Check(V.Falling && !V.Pivoting && !V.Starting); }},
        {"signals_lean_is_limited", [] { LocomotionSignals S;
            auto V=S.Step(200,0,0,1000,false,.1); Check(std::abs(V.LeanDegrees)<=8.); }},
        {"signals_invalid_sample_resets", [] { LocomotionSignals S;
            auto V=S.Step(std::numeric_limits<double>::infinity(),0,0,0,false,.1);
            Near(V.Speed,0); Near(V.LeanDegrees,0); }},
        {"input_response_budget_for_supported_frame_rates", [] {
            for(int FPS:{30,60,120}) { MoveInputFilter F; double Time=0; MoveInput V;
                while(V.Y < .9 && Time < .2) { V=F.Step({0,1},1./FPS,.12,1.4,.025); Time+=1./FPS; }
                Check(Time<=.1+1e-9); } }},
        {"cancel_request_clears_queued_action", [] { auto R=Fresh(); Action Out=Action::Idle;
            R.TryStart(Action::LightAttack); R.Tick(.55f); R.BufferAction(Action::Dodge);
            R.SetCancelWindow(true); Check(R.TryCancelInWindow()); R.Tick(.11f);
            Check(!R.TakeBufferedAction(Out)); Near(R.GetStamina(),80); }},
        {"hit_recovery_configuration_validation", [] { Config C;
            for(float V:{-1.f,3.f,std::numeric_limits<float>::infinity(),std::numeric_limits<float>::quiet_NaN()})
            { C.HitRecoverySeconds=V; Check(!C.IsValid()); } }},
        {"yaw_randomized_rate_and_finiteness", [] { YawDriver Y; double Angle=0;
            unsigned State=17; for(int I=0;I<2000;++I) {
                State=State*1664525u+1013904223u;
                const double Target=static_cast<int>(State%720u)-360.;
                const double Next=Y.Step(Angle,Target,1./60.,450,1800);
                Check(std::isfinite(Next)); Check(std::abs(ShortestYawDelta(Angle,Next))<=7.5+1e-7);
                Check(std::abs(Y.GetVelocity())<=450.+1e-7); Angle=Next;
            } }},
        {"buffer_near_recovery_starts_once", [] { auto R=Fresh(); Action Out=Action::Idle;
            R.TryStart(Action::LightAttack); R.Tick(.55f); Check(R.BufferAction(Action::Dodge));
            Near(R.GetStamina(),80); Check(!R.TakeBufferedAction(Out)); R.Tick(.11f);
            Check(R.TakeBufferedAction(Out)); Check(Out==Action::Dodge);
            Check(R.TryStartPresented(Out,[]{return true;})); Near(R.GetStamina(),50);
            Check(!R.TakeBufferedAction(Out)); }},
        {"buffer_accepts_exact_expiry_boundary", [] { Config C; C.AttackDuration=.5f; C.InputBufferSeconds=.125f;
            auto R=Fresh(C); Action Out=Action::Idle; R.TryStart(Action::LightAttack); R.Tick(.375f);
            Check(R.BufferAction(Action::Dodge)); R.Tick(.125f);
            Check(R.TakeBufferedAction(Out)); Check(Out==Action::Dodge); }},
        {"buffer_rejects_early_input", [] { auto R=Fresh(); R.TryStart(Action::LightAttack);
            Check(!R.BufferAction(Action::Dodge)); }},
        {"buffer_expired_after_hitch", [] { auto R=Fresh(); Action Out=Action::Idle;
            R.TryStart(Action::LightAttack); R.Tick(.55f); R.BufferAction(Action::Dodge);
            R.Tick(.2f); Check(!R.TakeBufferedAction(Out)); Near(R.GetStamina(),80); }},
        {"buffer_latest_valid_action_wins", [] { auto R=Fresh(); Action Out=Action::Idle;
            R.TryStart(Action::LightAttack); R.Tick(.55f); R.BufferAction(Action::Dodge);
            Check(!R.BufferAction(Action::Idle)); R.BufferAction(Action::Parry); R.Tick(.11f);
            Check(R.TakeBufferedAction(Out)); Check(Out==Action::Parry); }},
        {"buffer_duplicate_does_not_extend_expiry", [] { auto R=Fresh(); Action Out=Action::Idle;
            R.TryStart(Action::LightAttack); R.Tick(.55f); R.BufferAction(Action::Dodge);
            R.Tick(.08f); R.BufferAction(Action::Dodge); R.Tick(.08f);
            Check(!R.TakeBufferedAction(Out)); }},
        {"buffer_cleared_on_interruption", [] { auto R=Fresh(); Action Out=Action::Idle;
            R.TryStart(Action::LightAttack); R.Tick(.55f); R.BufferAction(Action::Dodge);
            R.ClearBufferedAction(); R.CancelAction(); R.Tick(.11f);
            Check(!R.TakeBufferedAction(Out)); Check(R.CanStart(Action::Dodge)); Near(R.GetStamina(),80); }},
        {"buffer_cleared_on_death", [] { auto R=Fresh(); Action Out=Action::Idle;
            R.TryStart(Action::LightAttack); R.Tick(.55f); R.BufferAction(Action::Dodge);
            R.Damage(100); R.Tick(.11f); Check(!R.TakeBufferedAction(Out)); }},
        {"buffer_failed_playback_is_not_retried", [] { auto R=Fresh(); Action Out=Action::Idle;
            R.TryStart(Action::LightAttack); R.Tick(.55f); R.BufferAction(Action::Dodge); R.Tick(.11f);
            Check(R.TakeBufferedAction(Out)); Check(!R.TryStartPresented(Out,[]{return false;}));
            Check(!R.TakeBufferedAction(Out)); Near(R.GetStamina(),80); }},
        {"buffer_disabled_and_invalid_config", [] { Config C; C.InputBufferSeconds=0; auto R=Fresh(C);
            R.TryStart(Action::LightAttack); R.Tick(.55f); Check(!R.BufferAction(Action::Dodge));
            C.InputBufferSeconds=.31f; Check(!C.IsValid()); }},
        {"buffer_not_allowed_during_presentation", [] { auto R=Fresh();
            Check(R.TryStartPresented(Action::Dodge,[&]{Check(!R.BufferAction(Action::Parry));return true;})); }},
        {"buffer_rejects_unaffordable_request", [] { Config C; C.MaxStamina=25; auto R=Fresh(C);
            R.TryStart(Action::LightAttack); R.Tick(.55f); Check(!R.BufferAction(Action::Parry)); }},
        {"move_radial_dead_zone", [] { MoveInputFilter F; auto V=F.Step({.05,.05},.016,.12,1.4,.04);
            Near(V.X,0); Near(V.Y,0); }},
        {"move_diagonal_speed_capped", [] { MoveInputFilter F; auto V=F.Step({1,1},1,.12,1.4,0);
            Near(std::hypot(V.X,V.Y),1); Near(V.X,V.Y); }},
        {"move_release_has_no_input_tail", [] { MoveInputFilter F; F.Step({1,0},1,.12,1.4,.04);
            auto V=F.Step({},.016,.12,1.4,.04); Near(V.X,0); Near(V.Y,0); }},
        {"move_filter_frame_independent", [] { MoveInputFilter A,B; auto V=A.Step({.7,.2},.1,.12,1.4,.04);
            MoveInput W; for(int I=0;I<10;++I) W=B.Step({.7,.2},.01,.12,1.4,.04);
            Near(V.X,W.X); Near(V.Y,W.Y); }},
        {"move_curve_preserves_analog_range", [] { MoveInputFilter F; auto V=F.Step({.56,0},1,.12,2,0);
            Near(V.X,.25); Near(V.Y,0); }},
        {"move_reversal_remains_bounded", [] { MoveInputFilter F; F.Step({1,0},1,0,1,.04);
            auto V=F.Step({-1,0},.01,0,1,.04); Check(V.X>0 && V.X<1);
            V=F.Step({-1,0},1,0,1,.04); Near(V.X,-1); }},
        {"move_invalid_input_resets", [] { MoveInputFilter F; F.Step({1,0},1,0,1,0);
            auto V=F.Step({std::numeric_limits<double>::quiet_NaN(),0},.01,0,1,.04);
            Near(V.X,0); Check(!MoveInputFilter::Valid(1,1,.04));
            Check(!MoveInputFilter::Valid(.12,0,.04)); Check(!MoveInputFilter::Valid(.12,1,-1)); }},
        {"move_invalid_delta_does_not_advance", [] { MoveInputFilter F;
            auto V=F.Step({1,0},-1,0,1,.04); Near(V.X,0);
            V=F.Step({1,0},std::numeric_limits<double>::infinity(),0,1,.04); Near(V.X,0); }},
        {"move_reset_clears_history", [] { MoveInputFilter F; F.Step({1,0},1,0,1,.04); F.Reset();
            auto V=F.Step({0,1},.01,0,1,.04); Near(V.X,0); Check(V.Y>0 && V.Y<1); }},
        {"presentation_blocks_reentrant_requests", [] { auto R=Fresh();
            Check(R.TryStartPresented(Action::Dodge, [&] {
                Check(!R.TryStart(Action::LightAttack)); Check(!R.CanStart(Action::Parry)); return true;
            })); Near(R.GetStamina(),70); }},
        {"presentation_has_no_early_invulnerability", [] { auto R=Fresh();
            Check(!R.TryStartPresented(Action::Dodge, [&] {
                Check(R.Damage(10)==DamageOutcome::Applied); return true;
            })); Near(R.GetHealth(),90); Near(R.GetStamina(),100);
            Check(R.GetControlPhase()==ControlPhase::Hit); }},
        {"yaw_wraps_multiple_turns", [] { Near(ShortestYawDelta(359,-359),2);
            Near(ShortestYawDelta(-359,359),-2); Near(ShortestYawDelta(719,-719),2); }},
        {"death_during_presentation_aborts_commit", [] { auto R=Fresh();
            Check(!R.TryStartPresented(Action::Dodge, [&] { R.Damage(100); return true; }));
            Near(R.GetStamina(),100); Check(R.GetAction()==Action::Idle); }},
        {"failed_presentation_allows_retry", [] { auto R=Fresh();
            Check(!R.TryStartPresented(Action::Dodge, [] { return false; }));
            Check(R.TryStartPresented(Action::Dodge, [] { return true; })); Near(R.GetStamina(),70); }},
        {"presentation_exception_releases_reservation", [] { auto R=Fresh(); bool Threw=false;
            try { R.TryStartPresented(Action::Dodge, []()->bool { throw std::runtime_error("callback"); }); }
            catch(const std::runtime_error&) { Threw=true; }
            Check(Threw); Check(R.CanStart(Action::Dodge)); Near(R.GetStamina(),100); }},
        {"failed_playback_spends_nothing", [] { auto R=Fresh();
            Check(!R.TryStartPresented(Action::LightAttack, [] { return false; }));
            Near(R.GetStamina(),100); Check(R.CanStart(Action::LightAttack)); }},
        {"failed_dodge_grants_no_defense", [] { auto R=Fresh();
            Check(!R.TryStartPresented(Action::Dodge, [] { return false; })); R.Tick(.15f);
            Check(R.Damage(10)==DamageOutcome::Applied); Near(R.GetStamina(),100); }},
        {"failed_parry_grants_no_defense", [] { auto R=Fresh();
            Check(!R.TryStartPresented(Action::Parry, [] { return false; }));
            Check(R.Damage(10)==DamageOutcome::Applied); }},
        {"accepted_playback_spends_once", [] { auto R=Fresh(); int Calls=0;
            Check(R.TryStartPresented(Action::LightAttack, [&] { ++Calls; return true; }));
            Check(Calls==1); Near(R.GetStamina(),80); }},
        {"rejected_action_never_plays", [] { Config C; C.MaxStamina=1; auto R=Fresh(C); int Calls=0;
            Check(!R.TryStartPresented(Action::Dodge, [&] { ++Calls; return true; })); Check(Calls==0); }},
        {"spam_does_not_replay", [] { auto R=Fresh(); int Calls=0;
            Check(R.TryStartPresented(Action::Dodge, [&] { ++Calls; return true; }));
            Check(!R.TryStartPresented(Action::Dodge, [&] { ++Calls; return true; })); Check(Calls==1); }},
        {"cancel_attack_closes_hits", [] { auto R=Fresh(); Check(R.TryStart(Action::LightAttack));
            R.SetAttackWindow(true); Check(R.CancelAction()); Check(!R.RegisterHit(1));
            R.SetAttackWindow(true); Check(!R.RegisterHit(1)); }},
        {"cancel_dodge_revokes_invulnerability", [] { auto R=Fresh(); Check(R.TryStart(Action::Dodge));
            R.Tick(.15f); Check(R.CancelAction()); Check(R.Damage(10)==DamageOutcome::Applied); }},
        {"cancel_parry_revokes_defense", [] { auto R=Fresh(); Check(R.TryStart(Action::Parry));
            Check(R.CancelAction()); Check(R.Damage(10)==DamageOutcome::Applied); }},
        {"cancel_preserves_recovery_and_cost", [] { auto R=Fresh(); Check(R.TryStart(Action::Dodge));
            Check(R.CancelAction()); Near(R.GetStamina(),70); Check(R.GetAction()==Action::Idle);
            Check(!R.CanStart(Action::Dodge)); R.Tick(.6f); Check(R.CanStart(Action::Dodge)); }},
        {"cancel_cannot_restart_or_replay", [] { auto R=Fresh(); Check(R.TryStart(Action::Dodge));
            Check(R.CancelAction()); int Calls=0;
            Check(!R.TryStartPresented(Action::LightAttack,[&]{++Calls;return true;})); Check(Calls==0); }},
        {"cancel_keeps_regen_delay", [] { auto R=Fresh(); Check(R.TryStart(Action::Dodge));
            R.CancelAction(); R.Tick(.75f); Near(R.GetStamina(),70); R.Tick(.25f); Near(R.GetStamina(),74.5f); }},
        {"cancel_idle_is_noop", [] { auto R=Fresh(); Check(!R.CancelAction());
            Near(R.GetStamina(),100); Check(R.CanStart(Action::Dodge)); }},
        {"new_action_after_cancel_resets_state", [] { auto R=Fresh(); Check(R.TryStart(Action::Parry));
            R.CancelAction(); R.Tick(.25f); Check(R.TryStart(Action::Parry));
            Check(R.Damage(10)==DamageOutcome::Parried); }},
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
