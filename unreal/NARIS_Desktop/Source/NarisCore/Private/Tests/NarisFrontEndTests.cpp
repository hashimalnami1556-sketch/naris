#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "NarisGameModeBase.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FNarisFrontEndStateTest,
 "NARIS.FrontEnd.StartsInMenuAndCanStart",
 EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FNarisFrontEndStateTest::RunTest(const FString& Parameters)
{
 ANarisGameModeBase* Mode = NewObject<ANarisGameModeBase>();
 TestFalse(TEXT("Fresh game mode must begin at the front-end"), Mode->IsGameStarted());
 Mode->StartGame();
 TestTrue(TEXT("StartGame must transition into gameplay"), Mode->IsGameStarted());
 return true;
}
#endif
