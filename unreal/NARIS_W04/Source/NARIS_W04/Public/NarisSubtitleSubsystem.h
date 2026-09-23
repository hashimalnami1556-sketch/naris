#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "NarisSubtitleSubsystem.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(
    FNarisSubtitleShown,
    FText,
    Speaker,
    FText,
    Line
);

DECLARE_DYNAMIC_MULTICAST_DELEGATE(FNarisSubtitleCleared);

UCLASS()
class NARIS_W04_API UNarisSubtitleSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category="NARIS|Subtitle")
    bool ShowSubtitle(
        const FText& Speaker,
        const FText& Line,
        float DurationSeconds = 4.f
    );

    UFUNCTION(BlueprintCallable, Category="NARIS|Subtitle")
    void ClearSubtitle();

    UFUNCTION(BlueprintPure, Category="NARIS|Subtitle")
    bool IsSubtitleActive() const;

    UFUNCTION(BlueprintPure, Category="NARIS|Subtitle")
    FText GetSpeaker() const { return ActiveSpeaker; }

    UFUNCTION(BlueprintPure, Category="NARIS|Subtitle")
    FText GetLine() const { return ActiveLine; }

    UFUNCTION(BlueprintPure, Category="NARIS|Subtitle")
    float GetRemainingSeconds() const;

    UPROPERTY(BlueprintAssignable, Category="NARIS|Subtitle")
    FNarisSubtitleShown OnSubtitleShown;

    UPROPERTY(BlueprintAssignable, Category="NARIS|Subtitle")
    FNarisSubtitleCleared OnSubtitleCleared;

private:
    UPROPERTY(Transient)
    FText ActiveSpeaker;

    UPROPERTY(Transient)
    FText ActiveLine;

    double ExpiresAtGameTime = -1.0;
};
