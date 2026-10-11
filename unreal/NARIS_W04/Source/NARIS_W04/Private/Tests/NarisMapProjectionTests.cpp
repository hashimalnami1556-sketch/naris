#include "Misc/AutomationTest.h"
#include "NarisMapProjection.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FNarisMapProjectionTest,
    "NARIS.UI.Map.Projection",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FNarisMapProjectionTest::RunTest(const FString& Parameters)
{
    const FVector Origin(1200., -800., 450.);
    const FVector2D Center(300., 400.);
    TestTrue(TEXT("Player centered"), FNarisMapProjection::Project(Origin, Origin, Center, 100.f, 10000.f).Equals(Center));
    TestTrue(TEXT("Positive X points up"), FNarisMapProjection::Project(Origin + FVector(10000., 0., 0.), Origin, Center, 100.f, 10000.f).Equals(FVector2D(300., 300.)));
    TestTrue(TEXT("Positive Y points right"), FNarisMapProjection::Project(Origin + FVector(0., 10000., 0.), Origin, Center, 100.f, 10000.f).Equals(FVector2D(400., 400.)));
    TestTrue(TEXT("Altitude ignored"), FNarisMapProjection::Project(Origin + FVector(0., 0., 9000.), Origin, Center, 100.f, 10000.f).Equals(Center));
    TestFalse(TEXT("Marker crossing border hidden"), FNarisMapProjection::IsVisible(FVector2D(398., 400.), Center, 100.f, 5.f));
    TestTrue(TEXT("Marker wholly inside visible"), FNarisMapProjection::IsVisible(FVector2D(395., 400.), Center, 100.f, 5.f));
    const FVector2D InvalidRadius = FNarisMapProjection::Project(Origin + FVector(1., 1., 0.), Origin, Center, 100.f, 0.f);
    TestFalse(TEXT("Zero radius produces finite coordinates"), InvalidRadius.ContainsNaN());
    return true;
}
#endif
