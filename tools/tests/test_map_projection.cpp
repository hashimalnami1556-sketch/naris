#include "NarisMapProjection.h"
#include <cassert>
#include <limits>
int main()
{
    double U, V;
    using NarisMapProjection::Project;
    assert(Project(100, 200, 100, 200, 1000, U, V) && U == 0.5 && V == 0.5);
    assert(Project(1100, 200, 100, 200, 1000, U, V) && U == 0.5 && V == 0.0);
    assert(Project(100, 1200, 100, 200, 1000, U, V) && U == 1.0 && V == 0.5);
    assert(Project(-900, -800, 100, 200, 1000, U, V) && U == 0.0 && V == 1.0);
    assert(!Project(1101, 200, 100, 200, 1000, U, V));
    assert(!Project(0, 0, 0, 0, 0, U, V));
    assert(!Project(0, 0, 0, 0, -1, U, V));
    assert(!Project(std::numeric_limits<double>::quiet_NaN(), 0, 0, 0, 1000, U, V));
    // A stationary landmark moves left when the player moves east.
    assert(Project(100, 200, 100, 700, 1000, U, V) && U == 0.25 && V == 0.5);
    // Translation of the entire world must leave the projection unchanged.
    assert(Project(10100, 20200, 10100, 20700, 1000, U, V) && U == 0.25 && V == 0.5);
}
