#include "NarisSubtitleSubsystem.h"

#include "Engine/World.h"

bool UNarisSubtitleSubsystem::ShowSubtitle(
    const FText& Speaker,
    const FText& Line,
    float DurationSeconds
)
{
    if (Line.IsEmpty() || DurationSeconds <= 0.f)
    {
        return false;
    }

    UWorld* World = GetWorld();
    if (!World)
    {
        return false;
    }

    ActiveSpeaker = Speaker;
    ActiveLine = Line;
    ExpiresAtGameTime =
        static_cast<double>(World->GetTimeSeconds())
        + static_cast<double>(FMath::Max(DurationSeconds, 0.1f));

    OnSubtitleShown.Broadcast(ActiveSpeaker, ActiveLine);
    return true;
}

void UNarisSubtitleSubsystem::ClearSubtitle()
{
    const bool bHadSubtitle = !ActiveLine.IsEmpty();

    ActiveSpeaker = FText::GetEmpty();
    ActiveLine = FText::GetEmpty();
    ExpiresAtGameTime = -1.0;

    if (bHadSubtitle)
    {
        OnSubtitleCleared.Broadcast();
    }
}

bool UNarisSubtitleSubsystem::IsSubtitleActive() const
{
    const UWorld* World = GetWorld();
    return World
        && !ActiveLine.IsEmpty()
        && ExpiresAtGameTime > static_cast<double>(World->GetTimeSeconds());
}

float UNarisSubtitleSubsystem::GetRemainingSeconds() const
{
    const UWorld* World = GetWorld();
    if (!World || !IsSubtitleActive())
    {
        return 0.f;
    }

    return FMath::Max(
        0.f,
        static_cast<float>(
            ExpiresAtGameTime
            - static_cast<double>(World->GetTimeSeconds())
        )
    );
}
