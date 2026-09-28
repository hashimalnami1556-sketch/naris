#pragma once
#include "CoreMinimal.h"
#include "Subsystems/EngineSubsystem.h"
#include "NarisReleaseGateSubsystem.generated.h"
UCLASS() class NARISCORE_API UNarisReleaseGateSubsystem: public UEngineSubsystem { GENERATED_BODY() public: UFUNCTION(BlueprintCallable) bool RunPreflight(TArray<FString>& Failures) const; };
