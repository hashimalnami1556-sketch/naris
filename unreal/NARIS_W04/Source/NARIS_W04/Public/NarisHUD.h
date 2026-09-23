#pragma once

#include "CoreMinimal.h"
#include "GameFramework/HUD.h"
#include "NarisHUD.generated.h"

UCLASS(Blueprintable)
class NARIS_W04_API ANarisHUD : public AHUD
{
    GENERATED_BODY()

public:
    virtual void DrawHUD() override;

private:
    void DrawPauseMenu();
    void DrawSubtitle();
    void DrawBar(
        const FString& Label,
        float Value,
        float MaxValue,
        float X,
        float Y,
        const FLinearColor& FillColor
    );
};
