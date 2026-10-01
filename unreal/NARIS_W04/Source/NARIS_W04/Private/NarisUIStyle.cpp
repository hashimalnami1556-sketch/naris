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
    return 40.f * GetViewportScale(Width, Height);
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
    return FLinearColor(0.025f, 0.032f, 0.043f, 0.94f);
}

FLinearColor FNarisUIStyle::Surface()
{
    return FLinearColor(0.055f, 0.071f, 0.090f, 0.96f);
}

FLinearColor FNarisUIStyle::SurfaceElevated()
{
    return FLinearColor(0.082f, 0.102f, 0.125f, 0.97f);
}

FLinearColor FNarisUIStyle::Bone()
{
    return FLinearColor(0.906f, 0.878f, 0.831f, 1.f);
}

FLinearColor FNarisUIStyle::Muted()
{
    return FLinearColor(0.64f, 0.66f, 0.68f, 1.f);
}

FLinearColor FNarisUIStyle::Gold()
{
    return FLinearColor(0.776f, 0.631f, 0.357f, 1.f);
}

FLinearColor FNarisUIStyle::Cyan()
{
    return FLinearColor(0.388f, 0.839f, 0.812f, 1.f);
}

FLinearColor FNarisUIStyle::Violet()
{
    return FLinearColor(0.541f, 0.357f, 0.718f, 1.f);
}

FLinearColor FNarisUIStyle::Danger()
{
    return FLinearColor(0.788f, 0.298f, 0.271f, 1.f);
}

FLinearColor FNarisUIStyle::Ember()
{
    return FLinearColor(0.90f, 0.31f, 0.10f, 1.f);
}

FLinearColor FNarisUIStyle::Selection()
{
    return FLinearColor(0.19f, 0.15f, 0.07f, 0.92f);
}
