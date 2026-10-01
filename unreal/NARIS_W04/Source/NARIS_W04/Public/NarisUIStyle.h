#pragma once

#include "CoreMinimal.h"

class NARIS_W04_API FNarisUIStyle
{
public:
    static float GetViewportScale(float Width, float Height);
    static float GetSafeMargin(float Width, float Height);
    static float SafeRatio(float Value, float MaxValue);

    static FLinearColor Canvas();
    static FLinearColor Surface();
    static FLinearColor SurfaceElevated();
    static FLinearColor Bone();
    static FLinearColor Muted();
    static FLinearColor Gold();
    static FLinearColor Cyan();
    static FLinearColor Violet();
    static FLinearColor Danger();
    static FLinearColor Ember();
    static FLinearColor Selection();
};
