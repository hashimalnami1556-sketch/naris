#include "UI/NarisUIFlow.h"

FNarisUIFlow::FNarisUIFlow()
    : CurrentScreen(ENarisUIScreen::MainMenu)
    , ScreenBeforePause(ENarisUIScreen::GameplayHUD)
{
}

void FNarisUIFlow::OpenGameplay()
{
    CurrentScreen = ENarisUIScreen::GameplayHUD;
}

void FNarisUIFlow::OpenScreen(ENarisUIScreen Screen)
{
    CurrentScreen = Screen;
}

void FNarisUIFlow::TogglePause()
{
    if (CurrentScreen == ENarisUIScreen::Pause)
    {
        CurrentScreen = ScreenBeforePause;
        return;
    }

    ScreenBeforePause = CurrentScreen;
    CurrentScreen = ENarisUIScreen::Pause;
}
