#pragma once
#include <cmath>

namespace NarisMapProjection
{
    // North is world +X; east is world +Y. Output uses screen-down Y.
    inline bool Project(double X, double Y, double CenterX, double CenterY,
        double Radius, double& U, double& V)
    {
        U = V = 0.5;
        if (!std::isfinite(X) || !std::isfinite(Y) || !std::isfinite(CenterX)
            || !std::isfinite(CenterY) || !std::isfinite(Radius) || Radius <= 0.0)
            return false;
        U = 0.5 + (Y - CenterY) / (2.0 * Radius);
        V = 0.5 - (X - CenterX) / (2.0 * Radius);
        return U >= 0.0 && U <= 1.0 && V >= 0.0 && V <= 1.0;
    }
}
