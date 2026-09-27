#include "NarisReleaseGateSubsystem.h"
#include "Misc/Paths.h"
#include "HAL/FileManager.h"

bool UNarisReleaseGateSubsystem::RunPreflight(TArray<FString>& Failures) const
{
    Failures.Reset();
    const FString ContentDir = FPaths::ProjectContentDir();
    if (!IFileManager::Get().DirectoryExists(*ContentDir))
    {
        Failures.Add(TEXT("Project Content directory is missing."));
    }
    return Failures.Num() == 0;
}
