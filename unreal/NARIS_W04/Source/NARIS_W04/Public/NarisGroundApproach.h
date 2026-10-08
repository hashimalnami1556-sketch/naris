#pragma once

#include <cmath>

// Engine-independent calculation shared by runtime and the portable regression test.
namespace NarisGroundApproach
{
    inline double InputScale(double PlanarDistance, double AcceptanceRadius, double SlowdownDistance)
    {
        if (!std::isfinite(PlanarDistance) || !std::isfinite(AcceptanceRadius)
            || !std::isfinite(SlowdownDistance))
        {
            return 0.0;
        }
        const double Radius = AcceptanceRadius > 0.0 ? AcceptanceRadius : 0.0;
        const double Remaining = PlanarDistance - Radius;
        if (Remaining <= 0.0)
        {
            return 0.0;
        }
        const double Ramp = SlowdownDistance > 1.0 ? SlowdownDistance : 1.0;
        return Remaining >= Ramp ? 1.0 : Remaining / Ramp;
    }
}
