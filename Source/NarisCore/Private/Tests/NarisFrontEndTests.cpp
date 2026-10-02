#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "NarisGameModeBase.h"
#include "NarisHUD.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FNarisDismissMenuOnResumeTest,
 "NARIS.FrontEnd.DismissesMenuWhenGameplayResumes",
 EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FNarisDismissMenuOnResumeTest::RunTest(const FString& Parameters)
{
 TestTrue(TEXT("Resumed gameplay dismisses any remaining menu"), ANarisHUD::ShouldDismissFrontEnd(true,false));
 TestFalse(TEXT("Pause menu stays visible during paused gameplay"), ANarisHUD::ShouldDismissFrontEnd(true,true));
 TestFalse(TEXT("Front-end stays visible before first play"), ANarisHUD::ShouldDismissFrontEnd(false,true));
 return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FNarisFrontEndStateTest,
 "NARIS.FrontEnd.StartsInFrontEndThenTransitionsToGameplay",
 EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FNarisFrontEndStateTest::RunTest(const FString& Parameters)
{
 ANarisGameModeBase* Mode = NewObject<ANarisGameModeBase>();
 TestFalse(TEXT("Fresh game mode must begin in the front-end state"), Mode->IsGameStarted());
 Mode->StartGame();
 TestTrue(TEXT("StartGame must transition into gameplay"), Mode->IsGameStarted());
 return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FNarisDirectPlayFlagTest,
 "NARIS.FrontEnd.DirectPlayFlagsBypassFrontEnd",
 EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FNarisDirectPlayFlagTest::RunTest(const FString& Parameters)
{
 TestFalse(TEXT("Normal launch uses the front end"), ANarisGameModeBase::ShouldStartDirectly(TEXT("")));
 TestTrue(TEXT("Direct play bypasses the front end"), ANarisGameModeBase::ShouldStartDirectly(TEXT("-NarisDirectPlay")));
 TestTrue(TEXT("Quest smoke bypasses the front end"), ANarisGameModeBase::ShouldStartDirectly(TEXT("-NarisQuestSmoke")));
 return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FNarisWorldRoutingTest,
 "NARIS.WorldRouting.JeddahSkipsAshenGateInjection",
 EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FNarisWorldRoutingTest::RunTest(const FString& Parameters)
{
 TestFalse(TEXT("Ashen Forest keeps Ashen Gate gameplay"), ANarisGameModeBase::ShouldSkipAshenGateForWorld(TEXT("/Game/World/Maps/L_AshenForest_EntryRestored_V2")));
 TestTrue(TEXT("GIS Jeddah must not inject Ashen Gate gameplay"), ANarisGameModeBase::ShouldSkipAshenGateForWorld(TEXT("/Game/NARIS_GIS/Jeddah/Maps/L_Jeddah_GIS_V2")));
 TestTrue(TEXT("Legacy coastal concept remains isolated"), ANarisGameModeBase::ShouldSkipAshenGateForWorld(TEXT("/Game/NARIS_AI_Stage/Maps/L_Jeddah_RedSea_V1")));
 return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FNarisBenchmarkEnemyCountTest,
 "NARIS.Benchmark.ParsesEnemyCount",
 EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FNarisBenchmarkEnemyCountTest::RunTest(const FString& Parameters)
{
 TestEqual(TEXT("Benchmark count defaults to zero"), ANarisGameModeBase::ParseBenchmarkEnemyCount(TEXT("")), 0);
 TestEqual(TEXT("Benchmark accepts 20 enemies"), ANarisGameModeBase::ParseBenchmarkEnemyCount(TEXT("-NarisBenchmarkEnemies=20")), 20);
 TestEqual(TEXT("Benchmark clamps excessive counts"), ANarisGameModeBase::ParseBenchmarkEnemyCount(TEXT("-NarisBenchmarkEnemies=999")), 64);
 return true;
}
#endif

