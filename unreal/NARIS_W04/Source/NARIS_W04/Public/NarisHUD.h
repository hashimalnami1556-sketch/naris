#pragma once

#include "CoreMinimal.h"
#include "GameFramework/HUD.h"
#include "NarisHUD.generated.h"

class ANarisHeroCharacter;
class ANarisPlayerController;
class UNarisRuntimeSubsystem;
class UNarisRewardDirectorSubsystem;

UCLASS(Blueprintable)
class NARIS_W04_API ANarisHUD : public AHUD
{
    GENERATED_BODY()

public:
    virtual void DrawHUD() override;

private:
    void DrawPauseMenu();
    void DrawContentPage(
        ANarisPlayerController* Controller,
        UNarisRuntimeSubsystem* Runtime,
        float X,
        float Y,
        float Width,
        float Height,
        float Scale
    );
    void DrawSubtitle();
    void DrawRewardToast(float Scale, float Safe);
    void DrawPlayerVitals(ANarisHeroCharacter* Hero, float Scale, float Safe);
    void DrawObjectiveCard(UNarisRuntimeSubsystem* Runtime, float Scale, float Safe);
    void DrawInteractionPrompt(ANarisHeroCharacter* Hero, float Scale);
    void DrawBossHUD(float Scale, float Safe);
    void DrawBar(
        const FString& Label,
        float Value,
        float MaxValue,
        float X,
        float Y,
        float Width,
        float Height,
        const FLinearColor& FillColor,
        float Scale
    );
    FString ActiveRewardEventId;
    float ActiveRewardStartedAt = -1.f;

    void DrawPanel(
        float X,
        float Y,
        float Width,
        float Height,
        const FLinearColor& Color
    );
};
