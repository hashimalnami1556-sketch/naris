#pragma once

#include "CoreMinimal.h"
#include "GameFramework/HUD.h"
#include "NarisHUD.generated.h"

class ANarisHeroCharacter;
class ANarisPlayerController;
class UNarisRuntimeSubsystem;

UCLASS(Blueprintable)
class NARIS_W04_API ANarisHUD : public AHUD
{
    GENERATED_BODY()

public:
    virtual void DrawHUD() override;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Map", meta=(ClampMin="100.0"))
    float LocalMapRadius = 5000.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Map")
    bool bShowLocalMap = true;

private:
    void DrawLocalMap(float X, float Y, float Size, float Scale, UNarisRuntimeSubsystem* Runtime);
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
    void DrawPlayerVitals(ANarisHeroCharacter* Hero, float Scale, float Safe);
    void DrawBreath(ANarisHeroCharacter* Hero, float Scale);
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
    void DrawPanel(
        float X,
        float Y,
        float Width,
        float Height,
        const FLinearColor& Color
    );
};
