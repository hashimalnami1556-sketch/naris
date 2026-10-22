#pragma once
#include <algorithm>
#include <cmath>

namespace NarisP15
{
inline double ShortestYawDelta(double From, double To)
{
    if (!std::isfinite(From) || !std::isfinite(To)) return 0.;
    return std::remainder(std::fmod(To, 360.) - std::fmod(From, 360.), 360.);
}

// Desired controller heading only; CharacterMovement remains the actor-rotation owner.
class YawDriver
{
public:
    double Step(double Current, double Desired, double Delta, double MaxSpeed, double Acceleration)
    {
        if (!std::isfinite(Current)) { Reset(); return 0.; }
        if (!std::isfinite(Desired) || !std::isfinite(Delta) || Delta <= 0.
            || !std::isfinite(MaxSpeed) || MaxSpeed <= 0.
            || !std::isfinite(Acceleration) || Acceleration <= 0.)
        { Reset(); return Current; }
        // A hitch must not turn the character through a large angle in one rendered frame.
        double Remaining = std::min(Delta, .1);
        while (Remaining > 1e-10)
        {
            const double H = std::min(Remaining, 1. / 120.);
            const double Error = ShortestYawDelta(Current, Desired);
            if (std::abs(Error) < 1e-7 && std::abs(Error) <= MaxSpeed * H
                && std::abs(Velocity) <= Acceleration * H)
            { Current += Error; Reset(); break; }
            // Damped steering preserves inertia after an abrupt target change. Snapping
            // to a nearby target would violate the angular-deceleration limit.
            const double AngularAcceleration = std::clamp(144. * Error - 24. * Velocity,
                -Acceleration, Acceleration);
            const double Next = std::clamp(Velocity + AngularAcceleration * H, -MaxSpeed, MaxSpeed);
            const double Travel = (Velocity + Next) * .5 * H;
            Current += Travel;
            Velocity = Next;
            Remaining -= H;
        }
        return Current;
    }
    double GetVelocity() const { return Velocity; }
    void Reset() { Velocity = 0.; }
private:
    double Velocity = 0.;
};

struct MotionSignals
{
    double Speed = 0., DirectionDegrees = 0., LeanDegrees = 0.;
    bool Starting = false, Stopping = false, Pivoting = false, Falling = false;
};

// Inputs are velocity/acceleration in actor-local XY coordinates, in UE units.
// These signals select existing clips; they do not manufacture animations or foot IK.
class LocomotionSignals
{
public:
    MotionSignals Step(double VX, double VY, double AX, double AY, bool Falling, double Delta)
    {
        const double Values[] = {VX, VY, AX, AY, Delta};
        for (double Value : Values) if (!std::isfinite(Value)) { Reset(); return {}; }
        if (Delta <= 0.) { Reset(); return {}; }
        MotionSignals Out;
        Out.Speed = std::hypot(VX, VY);
        const double Acceleration = std::hypot(AX, AY);
        if (!std::isfinite(Out.Speed) || !std::isfinite(Acceleration)) { Reset(); return {}; }
        Out.DirectionDegrees = Out.Speed > 1. ? std::atan2(VY, VX) * (180. / 3.14159265358979323846) : 0.;
        Out.Falling = Falling;
        const bool HasInput = Acceleration > 1.;
        const bool WasMoving = Moving;
        Moving = Moving ? Out.Speed >= 5. : Out.Speed > 15.;
        StartRemaining = std::max(0., StartRemaining - Delta);
        if (Falling) StartRemaining = 0.;
        else if (!WasMoving && Moving && HasInput) StartRemaining = .15;
        Out.Pivoting = !Falling && Out.Speed >= 80. && HasInput
            && (VX / Out.Speed * (AX / Acceleration) + VY / Out.Speed * (AY / Acceleration)) < -.7071067811865475;
        Out.Stopping = !Falling && Out.Speed >= 5. && !HasInput;
        Out.Starting = !Falling && HasInput && StartRemaining > 0. && !Out.Pivoting;
        const double TargetLean = Falling ? 0. : std::clamp(AY / 1800. * 8., -8., 8.);
        Lean += (TargetLean - Lean) * -std::expm1(-Delta / .1);
        Out.LeanDegrees = Lean;
        return Out;
    }
    void Reset() { Moving = false; StartRemaining = Lean = 0.; }
private:
    bool Moving = false;
    double StartRemaining = 0., Lean = 0.;
};
}
