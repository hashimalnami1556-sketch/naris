#include "Misc/AutomationTest.h"
#include "NarisUIStyle.h"

#if WITH_DEV_AUTOMATION_TESTS

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FNarisUILayoutScaleTest,
    "NARIS.UI.Layout.Scale",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter
)

bool FNarisUILayoutScaleTest::RunTest(const FString& Parameters)
{
    TestEqual(TEXT("1080p scale"), FNarisUIStyle::GetViewportScale(1920.f, 1080.f), 1.0f);
    TestTrue(TEXT("720p scale is clamped for readability"), FNarisUIStyle::GetViewportScale(1280.f, 720.f) >= 0.75f);
    TestTrue(TEXT("4K scale is capped"), FNarisUIStyle::GetViewportScale(3840.f, 2160.f) <= 1.60f);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FNarisUILayoutSafeMarginTest,
    "NARIS.UI.Layout.SafeMargin",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter
)

bool FNarisUILayoutSafeMarginTest::RunTest(const FString& Parameters)
{
    const float Margin1080 = FNarisUIStyle::GetSafeMargin(1920.f, 1080.f);
    const float Margin4K = FNarisUIStyle::GetSafeMargin(3840.f, 2160.f);

    TestTrue(TEXT("Safe margin is positive"), Margin1080 > 0.f);
    TestTrue(TEXT("Safe margin scales up"), Margin4K > Margin1080);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FNarisUILayoutRatioTest,
    "NARIS.UI.Layout.Ratio",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter
)

bool FNarisUILayoutRatioTest::RunTest(const FString& Parameters)
{
    TestEqual(TEXT("Half ratio"), FNarisUIStyle::SafeRatio(50.f, 100.f), 0.5f);
    TestEqual(TEXT("Zero max produces zero"), FNarisUIStyle::SafeRatio(10.f, 0.f), 0.0f);
    TestEqual(TEXT("Ratio clamps high"), FNarisUIStyle::SafeRatio(200.f, 100.f), 1.0f);
    TestEqual(TEXT("Ratio clamps low"), FNarisUIStyle::SafeRatio(-10.f, 100.f), 0.0f);
    return true;
}

#endif
