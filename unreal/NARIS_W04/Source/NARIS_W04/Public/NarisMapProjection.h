#pragma once

#include "CoreMinimal.h"

// Fixed world axes: +X is up, +Y is right. A square keeps distances isotropic.
struct FNarisMapProjection
{
    static FVector2D Project(const FVector& World, const FVector& Origin,
        const FVector2D& Center, float HalfSize, float WorldRadius)
    {
        const float PixelsPerUnit = HalfSize / FMath::Max(WorldRadius, 1.f);
        return Center + FVector2D(World.Y - Origin.Y, Origin.X - World.X) * PixelsPerUnit;
    }

    static bool IsVisible(const FVector2D& Point, const FVector2D& Center,
        float HalfSize, float Margin)
    {
        const float Extent = FMath::Max(0.f, HalfSize - Margin);
        return FMath::Abs(Point.X - Center.X) <= Extent
            && FMath::Abs(Point.Y - Center.Y) <= Extent;
    }
};
