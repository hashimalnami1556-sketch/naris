#include "NarisUIStyle.h"

float FNarisUIStyle::GetViewportScale(float Width, float Height)
{
    if (Width <= 0.f || Height <= 0.f)
    {
        return 1.f;
    }

    const float ScaleX = Width / 1920.f;
    const float ScaleY = Height / 1080.f;
    return FMath::Clamp(FMath::Min(ScaleX, ScaleY), 0.75f, 1.60f);
}

float FNarisUIStyle::GetSafeMargin(float Width, float Height)
{
    return 32.f * GetViewportScale(Width, Height);
}

float FNarisUIStyle::SafeRatio(float Value, float MaxValue)
{
    if (MaxValue <= KINDA_SMALL_NUMBER)
    {
        return 0.f;
    }

    return FMath::Clamp(Value / MaxValue, 0.f, 1.f);
}

FLinearColor FNarisUIStyle::Canvas()
{
    return FLinearColor(0.006f, 0.007f, 0.008f, 0.96f);
}

FLinearColor FNarisUIStyle::Surface()
{
    return FLinearColor(0.028f, 0.024f, 0.023f, 0.96f);
}

FLinearColor FNarisUIStyle::SurfaceElevated()
{
    return FLinearColor(0.060f, 0.049f, 0.043f, 0.98f);
}

FLinearColor FNarisUIStyle::Bone()
{
    return FLinearColor(0.940f, 0.915f, 0.865f, 1.f);
}

FLinearColor FNarisUIStyle::Muted()
{
    return FLinearColor(0.58f, 0.54f, 0.50f, 1.f);
}

FLinearColor FNarisUIStyle::Gold()
{
    return FLinearColor(0.72f, 0.46f, 0.18f, 1.f);
}

FLinearColor FNarisUIStyle::Cyan()
{
    return FLinearColor(0.42f, 0.66f, 0.70f, 1.f);
}

FLinearColor FNarisUIStyle::Violet()
{
    return FLinearColor(0.39f, 0.28f, 0.52f, 1.f);
}

FLinearColor FNarisUIStyle::Danger()
{
    return FLinearColor(0.78f, 0.18f, 0.12f, 1.f);
}

FLinearColor FNarisUIStyle::Ember()
{
    return FLinearColor(0.93f, 0.28f, 0.06f, 1.f);
}

FLinearColor FNarisUIStyle::Selection()
{
    return FLinearColor(0.25f, 0.115f, 0.035f, 0.94f);
}
