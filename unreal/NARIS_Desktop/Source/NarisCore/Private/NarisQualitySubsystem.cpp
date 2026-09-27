#include "NarisQualitySubsystem.h"
#include "GameFramework/GameUserSettings.h"

void UNarisQualitySubsystem::ApplyRecommendedQuality()
{
    if (UGameUserSettings* Settings = GEngine ? GEngine->GetGameUserSettings() : nullptr)
    {
        Settings->RunHardwareBenchmark();
        Settings->ApplyHardwareBenchmarkResults();
        Settings->ApplySettings(false);
    }
}
