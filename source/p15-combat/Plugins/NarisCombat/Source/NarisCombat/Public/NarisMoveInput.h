#pragma once
#include <algorithm>
#include <cmath>

namespace NarisP15
{
struct MoveInput
{
    double X = 0., Y = 0.;
};

// مرشح إدخال فقط: السرعة والتصادم والتنبؤ الشبكي تبقى لدى CharacterMovement.
class MoveInputFilter
{
public:
    static bool Valid(double DeadZone, double Exponent, double ResponseSeconds)
    {
        return std::isfinite(DeadZone) && DeadZone >= 0. && DeadZone < 1.
            && std::isfinite(Exponent) && Exponent >= 1. && Exponent <= 4.
            && std::isfinite(ResponseSeconds) && ResponseSeconds >= 0. && ResponseSeconds <= .2;
    }

    MoveInput Step(MoveInput Raw, double Delta, double DeadZone, double Exponent, double ResponseSeconds)
    {
        if (!Valid(DeadZone, Exponent, ResponseSeconds) || !std::isfinite(Raw.X)
            || !std::isfinite(Raw.Y)) { Reset(); return Current; }
        if (!std::isfinite(Delta) || Delta <= 0.) return Current;
        // قص كل محور قبل حساب الطول يمنع الفيضان ويحافظ على حد السرعة القطري.
        Raw.X = std::clamp(Raw.X, -1., 1.);
        Raw.Y = std::clamp(Raw.Y, -1., 1.);
        const double Length = std::hypot(Raw.X, Raw.Y);
        MoveInput Target;
        if (Length > DeadZone)
        {
            const double Magnitude = std::pow((std::min(Length, 1.) - DeadZone) / (1. - DeadZone), Exponent);
            Target = {Raw.X / Length * Magnitude, Raw.Y / Length * Magnitude};
        }
        // تحرير العصا يترك الفرملة للمحرك، دون ذيل إدخال يزيد مسافة التوقف.
        if (Length <= DeadZone || ResponseSeconds == 0.) Current = Target;
        else
        {
            const double Alpha = -std::expm1(-Delta / ResponseSeconds);
            Current.X += (Target.X - Current.X) * Alpha;
            Current.Y += (Target.Y - Current.Y) * Alpha;
        }
        return Current;
    }

    void Reset() { Current = {}; }
private:
    MoveInput Current;
};
}
