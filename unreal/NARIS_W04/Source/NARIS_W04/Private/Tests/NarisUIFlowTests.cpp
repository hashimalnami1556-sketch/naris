#include "Misc/AutomationTest.h"
#include "UI/NarisUIFlow.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FNarisUIFlowBootTest,
    "NARIS.UI.Flow.BootsIntoMainMenu",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FNarisUIFlowBootTest::RunTest(const FString&)
{
    FNarisUIFlow Flow;
    TestEqual(TEXT("Initial screen"), Flow.GetCurrentScreen(), ENarisUIScreen::MainMenu);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FNarisUIFlowGameplayTest,
    "NARIS.UI.Flow.GameplayAndPauseRoundTrip",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FNarisUIFlowGameplayTest::RunTest(const FString&)
{
    FNarisUIFlow Flow;
    Flow.OpenGameplay();
    TestEqual(TEXT("Gameplay screen"), Flow.GetCurrentScreen(), ENarisUIScreen::GameplayHUD);
    Flow.TogglePause();
    TestEqual(TEXT("Pause screen"), Flow.GetCurrentScreen(), ENarisUIScreen::Pause);
    Flow.TogglePause();
    TestEqual(TEXT("Resume gameplay"), Flow.GetCurrentScreen(), ENarisUIScreen::GameplayHUD);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FNarisUIFlowMenuTest,
    "NARIS.UI.Flow.OpensCoreMenusFromGameplay",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FNarisUIFlowMenuTest::RunTest(const FString&)
{
    FNarisUIFlow Flow;
    Flow.OpenGameplay();

    Flow.OpenScreen(ENarisUIScreen::Inventory);
    TestEqual(TEXT("Inventory"), Flow.GetCurrentScreen(), ENarisUIScreen::Inventory);

    Flow.OpenScreen(ENarisUIScreen::WorldMap);
    TestEqual(TEXT("World map"), Flow.GetCurrentScreen(), ENarisUIScreen::WorldMap);

    Flow.OpenScreen(ENarisUIScreen::Journal);
    TestEqual(TEXT("Journal"), Flow.GetCurrentScreen(), ENarisUIScreen::Journal);

    Flow.OpenScreen(ENarisUIScreen::Skills);
    TestEqual(TEXT("Skills"), Flow.GetCurrentScreen(), ENarisUIScreen::Skills);

    Flow.OpenScreen(ENarisUIScreen::Settings);
    TestEqual(TEXT("Settings"), Flow.GetCurrentScreen(), ENarisUIScreen::Settings);
    return true;
}
