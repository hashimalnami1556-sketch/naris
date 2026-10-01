#pragma once

#include "CoreMinimal.h"
#include "NarisUIFlow.generated.h"

UENUM(BlueprintType)
enum class ENarisUIScreen : uint8
{
    MainMenu,
    NewGame,
    Cinematic,
    GameplayHUD,
    WorldMap,
    Inventory,
    Journal,
    Skills,
    Crafting,
    Shop,
    Pause,
    Settings,
    Controls,
    Accessibility,
    Death,
    Loading,
    DemoEnd,
    Credits
};

class NARIS_W04_API FNarisUIFlow
{
public:
    FNarisUIFlow();

    ENarisUIScreen GetCurrentScreen() const { return CurrentScreen; }
    void OpenGameplay();
    void OpenScreen(ENarisUIScreen Screen);
    void TogglePause();

private:
    ENarisUIScreen CurrentScreen;
    ENarisUIScreen ScreenBeforePause;
};
