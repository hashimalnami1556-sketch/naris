#include "NarisGroundApproach.h"
#include <cassert>
#include <cmath>
#include <limits>

int main()
{
    using NarisGroundApproach::InputScale;
    assert(InputScale(0.0, 260.0, 500.0) == 0.0);
    assert(InputScale(259.0, 260.0, 500.0) == 0.0);
    assert(InputScale(260.0, 260.0, 500.0) == 0.0);
    assert(InputScale(260.001, 260.0, 500.0) < 0.00001);
    assert(std::abs(InputScale(510.0, 260.0, 500.0) - 0.5) < 1e-9);
    assert(InputScale(760.0, 260.0, 500.0) == 1.0);
    assert(InputScale(10000.0, 260.0, 500.0) == 1.0);
    assert(InputScale(250.0, -1.0, 500.0) == 0.5);
    assert(InputScale(261.0, 260.0, 0.0) == 1.0);
    assert(InputScale(std::numeric_limits<double>::quiet_NaN(), 260.0, 500.0) == 0.0);
    assert(InputScale(500.0, std::numeric_limits<double>::infinity(), 500.0) == 0.0);
    for (int i = 1; i <= 1000; ++i)
        assert(InputScale(260.0 + i, 260.0, 500.0) >= InputScale(259.0 + i, 260.0, 500.0));
}
